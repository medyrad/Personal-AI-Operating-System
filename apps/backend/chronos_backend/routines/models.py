"""Routine (definition) and RoutineOccurrence (the daily expected-vs-actual fact).

This is the core of the Behavior Engine described in the product vision: a Routine says
what should happen; each day's RoutineOccurrence records what actually did, with a reason
when it didn't — the raw material for insights like "you always skip exercise after a
hard meeting."
"""

import uuid

from django.conf import settings
from django.db import models


class Routine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="routines"
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=64, blank=True, default="")
    schedule_rule = models.CharField(
        max_length=255,
        default="FREQ=DAILY",
        help_text="RRULE string. Only FREQ=DAILY and FREQ=WEEKLY;BYDAY=... are "
        "interpreted today — see occurrences.due_today().",
    )
    expected_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class OccurrenceStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    FULFILLED = "fulfilled", "Fulfilled"
    SKIPPED = "skipped", "Skipped"


class RoutineOccurrence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name="occurrences")
    expected_date = models.DateField()
    status = models.CharField(
        max_length=16, choices=OccurrenceStatus.choices, default=OccurrenceStatus.PENDING
    )
    skip_reason = models.CharField(max_length=255, blank=True, default="")
    fulfilling_event = models.ForeignKey(
        "events.Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["routine", "expected_date"], name="unique_occurrence_per_day"
            )
        ]
        ordering = ["-expected_date"]

    def __str__(self) -> str:
        return f"{self.routine.name} @ {self.expected_date} ({self.status})"
