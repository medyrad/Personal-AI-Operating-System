"""API surface for the knowledge graph. Mounted at /api/knowledge in urls.py."""

from django.http import HttpRequest
from ninja import Router, Schema

from chronos_backend.accounts.devuser import get_dev_user

from .models import KnowledgeEdge

router = Router()


class EdgeOutSchema(Schema):
    id: str
    subject_type: str
    subject_id: str
    predicate: str
    object_type: str
    object_id: str
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
