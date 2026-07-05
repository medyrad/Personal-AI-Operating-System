import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_create_task_creates_event_and_detail() -> None:
    client = Client()
    response = client.post(
        "/api/events/tasks",
        data={"title": "Buy milk", "estimated_minutes": 10, "importance": 2},
        content_type="application/json",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["status"] == "planned"
    assert body["estimated_minutes"] == 10


def test_list_today_returns_created_task() -> None:
    client = Client()
    client.post(
        "/api/events/tasks",
        data={"title": "Read 30 min"},
        content_type="application/json",
    )
    response = client.get("/api/events/today")
    assert response.status_code == 200
    titles = [event["title"] for event in response.json()]
    assert "Read 30 min" in titles


def test_complete_task_transitions_status() -> None:
    client = Client()
    created = client.post(
        "/api/events/tasks",
        data={"title": "Exercise"},
        content_type="application/json",
    ).json()

    response = client.post(f"/api/events/tasks/{created['id']}/complete")

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_journal_entry_extracts_mood_event() -> None:
    client = Client()
    response = client.post(
        "/api/journal",
        data={"raw_text": "Had a stressed and tired day, meetings ran long."},
        content_type="application/json",
    )
    assert response.status_code == 200
    body = response.json()
    types = [e["type"] for e in body["extracted_events"]]
    assert "mood" in types


def test_journal_entry_with_no_signal_creates_no_events() -> None:
    client = Client()
    response = client.post(
        "/api/journal",
        data={"raw_text": "Reviewed the quarterly budget spreadsheet."},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["extracted_events"] == []
