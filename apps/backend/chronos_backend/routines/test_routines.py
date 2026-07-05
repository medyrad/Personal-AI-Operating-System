import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_create_routine() -> None:
    client = Client()
    response = client.post(
        "/api/routines/",
        data={"name": "Morning workout", "category": "health", "schedule_rule": "FREQ=DAILY"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Morning workout"


def test_ensure_today_creates_pending_occurrence() -> None:
    client = Client()
    routine = client.post(
        "/api/routines/",
        data={"name": "Evening reading", "schedule_rule": "FREQ=DAILY"},
        content_type="application/json",
    ).json()

    response = client.post(f"/api/routines/{routine['id']}/today")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending"

    # Idempotent: calling again the same day returns the same occurrence, not a duplicate.
    again = client.post(f"/api/routines/{routine['id']}/today").json()
    assert again["id"] == body["id"]


def test_list_today_occurrences_prepares_due_routines() -> None:
    client = Client()
    daily = client.post(
        "/api/routines/",
        data={"name": "Daily planning", "schedule_rule": "FREQ=DAILY"},
        content_type="application/json",
    ).json()

    response = client.get("/api/routines/occurrences/today")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["routine_id"] == daily["id"]
    assert body[0]["status"] == "pending"


def test_fulfill_occurrence_creates_habit_check_event() -> None:
    client = Client()
    routine = client.post(
        "/api/routines/",
        data={"name": "Stretch", "schedule_rule": "FREQ=DAILY"},
        content_type="application/json",
    ).json()
    occurrence = client.post(f"/api/routines/{routine['id']}/today").json()

    response = client.post(f"/api/routines/occurrences/{occurrence['id']}/fulfill")

    assert response.status_code == 200
    assert response.json()["status"] == "fulfilled"


def test_skip_occurrence_records_reason() -> None:
    client = Client()
    routine = client.post(
        "/api/routines/",
        data={"name": "Journal before bed", "schedule_rule": "FREQ=DAILY"},
        content_type="application/json",
    ).json()
    occurrence = client.post(f"/api/routines/{routine['id']}/today").json()

    response = client.post(
        f"/api/routines/occurrences/{occurrence['id']}/skip",
        data={"reason": "Worked late"},
        content_type="application/json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "skipped"
    assert body["skip_reason"] == "Worked late"
