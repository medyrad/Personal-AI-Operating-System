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

Prerequisites: `uv`, `pnpm`, `Docker`.

```bash
make bootstrap   # installs Python + Node workspaces, sets up pre-commit
make up           # starts local infrastructure (Postgres, Redis, MinIO, Mailpit)
make dev           # runs backend + frontend in watch mode
```

Full setup instructions land in PR-0005/PR-0006 (local infrastructure and dev containers).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the PR template, branching model, and commit
conventions every change in this repository follows.

## License

MIT — see [`LICENSE`](LICENSE).
