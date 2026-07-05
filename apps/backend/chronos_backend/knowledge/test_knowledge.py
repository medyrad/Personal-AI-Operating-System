import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_journal_with_person_mention_creates_conversation_and_edge() -> None:
    client = Client()
    response = client.post(
        "/api/journal",
        data={"raw_text": "Had a long meeting with Ali about the ERP architecture."},
        content_type="application/json",
    )
    assert response.status_code == 200
    types = [e["type"] for e in response.json()["extracted_events"]]
    assert "conversation" in types

    edges = client.get("/api/knowledge/edges?subject_type=event").json()
    assert any(edge["predicate"] == "involves" for edge in edges)


def test_same_person_mentioned_twice_resolves_to_one_record() -> None:
    from chronos_backend.accounts.devuser import get_dev_user
    from chronos_backend.people.models import Person

    user = get_dev_user()
    first = Person.get_or_create_by_name(user, "Ali")
    second = Person.get_or_create_by_name(user, "ali")  # case-insensitive match

    assert first.id == second.id
    assert Person.objects.filter(user=user, display_name__iexact="Ali").count() == 1
