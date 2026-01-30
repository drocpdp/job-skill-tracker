.PHONY: up down rebuild logs ps migrate test test-down dbshell

up:
	docker compose up -d --build

down:
	docker compose down

rebuild:
	docker compose build --no-cache

logs:
	docker compose logs -f --tail=200 api

ps:
	docker compose ps

migrate:
	docker compose --profile ops run --rm migrate

test:
	docker compose --profile test run --rm test

test-down:
	docker compose --profile test down

dbshell:
	docker compose exec db psql -U postgres -d jobskills_dev
