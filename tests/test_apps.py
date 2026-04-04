def test_create_app(client):
    payload = {
        "name": "demo-app",
        "image": "nginx:latest",
        "internal_port": 80,
    }

    response = client.post("/apps", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "demo-app"
    assert data["image"] == "nginx:latest"
    assert data["internal_port"] == 80
    assert data["status"] == "created"
    assert data["assigned_port"] is None
    assert data["container_id"] is None


def test_create_app_with_duplicate_name(client):
    payload = {
        "name": "demo-app",
        "image": "nginx:latest",
        "internal_port": 80,
    }

    first_response = client.post("/apps", json=payload)
    second_response = client.post("/apps", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "App with this name already exists"


def test_list_apps(client):
    payload = {
        "name": "demo-app",
        "image": "nginx:latest",
        "internal_port": 80,
    }

    client.post("/apps", json=payload)

    response = client.get("/apps")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "demo-app"


def test_get_app(client):
    payload = {
        "name": "demo-app",
        "image": "nginx:latest",
        "internal_port": 80,
    }

    create_response = client.post("/apps", json=payload)
    app_id = create_response.json()["id"]

    response = client.get(f"/apps/{app_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == app_id
    assert data["name"] == "demo-app"


def test_get_app_not_found(client):
    response = client.get("/apps/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "App not found"

