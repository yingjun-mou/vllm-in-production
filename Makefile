# Usage:
# make init
# make redeploy
SHELL := /bin/bash
PORT ?= 8000

.PHONY: init stop redeploy ps port logs

init:
	@test -f .env || cp .env.example .env || true

# Avoid race condition
stop:
	- docker compose down -v --remove-orphans
	@echo "Waiting for port $(PORT) to be free..."
	@for i in {1..20}; do \
		if ss -ltnp | grep -q ":$(PORT)\b"; then \
			sleep 1; \
		else \
			echo "Port $(PORT) is free."; \
			break; \
		fi; \
	done
	# Kill any straggler that still publishes the port
	- docker ps --filter publish=$(PORT) -q | xargs -r docker kill

redeploy: stop
	docker compose up -d --remove-orphans

ps:
	docker compose ps

port:
	- ss -ltnp | grep :$(PORT) || echo "Port $(PORT) is free"
	- docker ps --filter publish=$(PORT)

logs:
	docker compose logs --tail=100
