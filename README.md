# mini-paas

A self-hosted mini PaaS for deploying Docker-based applications via API.

---

## What is this?

mini-paas is a backend service that allows you to register applications and deploy them as Docker containers.

The goal of this project is to simulate a simplified Platform-as-a-Service:
you send a request → your app gets deployed → you get a running container with an exposed port.

---

## Stack

- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Docker SDK
- Docker Compose

---

## Features

- register applications
- deploy containers dynamically
- automatic port allocation
- container lifecycle management:
  - deploy
  - stop
  - start
  - remove
- container logs via API
- health checks

---

## How it works

1. App metadata is stored in PostgreSQL
2. API receives a deploy request
3. Docker SDK runs a container
4. A free port is assigned automatically
5. Container info is saved in DB
6. You can manage it via API

---

## Quick start

```bash
docker compose up --build
API usage
Create app
curl -X POST http://localhost:8081/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-app",
    "image": "nginx:latest",
    "internal_port": 80
  }'
Deploy
curl -X POST http://localhost:8081/apps/1/deploy
Access

Open in browser:

http://localhost:<assigned_port>
Logs
curl http://localhost:8081/apps/1/logs
Stop
curl -X POST http://localhost:8081/apps/1/stop
Start
curl -X POST http://localhost:8081/apps/1/start
Remove
curl -X POST http://localhost:8081/apps/1/remove
Health
curl http://localhost:8081/health
curl http://localhost:8081/db-health