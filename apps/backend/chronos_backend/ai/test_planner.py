import pytest
from pydantic_ai.models.test import TestModel

from chronos_backend.ai.gateway import GatewayNotConfigured, get_model
from chronos_backend.ai.planner import PendingTask, plan_tomorrow


def test_plan_tomorrow_returns_typed_day_plan() -> None:
    tasks = [
        PendingTask(title="Deep work: ERP module", estimated_minutes=90, importance=5),
        PendingTask(title="Reply to emails", estimated_minutes=20, importance=2),
    ]

    plan = plan_tomorrow("07:00", "23:00", tasks, model=TestModel())

    # TestModel fabricates output honoring the schema — this proves the agent is wired
    # correctly end to end (prompt -> model -> typed DayPlan) without any network call.
    assert isinstance(plan.blocks, list)


def test_gateway_raises_clear_error_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(GatewayNotConfigured):
        get_model()
