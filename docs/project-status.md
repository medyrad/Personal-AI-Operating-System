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
- People API exists for listing, creating, and updating relationship context.
- Knowledge graph summaries resolve event/person labels for UI consumption.
- Routine occurrences for the current day are hydrated on page load, so the UI reflects
  pending/fulfilled/skipped state without manual preparation.
- The frontend currently supports the Today task flow, Tonight journal capture, Tomorrow
  planner trigger, routines, people, and knowledge summaries.
- The frontend supports English/Persian UI copy, LTR/RTL layout direction, and dark/light
  themes with local preference persistence.
- The AI gateway supports `AI_PROVIDER=auto|anthropic|openai`, model overrides, Anthropic
  keys, and OpenAI keys without hard-coding provider logic inside agents.
- Local verification passes with `make check`.

## Current Local Startup

- Use Node from `.nvmrc`.
- Use `.env` for local settings; it is ignored by Git.
- SQLite can be used as a local fallback with `DATABASE_URL=sqlite:///chronos-dev.sqlite3`.
- Run `make bootstrap`, `make up`, then `make dev`.

## Known Gaps

- Planner is tested with `TestModel`, but not yet validated against a real provider because
  no fresh safe API key has been configured.
- Routine recurrence remains intentionally minimal: daily and weekly-by-day only.
- Knowledge graph UI is still a compact relationship feed, not a spatial exploratory
  graph view.
- Health, expense, learning, insight, reflection, and relationship-agent slices are not
  implemented yet.
- Auth is still a fixed development user.
- Docker/local PostgreSQL infrastructure is not committed yet.

## Suggested TODO

1. Validate the Planner Agent with a real model using a fresh, low-limit API key.
2. Add the next product slice: reflection questions or relationship nudges are the most
   natural follow-ups because current journal and people data can feed them.
3. Replace the SQLite fallback with committed local infrastructure once Docker/PostgreSQL
   setup is healthy.
4. Expand routines beyond the compact panel when weekly/monthly planning becomes a real
   user workflow.
