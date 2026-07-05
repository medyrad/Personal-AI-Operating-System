"""Convenience helpers for creating KnowledgeEdge rows from real model instances,
so callers don't have to know the EntityType/UUID plumbing by hand."""

from decimal import Decimal

from chronos_backend.accounts.models import User

from .models import EntityType, KnowledgeEdge

_MODEL_TO_ENTITY_TYPE = {
    "Person": EntityType.PERSON,
    "Project": EntityType.PROJECT,
    "Event": EntityType.EVENT,
    "Tag": EntityType.TAG,
}


def _entity_type_for(instance: object) -> str:
    name = type(instance).__name__
    try:
        return _MODEL_TO_ENTITY_TYPE[name]
    except KeyError as exc:
        raise ValueError(f"No EntityType mapping for model {name!r}") from exc


def create_edge(
    user: User,
    subject: object,
    predicate: str,
    obj: object,
    confidence: float = 1.0,
) -> KnowledgeEdge:
    return KnowledgeEdge.objects.create(
        user=user,
        subject_type=_entity_type_for(subject),
        subject_id=subject.pk,  # type: ignore[attr-defined]
        predicate=predicate,
        object_type=_entity_type_for(obj),
        object_id=obj.pk,  # type: ignore[attr-defined]
        confidence=Decimal(str(confidence)),
    )
