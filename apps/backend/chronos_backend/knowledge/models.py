"""KnowledgeEdge — the knowledge graph, as a generic polymorphic table in PostgreSQL.

See docs/data-model.md section 3 and docs/adr/ for why this lives here instead of Neo4j:
one relational fact per row (`subject --predicate--> object`), with no traversal query
patterns yet demanding a native graph engine.

Deliberately no FK constraints on subject_id/object_id — they're polymorphic across
Person, Project, Event, Tag. Integrity is enforced at the application layer (see
`create_edge` in this module), which is the one intentional denormalization in the schema.
"""

import uuid

from django.conf import settings
from django.db import models


class EntityType(models.TextChoices):
    PERSON = "person", "Person"
    PROJECT = "project", "Project"
    EVENT = "event", "Event"
    TAG = "tag", "Tag"


class KnowledgeEdge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="knowledge_edges"
    )
    subject_type = models.CharField(max_length=16, choices=EntityType.choices)
    subject_id = models.UUIDField()
    predicate = models.CharField(max_length=64)
    object_type = models.CharField(max_length=16, choices=EntityType.choices)
    object_id = models.UUIDField()
    confidence = models.DecimalField(max_digits=3, decimal_places=2, default=1)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "subject_type", "subject_id"]),
            models.Index(fields=["user", "object_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return (
            f"({self.subject_type}:{self.subject_id}) "
            f"-{self.predicate}-> ({self.object_type}:{self.object_id})"
        )
