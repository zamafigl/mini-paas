# Mini PaaS Platform

A lightweight self-hosted Platform-as-a-Service built with FastAPI, Docker, Redis, PostgreSQL, and Nginx.

This project allows you to register applications, deploy Docker containers asynchronously, manage their lifecycle, expose them through Nginx routing, and track deployment history.

## Features

- app registration via API
- app listing and retrieval
- asynchronous app deployment with Redis + RQ worker
- Docker-based container lifecycle management
- start / stop / remove deployed apps
- container logs retrieval
- deployment history tracking
- dynamic Nginx routing
- health and database health endpoints
- basic API tests with pytest

## Tech Stack

- FastAPI
- PostgreSQL
- Redis
- RQ
- SQLAlchemy
- Docker SDK
- Docker Compose
- Nginx
- Pytest

## Architecture

```text
Client
  |
  v
Nginx
  |
  +--> /api/* --------------> FastAPI API
  |
  +--> /apps/{id}/ ---------> Deployed app container

FastAPI API
  |
  +--> PostgreSQL (apps + deployment history)
  |
  +--> Redis queue ---> Worker ---> Docker SDK ---> Containers
How It Works
A user creates an app record through the API
A deploy request is sent to the API
The API pushes a deployment job into Redis
The worker consumes the job and starts a Docker container
The worker updates app state and deployment history in PostgreSQL
Nginx route config is generated dynamically
The deployed app becomes доступен through /apps/{id}/
Quick Start
docker compose up --build -d

API docs:

http://localhost/api/docs
API Examples
Create app
curl -X POST http://localhost:8081/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-app",
    "image": "nginx:latest",
    "internal_port": 80
  }'
Get app
curl http://localhost:8081/apps/1
Deploy app
curl -X POST http://localhost:8081/apps/1/deploy
View logs
curl http://localhost:8081/apps/1/logs
Stop app
curl -X POST http://localhost:8081/apps/1/stop
Start app
curl -X POST http://localhost:8081/apps/1/start
Remove app
curl -X POST http://localhost:8081/apps/1/remove
Deployment history
curl http://localhost:8081/apps/1/deployments
Health checks
curl http://localhost:8081/health
curl http://localhost:8081/db-health
Tests

Run tests inside the API container:

docker compose exec -e PYTHONPATH=/app api pytest -v
Current Limitations
no authentication
no multi-user support
no resource quotas
single-host deployment only
limited test coverage for worker/nginx integration
