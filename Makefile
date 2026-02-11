.PHONY: up down build logs backend-logs worker-logs db-shell backend-shell migrate makemigrations restart-workers clean

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

backend-logs:
	docker compose logs -f backend

worker-logs:
	docker compose logs -f worker-processing worker-llm worker-embedding

db-shell:
	docker compose exec db psql -U bookflix

backend-shell:
	docker compose exec backend bash

migrate:
	docker compose exec backend alembic upgrade head

makemigrations:
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

restart-workers:
	docker compose restart worker-processing worker-llm worker-embedding beat

clean:
	docker compose down -v
