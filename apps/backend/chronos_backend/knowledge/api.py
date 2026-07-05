"""API surface for the knowledge graph. Mounted at /api/knowledge in urls.py."""

from uuid import UUID

from django.http import HttpRequest
from ninja import Router, Schema

from chronos_backend.accounts.devuser import get_dev_user
from chronos_backend.events.models import Event
from chronos_backend.people.models import Person

from .models import EntityType, KnowledgeEdge

router = Router()


class EdgeOutSchema(Schema):
    id: str
    subject_type: str
    subject_id: str
    predicate: str
    object_type: str
    object_id: str
    confidence: float


class EdgeSummaryOutSchema(Schema):
    id: str
    subject_type: str
    subject_id: str
    subject_label: str
    predicate: str
    object_type: str
    object_id: str
    object_label: str
    confidence: float


def _serialize(edge: KnowledgeEdge) -> EdgeOutSchema:
    return EdgeOutSchema(
        id=str(edge.id),
        subject_type=edge.subject_type,
        subject_id=str(edge.subject_id),
        predicate=edge.predicate,
        object_type=edge.object_type,
        object_id=str(edge.object_id),
        confidence=float(edge.confidence),
    )


def _label_for(entity_type: str, entity_id: UUID) -> str:
    user = get_dev_user()
    if entity_type == EntityType.PERSON:
        person = Person.objects.filter(user=user, id=entity_id).first()
        return person.display_name if person else "Unknown person"
    if entity_type == EntityType.EVENT:
        event = Event.objects.filter(user=user, id=entity_id).first()
        return event.title if event else "Unknown event"
    return str(entity_id)


def _serialize_summary(edge: KnowledgeEdge) -> EdgeSummaryOutSchema:
    return EdgeSummaryOutSchema(
        id=str(edge.id),
        subject_type=edge.subject_type,
        subject_id=str(edge.subject_id),
        subject_label=_label_for(edge.subject_type, edge.subject_id),
        predicate=edge.predicate,
        object_type=edge.object_type,
        object_id=str(edge.object_id),
        object_label=_label_for(edge.object_type, edge.object_id),
        confidence=float(edge.confidence),
    )


@router.get("/edges", response=list[EdgeOutSchema])
def list_edges(
    request: HttpRequest,
    subject_type: str | None = None,
    subject_id: str | None = None,
) -> list[EdgeOutSchema]:
    edges = KnowledgeEdge.objects.filter(user=get_dev_user())
    if subject_type:
        edges = edges.filter(subject_type=subject_type)
    if subject_id:
        edges = edges.filter(subject_id=subject_id)
    return [_serialize(e) for e in edges]


@router.get("/summary", response=list[EdgeSummaryOutSchema])
def list_edge_summaries(request: HttpRequest) -> list[EdgeSummaryOutSchema]:
    edges = KnowledgeEdge.objects.filter(user=get_dev_user()).order_by("-created_at")[:25]
    return [_serialize_summary(edge) for edge in edges]
