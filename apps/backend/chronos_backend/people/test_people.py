import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_create_and_list_people() -> None:
    client = Client()

    created = client.post(
        "/api/people/",
        data={
            "display_name": "Mina",
            "relationship_label": "friend",
            "aliases": ["Min"],
        },
        content_type="application/json",
    )

    assert created.status_code == 200
    assert created.json()["display_name"] == "Mina"
    assert created.json()["relationship_label"] == "friend"

    listed = client.get("/api/people/")
    assert listed.status_code == 200
    assert listed.json() == [created.json()]


def test_update_person_relationship_context() -> None:
    client = Client()
    person = client.post(
        "/api/people/",
        data={"display_name": "Ali"},
        content_type="application/json",
    ).json()

    response = client.patch(
        f"/api/people/{person['id']}",
        data={"relationship_label": "mentor", "aliases": ["Ali R."]},
        content_type="application/json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["relationship_label"] == "mentor"
    assert body["aliases"] == ["Ali R."]
