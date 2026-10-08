DC = docker compose
APP_CONTAINER = app


.PHONY: up down restart logs logs-worker

up:
	$(DC) up -d --build

down:
	$(DC) down

restart:
	$(DC) restart

logs:
	$(DC) logs -f $(APP_CONTAINER)

logs-worker:
	${DC} logs -f payment_worker