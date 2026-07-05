# ADR-0001: Division of responsibility between Pydantic AI and LangGraph

## Status
Accepted

## Context
The frozen stack lists both LangGraph and Pydantic AI for the AI layer. Both frameworks
offer agent orchestration, so listing them side by side without a rule for which does
what invites duplication and confusion once more than one agent exists.

## Decision
- **Pydantic AI defines individual agents.** Each agent (Planner, Coach, Reflection...) is
  a Pydantic AI `Agent` with a typed `output_type`, so its input/output contract is
  enforced by the type system, not by hoping the model's JSON matches expectations.
- **LangGraph orchestrates multi-agent flows.** Once more than one agent must run in a
  sequence or with conditional branching (e.g. "Coach Agent must review today before the
  Planner Agent builds tomorrow"), that flow becomes a LangGraph graph whose nodes call
  Pydantic AI agents.
- Until a second agent exists, there is nothing to orchestrate — LangGraph is not wired in
  yet. It is added when the first multi-agent flow is actually built, not speculatively.

## Consequences
- Every agent has the same shape regardless of how many end up existing, which keeps
  testing consistent (Pydantic AI's `TestModel` covers each agent in isolation).
- No LangGraph dependency or graph-definition code exists until PR that introduces the
  second agent — avoids an empty/placeholder orchestration layer.

## Alternatives Considered
- **LangGraph for everything, including single agents.** Rejected: adds graph-definition
  overhead for what is, today, a single typed function call.
- **Pydantic AI for everything, including orchestration.** Revisit if LangGraph's graph
  model turns out to be unnecessary once multi-agent flows are real — Pydantic AI alone
  can express simple sequential chains via plain Python.
