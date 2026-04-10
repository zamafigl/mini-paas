up:
	docker compose up --build -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up --build -d

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

test:
	docker compose exec -e PYTHONPATH=/app api pytest -v

test-deployments:
	docker compose exec -e PYTHONPATH=/app api pytest -v tests/test_deployments.py

shell-api:
	docker compose exec api bash

shell-worker:
	docker compose exec worker bash
migrate-up:
	docker compose run --rm api alembic upgrade head

migrate-stamp:
	docker compose run --rm api alembic stamp head

migrate-current:
	docker compose run --rm api alembic current

migrate-create:
	docker compose run --rm api alembic revision --autogenerate -m "$(m)"
