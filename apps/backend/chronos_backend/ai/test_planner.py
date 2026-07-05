import pytest
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
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
