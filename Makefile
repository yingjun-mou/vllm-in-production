# Usage:
# make init
# make redeploy
SHELL := /bin/bash
ENV ?= .env
init:
	@test -f .env || cp .env.example .env || true

redeploy:
	docker compose down -v --remove-orphans || true
	docker compose up -d --remove-orphans
