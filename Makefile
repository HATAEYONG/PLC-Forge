.PHONY: up down backend-test backend-lint frontend-test frontend-lint test lint

up:
	docker compose up --build

down:
	docker compose down

backend-test:
	cd backend && python -m pytest -q

backend-lint:
	cd backend && ruff check . && ruff format --check .

frontend-test:
	cd frontend && npm run test

frontend-lint:
	cd frontend && npm run lint && npm run format:check && npx tsc --noEmit

test: backend-test frontend-test

lint: backend-lint frontend-lint
