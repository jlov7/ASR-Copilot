SHELL := /bin/bash

.PHONY: demo dev test lint format compose-up compose-down

demo:
	./app/scripts/run_demo.sh

dev:
	cd app && ./scripts/run_dev.sh

test:
	pytest
	cd app/frontend && npm run test -- --run

lint:
	ruff check .
	cd app/frontend && npm run lint

format:
	ruff format .
	cd app/frontend && npm run lint -- --fix

compose-up:
	docker compose -f compose.yaml up --build

compose-down:
	docker compose -f compose.yaml down
