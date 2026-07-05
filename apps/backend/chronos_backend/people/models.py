"""Person — someone in the user's life, distinct from a system User account.

See docs/data-model.md section 3 (`Person`). Entity resolution (merging "Ali" and
"Ali R." into one Person via `aliases`) is a simple exact/substring match for now;
a real resolution pipeline is deferred until the extraction pipeline needs it.
"""

import uuid

from django.conf import settings
from django.db import models

from chronos_backend.accounts.models import User


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="people"
    )
    display_name = models.CharField(max_length=255)
    relationship_label = models.CharField(max_length=64, blank=True, default="")
    aliases = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "people"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "display_name"], name="unique_person_display_name_per_user"
            )
        ]

    def __str__(self) -> str:
        return self.display_name

    @classmethod
    def get_or_create_by_name(cls, user: User, name: str) -> "Person":
        """Exact-match resolution against display_name and aliases.

        A real entity-resolution step (fuzzy matching, LLM-assisted disambiguation)
        replaces this once the extraction pipeline is LLM-backed — see
        chronos_backend/events/extraction.py.
        """
        existing = cls.objects.filter(user=user, display_name__iexact=name).first()
        if existing:
            return existing
        for person in cls.objects.filter(user=user):
            if any(alias.lower() == name.lower() for alias in person.aliases):
                return person
        return cls.objects.create(user=user, display_name=name)
