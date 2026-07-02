# Contributing to Chronos

This repository is developed as a series of small, reviewable, production-quality pull
requests. Every PR — whether written by a human or generated with AI assistance — follows
the same discipline described below.

## Branching Model

- `main` is always deployable.
- Work happens on short-lived branches named `type/scope-short-description`, e.g.
  `feat/backend-event-model`, `chore/repo-tooling`, `fix/planner-timezone-bug`.
- Branches are rebased onto `main` before merge; no merge commits in history.
- Squash-merge into `main` so each PR becomes exactly one commit on the trunk.

## Commit Convention

This repository follows [Conventional Commits](https://www.conventionalcommits.org/),
enforced by `commitlint` (see PR-0004):

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`.

Examples:
```
feat(backend): add Event aggregate and repository
chore(repo): initialize production repository
docs(adr): record decision on knowledge graph storage
```

## Pull Request Template

Every PR description must follow this structure — no exceptions:

1. **Title** — conventional-commit style.
2. **Objective** — what this PR accomplishes and why, in one or two sentences.
3. **Architecture Decision** — any design choice made or reaffirmed, with rationale.
   Link to an ADR in `docs/adr/` if the decision is non-trivial or reversible at cost.
4. **Directory Changes** — a tree view of files added, modified, or removed.
5. **Files** — the list of files touched.
6. **Implementation** — a short walkthrough of what the code does.
7. **Commands** — exact commands to run the PR locally (setup, run, verify).
8. **Tests** — what is covered and how to run it.
9. **Expected Output** — what a reviewer should see when running the commands.
10. **Code Review** — self-review notes: trade-offs, known limitations, follow-ups.
11. **Lessons Learned** — what this PR teaches, for the engineering notebook.
12. **Interview Questions** — 2–3 questions this PR's topic could generate in a senior
    engineering interview, with brief answers.
13. **Next PR** — what naturally follows.

## Code Standards

- No placeholders, no `TODO` left in merged code. If something is intentionally deferred,
  it belongs in an issue, not a comment.
- Python: formatted and linted with Ruff, type-checked with MyPy (strict mode where
  practical).
- TypeScript: formatted and linted per the shared config in PR-0003, `strict: true`.
- Every backend module and every non-trivial frontend module ships with tests in the same
  PR that introduces it.

## Definition of Done

A PR is done when:
- CI is green (lint, type-check, tests, security scan, build).
- The PR template is fully filled in.
- Any new architecture decision has a corresponding ADR.
- No `TODO`, no dead code, no commented-out blocks.

## Getting Help

Open a discussion or draft PR early rather than working in isolation on a large change —
this repository favors small, frequent, reviewable increments over large batches.
