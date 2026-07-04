.PHONY: bootstrap lint typecheck test check up dev

bootstrap: ## Install Python workspace dependencies (Node workspace lands in PR-0003)
	uv sync --all-groups

lint: ## Run Ruff over the whole workspace
	uv run ruff check .

format: ## Auto-fix formatting and safe lint issues
	uv run ruff format .
	uv run ruff check --fix .

typecheck: ## Run MyPy over the backend app
	uv run mypy apps/backend/chronos_backend

test: ## Run the Python test suite
	uv run pytest

check: lint typecheck test ## Run everything CI will run

up: ## Start local infrastructure (Postgres, Redis...) — lands in PR-0005
	@echo "Local infrastructure (docker compose) lands in PR-0005."

dev: ## Run backend + frontend in watch mode — lands with the vertical slice
	@echo "Dev servers land with the first vertical slice."
