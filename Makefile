.PHONY: bootstrap lint lint-backend lint-frontend format typecheck test build-frontend check migrate up dev dev-backend dev-frontend

bootstrap: ## Install Python and Node workspace dependencies
	uv sync --all-groups
	corepack enable pnpm
	pnpm install --frozen-lockfile

lint: lint-backend lint-frontend ## Run backend and frontend linters

lint-backend: ## Run Ruff over the Python workspace
	uv run ruff check .

lint-frontend: ## Run ESLint over the frontend workspace
	pnpm --filter @chronos/frontend lint

format: ## Auto-fix formatting and safe lint issues
	uv run ruff format .
	uv run ruff check --fix .

typecheck: ## Run MyPy over the backend app
	uv run mypy apps/backend/chronos_backend

test: ## Run the Python test suite
	uv run pytest

build-frontend: ## Build the frontend production bundle
	pnpm --filter @chronos/frontend build

migrate: ## Apply backend database migrations
	uv run python apps/backend/manage.py migrate

check: lint typecheck test build-frontend ## Run the local verification suite

up: migrate ## Prepare local development state

dev-backend: ## Run the Django development server
	uv run python apps/backend/manage.py runserver 127.0.0.1:8000

dev-frontend: ## Run the Vite development server
	pnpm --filter @chronos/frontend dev --host 127.0.0.1

dev: migrate ## Run backend + frontend in watch mode
	@uv run python apps/backend/manage.py runserver 127.0.0.1:8000 & \
	backend_pid=$$!; \
	trap 'kill $$backend_pid 2>/dev/null' INT TERM EXIT; \
	pnpm --filter @chronos/frontend dev --host 127.0.0.1
