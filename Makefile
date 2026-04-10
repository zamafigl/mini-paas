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
