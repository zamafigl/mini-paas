# Mini PaaS Platform

![CI](https://github.com/zamafigl/mini-paas/actions/workflows/ci.yml/badge.svg)

A lightweight self-hosted Platform-as-a-Service built with **FastAPI, Docker, Redis, PostgreSQL, Alembic, and Nginx**.

This project allows you to:

- register applications through an API
- deploy Docker containers asynchronously
- manage container lifecycle
- expose deployed apps through dynamic Nginx routing
- inspect logs
- track deployment history

The goal of the project is not to compete with Kubernetes or a production-grade orchestrator.  
It is a **single-host mini PaaS** that demonstrates backend, infrastructure, async job processing, container lifecycle management, and platform-style thinking.

---

## Features

- application registration via REST API
- application listing and retrieval
- asynchronous deployment with **Redis + RQ worker**
- Docker-based container lifecycle management
- start / stop / restart / remove operations for deployed apps
- container logs retrieval
- deployment history tracking
- dynamic Nginx route generation
- health and database health endpoints
- database migrations with **Alembic**
- API test coverage with **pytest**
- local developer commands via **Makefile**

---

## Tech Stack

- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Redis**
- **RQ**
- **Docker SDK**
- **Docker Compose**
- **Nginx**
- **Alembic**
- **Pytest**

---

## Architecture

```text
Client
  |
  v
Nginx
  |--------------------> /api/* --------------------> FastAPI API
  |
  |--------------------> /apps/{id}/ ---------------> Deployed App Container

FastAPI API
  |--------------------> PostgreSQL (apps + deployment history)
  |
  |--------------------> Redis queue ---> Worker ---> Docker SDK ---> Containers
                                                   |
                                                   +--> dynamic Nginx route generation
```


--- 

## How It Works

A user creates an application record through the API.
A deployment request is sent to the API.
The API enqueues a deployment job into Redis.
The worker consumes the job and starts a Docker container.
The worker updates application state and deployment history in PostgreSQL.
A dynamic Nginx route is generated for the deployed application.
The application becomes accessible through /apps/{id}/.
Project Structure
mini-paas/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       └── apps.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   ├── schemas/
│   ├── services/
│   │   └── docker_service.py
│   └── main.py
├── worker/
│   ├── jobs.py
│   └── worker.py
├── nginx/
│   ├── nginx.conf
│   └── dynamic/
├── tests/
├── alembic/
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.worker
├── Makefile
├── requirements.txt
└── README.md


## Quick Start
1. Clone the repository
git clone https://github.com/zamafigl/mini-paas.git
cd mini-paas
2. Create environment file
cp .env.example .env
3. Build and start services
make up

Or without Makefile:

docker compose up --build -d
4. Apply database migrations

For a fresh environment:

make migrate-up

If your local database already contains tables created before Alembic integration:

make migrate-stamp
5. Open API docs
http://localhost:8081/docs

Nginx is exposed on port 80, and the API container is exposed on port 8081.

Environment Variables

Example .env.example:

APP_NAME=mini-paas
APP_HOST=0.0.0.0
APP_PORT=8081
DEBUG=false

POSTGRES_DB=mini_paas
POSTGRES_USER=mini_paas
POSTGRES_PASSWORD=mini_paas
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

DOCKER_NETWORK=mini-paas_default
NGINX_CONTAINER_NAME=mini-paas-nginx
NGINX_DYNAMIC_DIR=/app/nginx/dynamic
API Examples
Create an app
curl -X POST http://localhost:8081/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-app",
    "image": "nginx:latest",
    "internal_port": 80
  }'
List apps
curl http://localhost:8081/apps
Get app by id
curl http://localhost:8081/apps/1
Deploy app
curl -X POST http://localhost:8081/apps/1/deploy
View logs
curl http://localhost:8081/apps/1/logs
Stop app
curl -X POST http://localhost:8081/apps/1/stop
Start app
curl -X POST http://localhost:8081/apps/1/start
Restart app
curl -X POST http://localhost:8081/apps/1/restart
Remove deployed container
curl -X POST http://localhost:8081/apps/1/remove
Deployment history
curl http://localhost:8081/apps/1/deployments
Health checks
curl http://localhost:8081/health
curl http://localhost:8081/db-health
Makefile Commands
Runtime
make up
make down
make restart
make logs
make ps
Testing
make test
make test-deployments
Migrations
make migrate-up
make migrate-stamp
make migrate-current
make migrate-create m="add new field"
Shell access
make shell-api
make shell-worker
Database Migrations

This project uses Alembic for schema management.

Initialize schema on a fresh environment
make migrate-up
Mark an existing local database as current

Use this when your tables already exist and you do not want Alembic to recreate them:

make migrate-stamp
Create a new migration after changing models
make migrate-create m="add new field"
make migrate-up
Testing

Run tests through the API container:

make test

Or directly:

docker compose exec -e PYTHONPATH=/app api pytest -v

The test suite currently focuses on:

application CRUD
deployment endpoint behavior
lifecycle endpoints
logs endpoint
deployment history endpoint
Design Decisions
Asynchronous deployment flow
The API does not deploy containers directly. It enqueues a job in Redis, and the worker performs the deployment.
Separated responsibilities
FastAPI handles API requests, PostgreSQL stores state, Redis buffers jobs, and the worker communicates with Docker.
Dynamic Nginx routing
For each deployed app, a route config is generated dynamically and Nginx is reloaded.
Single-host scope
This project is intentionally designed as a lightweight single-node platform rather than a production-grade orchestrator.
State tracking through database records
Application status and deployment history are persisted in PostgreSQL so lifecycle operations can be observed and queried.
Current Limitations
no authentication
no multi-user support
no resource quotas
single-host deployment only
limited worker/integration coverage compared with a full production platform
Nginx reload strategy is simple and not optimized for high-scale scenarios
no rollback support yet
Roadmap
authentication and role-based access
resource limits / quotas
rollback support
deployment retries and backoff
richer worker and integration test coverage
metrics and observability
better deployment failure diagnostics
image validation / safer deployment policies
Why This Project Matters

This repository is meant to demonstrate more than CRUD.

It shows:

API design with FastAPI
relational data modeling with SQLAlchemy
asynchronous job execution with Redis + RQ
Docker container lifecycle automation
reverse proxy integration with Nginx
database schema versioning with Alembic
project packaging and testability

In other words, it is a backend/infrastructure project with a platform engineering flavor.

License

This project is provided for educational and portfolio purposes.