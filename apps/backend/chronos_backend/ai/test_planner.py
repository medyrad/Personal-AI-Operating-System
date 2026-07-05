import pytest
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.test import TestModel

from chronos_backend.ai.gateway import GatewayNotConfigured, get_model
from chronos_backend.ai.planner import (
    DayPlan,
    PendingTask,
    PlannerValidationError,
    TimeBlock,
    plan_tomorrow,
    validate_day_plan,
)


def test_plan_tomorrow_returns_typed_day_plan() -> None:
    tasks = [
        PendingTask(title="Deep work: ERP module", estimated_minutes=90, importance=5),
        PendingTask(title="Reply to emails", estimated_minutes=20, importance=2),
    ]

    plan = plan_tomorrow(
        "07:00",
        "23:00",
        tasks,
        model=TestModel(
            custom_output_args={
                "blocks": [
                    {
                        "start": "08:00",
                        "end": "09:30",
                        "activity": "Deep work: ERP module",
                        "reason": "This protected morning slot fits the highest-importance task.",
                    },
                    {
                        "start": "10:00",
                        "end": "10:20",
                        "activity": "Reply to emails",
                        "reason": "A short admin block works after the deep work recovery gap.",
                    },
                ]
            }
        ),
    )

    # TestModel fabricates output honoring the schema — this proves the agent is wired
    # correctly end to end (prompt -> model -> typed DayPlan) without any network call.
    assert isinstance(plan.blocks, list)


def test_planner_rejects_overlapping_blocks() -> None:
    plan = DayPlan(
        blocks=[
            TimeBlock(start="08:00", end="09:00", activity="Deep work", reason="Early focus."),
            TimeBlock(start="08:45", end="09:15", activity="Email", reason="Too soon."),
        ]
    )

    with pytest.raises(PlannerValidationError, match="overlaps"):
        validate_day_plan(plan, wake_time="07:00", sleep_time="23:00")


def test_planner_rejects_blocks_outside_wake_sleep_window() -> None:
    plan = DayPlan(
        blocks=[
            TimeBlock(
                start="06:30",
                end="07:15",
                activity="Premature work",
                reason="This starts before wake time.",
            )
        ]
    )

    with pytest.raises(PlannerValidationError, match="wake_time"):
        validate_day_plan(plan, wake_time="07:00", sleep_time="23:00")


def test_planner_rejects_invalid_time_format() -> None:
    plan = DayPlan(
        blocks=[
            TimeBlock(
                start="8am",
                end="09:00",
                activity="Ambiguous block",
                reason="The model must use HH:MM format.",
            )
        ]
    )

    with pytest.raises(PlannerValidationError, match="HH:MM"):
        validate_day_plan(plan, wake_time="07:00", sleep_time="23:00")


def test_planner_accepts_django_time_boundaries() -> None:
    plan = DayPlan(
        blocks=[
            TimeBlock(
                start="08:00",
                end="09:00",
                activity="Deep work",
                reason="The block is inside the user's default Django time boundaries.",
            )
        ]
    )

    assert validate_day_plan(plan, wake_time="07:00:00", sleep_time="23:00:00") == plan


def test_gateway_raises_clear_error_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHRONOS_DISABLE_DOTENV_FILL", "1")
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(GatewayNotConfigured):
        get_model()


def test_gateway_uses_openai_when_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    assert isinstance(get_model(), OpenAIChatModel)


def test_gateway_auto_prefers_anthropic_when_both_keys_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    assert isinstance(get_model(), AnthropicModel)


def test_gateway_rejects_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "local")

    with pytest.raises(GatewayNotConfigured, match="AI_PROVIDER"):
        get_model()
