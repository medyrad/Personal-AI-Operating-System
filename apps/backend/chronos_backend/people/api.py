"""API surface for people in the user's life. Mounted at /api/people."""

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router, Schema

from chronos_backend.accounts.devuser import get_dev_user

from .models import Person

router = Router()


class PersonCreateSchema(Schema):
    display_name: str
    relationship_label: str = ""
    aliases: list[str] = []


class PersonUpdateSchema(Schema):
    relationship_label: str = ""
    aliases: list[str] = []


class PersonOutSchema(Schema):
    id: str
    display_name: str
    relationship_label: str
    aliases: list[str]


def _serialize(person: Person) -> PersonOutSchema:
    return PersonOutSchema(
        id=str(person.id),
        display_name=person.display_name,
        relationship_label=person.relationship_label,
        aliases=person.aliases,
    )


@router.get("/", response=list[PersonOutSchema])
def list_people(request: HttpRequest) -> list[PersonOutSchema]:
    people = Person.objects.filter(user=get_dev_user()).order_by("display_name")
    return [_serialize(person) for person in people]


@router.post("/", response=PersonOutSchema)
def create_person(request: HttpRequest, payload: PersonCreateSchema) -> PersonOutSchema:
    person = Person.get_or_create_by_name(get_dev_user(), payload.display_name.strip())
    person.relationship_label = payload.relationship_label.strip()
    person.aliases = [alias.strip() for alias in payload.aliases if alias.strip()]
    person.save(update_fields=["relationship_label", "aliases"])
    return _serialize(person)


@router.patch("/{person_id}", response=PersonOutSchema)
def update_person(
    request: HttpRequest, person_id: str, payload: PersonUpdateSchema
) -> PersonOutSchema:
    person = get_object_or_404(Person, id=person_id, user=get_dev_user())
    person.relationship_label = payload.relationship_label.strip()
    person.aliases = [alias.strip() for alias in payload.aliases if alias.strip()]
    person.save(update_fields=["relationship_label", "aliases"])
    return _serialize(person)
