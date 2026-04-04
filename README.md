# Mini PaaS Platform

A lightweight Platform-as-a-Service (PaaS) built with FastAPI, Docker,
and Nginx.

This project allows you to deploy, manage, and expose Docker containers
via HTTP API --- similar to a simplified Heroku.

------------------------------------------------------------------------

## Features

-   📦 Deploy apps from Docker images
-   🔁 Start / Stop / Remove containers
-   📜 View container logs
-   ⚙️ Async deployments via worker (RQ + Redis)
-   📊 Deployment history tracking
-   🌐 Dynamic Nginx routing
-   🧪 Test coverage with pytest

------------------------------------------------------------------------


## Getting Started

### Run project

docker compose up --build -d

### Open API docs

http://localhost/api/docs

------------------------------------------------------------------------

## API Usage

Create app:

curl -X POST http://localhost:8081/apps\
-H "Content-Type: application/json"\
-d '{ "name": "demo-app", "image": "nginx:latest", "internal_port": 80
}'

Deploy:

curl -X POST http://localhost:8081/apps/1/deploy

Open app:

http://localhost/apps/1/

------------------------------------------------------------------------

## Tests

docker compose exec -e PYTHONPATH=/app api pytest -v

------------------------------------------------------------------------

## Author

https://github.com/zamafigl