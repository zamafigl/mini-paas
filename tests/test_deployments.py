from datetime import datetime
from types import SimpleNamespace

import app.api.routes.apps as apps_routes
from app.db.models.app import App
from app.db.models.deployment import Deployment


def create_app(client, name: str = "demo-app") -> int:
    response = client.post(
        "/apps",
        json={
            "name": name,
            "image": "nginx:latest",
            "internal_port": 80,
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def mark_app_as_deployed(db_session, app_id: int) -> None:
    app = db_session.query(App).filter(App.id == app_id).first()
    app.container_id = "container-123"
    app.assigned_port = 5001
    app.status = "running"
    db_session.commit()


def test_deploy_app_marks_status_and_enqueues_job(client, monkeypatch):
    app_id = create_app(client)

    captured = {}

    class FakeQueue:
        def __init__(self, *args, **kwargs):
            pass

        def enqueue(self, func, queued_app_id, job_timeout=None):
            captured["func_name"] = func.__name__
            captured["app_id"] = queued_app_id
            captured["job_timeout"] = job_timeout

    monkeypatch.setattr(
        apps_routes.redis.Redis,
        "from_url",
        staticmethod(lambda url: object()),
    )
    monkeypatch.setattr(apps_routes, "Queue", FakeQueue)

    response = client.post(f"/apps/{app_id}/deploy")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "deploying"
    assert captured["func_name"] == "deploy_app_job"
    assert captured["app_id"] == app_id
    assert captured["job_timeout"] == 300


def test_deploy_app_rejects_second_in_progress_request(client, monkeypatch):
    app_id = create_app(client)

    class FakeQueue:
        def __init__(self, *args, **kwargs):
            pass

        def enqueue(self, *args, **kwargs):
            return None

    monkeypatch.setattr(
        apps_routes.redis.Redis,
        "from_url",
        staticmethod(lambda url: object()),
    )
    monkeypatch.setattr(apps_routes, "Queue", FakeQueue)

    first = client.post(f"/apps/{app_id}/deploy")
    second = client.post(f"/apps/{app_id}/deploy")

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["detail"] == "App deployment is already in progress"


def test_get_logs_for_not_deployed_app_returns_400(client):
    app_id = create_app(client)

    response = client.get(f"/apps/{app_id}/logs")
    assert response.status_code == 400
    assert response.json()["detail"] == "App is not deployed"


def test_get_logs_returns_container_logs(client, db_session, monkeypatch):
    app_id = create_app(client)
    mark_app_as_deployed(db_session, app_id)

    fake_docker = SimpleNamespace(get_logs=lambda container_id: "hello from container")
    monkeypatch.setattr(apps_routes, "DockerService", lambda: fake_docker)

    response = client.get(f"/apps/{app_id}/logs")
    assert response.status_code == 200
    assert response.json()["logs"] == "hello from container"


def test_stop_app_updates_status(client, db_session, monkeypatch):
    app_id = create_app(client)
    mark_app_as_deployed(db_session, app_id)

    fake_docker = SimpleNamespace(stop_container=lambda container_id: None)
    monkeypatch.setattr(apps_routes, "DockerService", lambda: fake_docker)

    response = client.post(f"/apps/{app_id}/stop")
    assert response.status_code == 200
    assert response.json()["status"] == "stopped"


def test_start_app_updates_status(client, db_session, monkeypatch):
    app_id = create_app(client)
    mark_app_as_deployed(db_session, app_id)

    fake_docker = SimpleNamespace(start_container=lambda container_id: None)
    monkeypatch.setattr(apps_routes, "DockerService", lambda: fake_docker)

    response = client.post(f"/apps/{app_id}/start")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_restart_app_updates_status(client, db_session, monkeypatch):
    app_id = create_app(client)
    mark_app_as_deployed(db_session, app_id)

    fake_docker = SimpleNamespace(restart_container=lambda container_id: None)
    monkeypatch.setattr(apps_routes, "DockerService", lambda: fake_docker)

    response = client.post(f"/apps/{app_id}/restart")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_remove_app_container_resets_runtime_fields(client, db_session, monkeypatch):
    app_id = create_app(client)
    mark_app_as_deployed(db_session, app_id)

    fake_docker = SimpleNamespace(
        remove_container=lambda container_id: None,
        remove_nginx_route=lambda app_id: None,
        reload_nginx=lambda: None,
    )
    monkeypatch.setattr(apps_routes, "DockerService", lambda: fake_docker)

    response = client.post(f"/apps/{app_id}/remove")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "created"
    assert data["container_id"] is None
    assert data["assigned_port"] is None


def test_list_deployments_returns_latest_first(client, db_session):
    app_id = create_app(client)

    db_session.add_all(
        [
            Deployment(
                app_id=app_id,
                status="failed",
                started_at=datetime.utcnow(),
                finished_at=datetime.utcnow(),
                error_message="boom",
            ),
            Deployment(
                app_id=app_id,
                status="success",
                started_at=datetime.utcnow(),
                finished_at=datetime.utcnow(),
                error_message=None,
            ),
        ]
    )
    db_session.commit()

    response = client.get(f"/apps/{app_id}/deployments")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["status"] == "success"
    assert data[1]["status"] == "failed"


def test_list_deployments_returns_404_for_missing_app(client):
    response = client.get("/apps/999/deployments")
    assert response.status_code == 404
    assert response.json()["detail"] == "App not found"
