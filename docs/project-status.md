# Project Status

Last reviewed locally: 2026-07-05.

## Done

- Repository foundation and monorepo tooling are in place.
- Python workspace uses `uv`, Ruff, MyPy, Pytest, and Django test settings.
- Node workspace uses pnpm, React 19, TypeScript, Vite, and ESLint.
- Backend domain models exist for users, people, events, tasks, journal entries, routines,
  routine occurrences, and knowledge edges.
- APIs exist for tasks, today's events, journal extraction, routines, knowledge edges, and
  the planner endpoint.
- The frontend currently supports the Today task flow, Tonight journal capture, and
  Tomorrow planner trigger.
- Local verification passes with `make check`.

## Current Local Startup

- Use Node from `.nvmrc`.
- Use `.env` for local settings; it is ignored by Git.
- SQLite can be used as a local fallback with `DATABASE_URL=sqlite:///chronos-dev.sqlite3`.
- Run `make bootstrap`, `make up`, then `make dev`.

## Known Gaps

- Planner is tested with `TestModel`, but not yet validated against a real provider in this
  checkout.
- Gateway currently supports Anthropic only.
- People models exist, but there is no mounted People API router in `chronos_backend/urls.py`.
- Routines and knowledge graph have backend APIs but no dedicated frontend UI.
- Health, expense, learning, insight, reflection, and relationship-agent slices are not
  implemented yet.
- Auth is still a fixed development user.
- Docker/local PostgreSQL infrastructure is not committed yet.

## Suggested TODO

1. Complete the half-finished routines and knowledge graph vertical slice in the frontend.
2. Add a People API router and expose relationship data intentionally.
3. Extend the AI gateway only after choosing the provider strategy and storing keys locally.
4. Validate the Planner Agent with a real model using a low-limit API key.
5. Add the next product slice: reflection questions or relationship nudges are the most
   natural follow-ups because current journal and people data can feed them.
6. Replace the SQLite fallback with committed local infrastructure once Docker/PostgreSQL
   setup is healthy.
