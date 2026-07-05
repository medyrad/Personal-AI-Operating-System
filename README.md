# Chronos

> An AI-powered digital twin of your life — a system that continuously learns from your
> actions, routines, conversations, projects, and reflections, then helps you plan tomorrow
> and understand today.

Chronos is **not** a to-do app. It is a personal operating system built around three ideas:

1. **Everything is an Event.** Tasks, conversations, workouts, meals, moods, meetings, ideas
   and habits are all stored as structured Life Events with time, people, emotion, and tags.
2. **Narrative is richer than checkboxes.** Daily free-text scenarios and voice notes are
   parsed into structured facts without forcing the user to tag anything manually.
3. **The LLM is a reasoning engine, not the database.** Structured data (tasks, routines,
   calendar, people, projects) gives reliable facts. A knowledge graph captures long-term
   relationships. The model reasons over both to coach, plan, and explain.

## Status

Architecture and domain design: complete. Implementation: in progress, PR by PR.
See [`docs/roadmap.md`](docs/roadmap.md) for the full phase breakdown and
[`docs/adr/`](docs/adr/) for frozen architecture decisions.

## Monorepo Layout

```
chronos/
├── apps/
│   ├── backend/          # Django + Django Ninja API
│   └── frontend/         # React 19 + Vite
├── services/
│   ├── cognitive/        # memory, planner, knowledge, decision, reflection
│   ├── ai/                # gateway, prompts, evaluation
│   └── platform/          # telemetry, search
├── infra/
│   ├── docker/            # local infrastructure (Postgres, Redis, MinIO, Mailpit)
│   └── ci/                 # GitHub Actions workflows
├── docs/
│   ├── adr/                # Architecture Decision Records
│   └── roadmap.md
├── pyproject.toml
├── package.json
├── pnpm-workspace.yaml
└── Makefile
```

## Technology Stack (frozen — see ADRs to change)

| Category | Decision |
|---|---|
| Monorepo | pnpm + uv |
| Backend | Django + Django Ninja |
| Frontend | React 19 + Vite |
| Language | Python 3.13 + TypeScript |
| Database | PostgreSQL 17 |
| Cache | Redis |
| Queue | Celery |
| API | OpenAPI |
| Auth | JWT + OAuth2 |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki, Tempo, Sentry |
| Testing | Pytest + Vitest + Playwright |
| AI | LangGraph + Pydantic AI + MCP |
| Vector Search | PostgreSQL + pgvector |
| Knowledge Graph | PostgreSQL first, Neo4j optional later |

## Getting Started

Prerequisites:

- `uv`
- Node 22.21.1 (`nvm use` reads `.nvmrc`)
- `pnpm` through Corepack
- Rust 1.83+ when Python packages need to build native wheels

Create a local environment file. It is ignored by Git:

```bash
cp apps/backend/.env.example .env
```

For the current local vertical slice, either keep the PostgreSQL URL from the example or
use the lightweight SQLite fallback:

```bash
DATABASE_URL=sqlite:///chronos-dev.sqlite3
```

Bootstrap and verify the workspace:

```bash
nvm use
make bootstrap
make up
make check
```

Run the app:

```bash
make dev
```

The backend runs at `http://127.0.0.1:8000/`, and the frontend runs at
`http://127.0.0.1:5173/`.

You can also run the servers separately:

```bash
make dev-backend
make dev-frontend
```

Notes from the first local startup on this machine:

- Docker daemon was not running, so local Docker infrastructure was not used.
- The installed Homebrew PostgreSQL 18 had missing shared files, so the app was started
  with the SQLite fallback above.
- Python dependency installation required updating Rust from 1.78 to a newer stable
  toolchain because `cryptography` builds require Rust 1.83+.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the PR template, branching model, and commit
conventions every change in this repository follows.

## License

MIT — see [`LICENSE`](LICENSE).
