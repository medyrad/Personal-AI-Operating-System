"""Planner Agent — the first real agent in Chronos.

Takes tomorrow's pending tasks plus the user's wake/sleep window and produces a reasoned
time-boxed schedule: not just placement, but *why* each block is where it is (per the
product vision — "you slept 5 hours, don't schedule 4 hours of deep work").

Per docs/adr/0001-ai-orchestration-split.md: this agent is a self-contained Pydantic AI
agent with a typed output. It is not yet wired into a LangGraph graph because there is
only one agent so far — orchestration is added when a second agent needs to run before or
after this one.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import Model

from .gateway import get_model

SYSTEM_PROMPT = """\
You are the Planner Agent inside Chronos, a personal AI operating system.

You build tomorrow's time-boxed schedule from a wake time, a sleep time, and a list of
pending tasks. You do not simply place tasks back to back:
- Leave buffer and recovery time; do not fill every minute.
- Put a short break between tasks longer than 45 minutes.
- Respect each task's `estimated_minutes` and `importance` — higher importance tasks get
  earlier, more protected slots.
- Always give a one-sentence `reason` for each block explaining the placement, in the
  voice of a thoughtful coach, not a scheduling algorithm.
- Every block's `start` and `end` must be between wake_time and sleep_time, in "HH:MM"
  24-hour format, non-overlapping, and in chronological order.
"""


class PendingTask(BaseModel):
    title: str
    estimated_minutes: int | None = Field(
        default=None, description="Best guess if not provided: 30."
    )
    importance: int = Field(default=3, ge=1, le=5)


class TimeBlock(BaseModel):
    start: str = Field(description="HH:MM 24-hour")
    end: str = Field(description="HH:MM 24-hour")
    activity: str
    reason: str


class DayPlan(BaseModel):
    blocks: list[TimeBlock]


def build_agent(model: Model | None = None) -> Agent[None, DayPlan]:
    """Builds the agent. Pass an explicit `model` (e.g. TestModel) in tests."""
    return Agent(model or get_model(), output_type=DayPlan, system_prompt=SYSTEM_PROMPT)


def _format_prompt(wake_time: str, sleep_time: str, tasks: list[PendingTask]) -> str:
    lines = [f"Wake time: {wake_time}", f"Sleep time: {sleep_time}", "Pending tasks:"]
    for task in tasks:
        minutes = task.estimated_minutes or "unknown"
        lines.append(f"- {task.title} (~{minutes} min, importance {task.importance}/5)")
    return "\n".join(lines)


def plan_tomorrow(
    wake_time: str,
    sleep_time: str,
    tasks: list[PendingTask],
    model: Model | None = None,
) -> DayPlan:
    agent = build_agent(model)
    result = agent.run_sync(_format_prompt(wake_time, sleep_time, tasks))
    return result.output
