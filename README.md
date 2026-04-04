# mini-paas

Self-hosted mini PaaS platform for deploying Docker-based applications.

## Current features
- app registration via API
- PostgreSQL-backed app storage
- Docker-based app deployment
- automatic external port assignment
- app status tracking
- health and database health endpoints

## Tech stack
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Docker SDK
- Docker Compose
- Nginx

## Demo flow
1. Create an app via POST /apps
2. Deploy it via POST /apps/{id}/deploy
3. Access the deployed app on the assigned port
4. Inspect app metadata via GET /apps/{id}

## Next steps
- logs endpoint
- stop/remove/start/restart endpoints
- background deployment jobs
- reverse proxy routing