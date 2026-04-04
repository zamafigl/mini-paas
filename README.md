# mini-paas

A self-hosted mini PaaS for deploying Docker-based applications via API.

## Overview

mini-paas is a backend service that lets you register applications, deploy them as Docker containers, and manage their lifecycle through an HTTP API.

The project is designed as a simplified Platform-as-a-Service:
you create an app record, trigger deployment, and get a running container with an assigned external port.

## Tech Stack

- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Docker SDK
- Docker Compose

## Implemented Features

- app registration via API
- app listing and retrieval
- PostgreSQL-based persistence
- async deployment via Redis + RQ worker
- automatic external port allocation
- container lifecycle management:
  - deploy
  - stop
  - start
  - remove
- container logs retrieval
- health and database health endpoints
- deployment history tracking

## Architecture

- **API** — FastAPI control plane
- **PostgreSQL** — stores app metadata and deployment history
- **Redis** — queue backend for background jobs
- **Worker** — processes deployment jobs asynchronously
- **Docker SDK** — manages runtime containers
- **Docker Compose** — local orchestration

## How It Works

1. App metadata is stored in PostgreSQL
2. A deploy request is sent to the API
3. The API places a job into Redis queue
4. A worker picks up the deployment job
5. Docker SDK runs the container
6. Assigned port and container metadata are saved to the database
7. Deployment history is recorded

## Quick Start

```bash
docker compose up --build
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
Remove container
curl -X POST http://localhost:8081/apps/1/remove
Deployment history
curl http://localhost:8081/apps/1/deployments
Health checks
curl http://localhost:8081/health
curl http://localhost:8081/db-health