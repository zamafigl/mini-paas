from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.app import App
from app.db.models.deployment import Deployment
from app.db.session import SessionLocal
from app.services.docker_service import DockerService


def deploy_app_job(app_id: int) -> None:
    db: Session = SessionLocal()
    deployment: Deployment | None = None
    app: App | None = None
    docker_service: DockerService | None = None
    container_id: str | None = None
    route_written = False

    try:
        app = db.query(App).filter(App.id == app_id).first()
        if not app:
            return

        deployment = Deployment(
            app_id=app.id,
            status="running",
            started_at=datetime.utcnow(),
        )
        db.add(deployment)
        db.commit()
        db.refresh(deployment)

        if app.container_id:
            deployment.status = "failed"
            deployment.finished_at = datetime.utcnow()
            deployment.error_message = "App is already deployed"
            db.commit()
            return

        docker_service = DockerService()
        assigned_port = docker_service.get_free_port()
        safe_container_name = f"mini-paas-app-{app.id}"

        container = docker_service.run_container(
            name=safe_container_name,
            image=app.image,
            internal_port=app.internal_port,
            external_port=assigned_port,
        )
        container_id = container.id

        docker_service.write_nginx_route(
            app_id=app.id,
            container_name=safe_container_name,
            internal_port=app.internal_port,
        )
        route_written = True
        docker_service.reload_nginx()

        app.assigned_port = assigned_port
        app.container_id = container.id
        app.status = "running"

        deployment.status = "success"
        deployment.finished_at = datetime.utcnow()

        db.commit()
        db.refresh(app)

    except Exception as exc:
        if docker_service and container_id:
            try:
                docker_service.remove_container(container_id)
            except Exception:
                pass

        if docker_service and route_written and app:
            try:
                docker_service.remove_nginx_route(app.id)
                docker_service.reload_nginx()
            except Exception:
                pass

        if deployment:
            deployment.status = "failed"
            deployment.finished_at = datetime.utcnow()
            deployment.error_message = str(exc)

        if app:
            app.status = "failed"
            app.container_id = None
            app.assigned_port = None

        db.commit()
        raise
    finally:
        db.close()
