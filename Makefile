SHELL := /bin/bash
ENV ?= .env
include $(ENV)
export $(shell sed 's/=.*//' $(ENV))

.PHONY: up down logs pull restart

up:
	docker compose --env-file $(ENV) up -d

down:
	docker compose --env-file $(ENV) down

pull:
	docker compose --env-file $(ENV) pull

restart:
	docker compose --env-file $(ENV) down && docker compose --env-file $(ENV) up -d

logs:
	docker compose --env-file $(ENV) logs -f --tail=200
