import pytest
from django.test import Client

from chronos_backend.ai.planner import PlannerValidationError

pytestmark = pytest.mark.django_db


def test_planner_endpoint_returns_502_for_invalid_model_schedule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken_plan(*args: object, **kwargs: object) -> None:
        raise PlannerValidationError("Block 1 overlaps or is earlier than a previous block.")

    monkeypatch.setattr("chronos_backend.ai.api.plan_tomorrow", broken_plan)

    response = Client().post("/api/ai/planner/tomorrow")

    assert response.status_code == 502
    assert "overlaps" in response.json()["detail"]
