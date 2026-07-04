"""Core Event model and its first satellite detail table.

Only `task` events are implemented in this first vertical slice — Conversation, Health,
Mood, etc. detail tables follow the exact same pattern (see docs/data-model.md) and are
added when the feature that needs them is built, not before.
"""

import uuid

from django.conf import settings
from django.db import models


class EventType(models.TextChoices):
    TASK = "task", "Task"
    CONVERSATION = "conversation", "Conversation"
    WORKOUT = "workout", "Workout"
    MEAL = "meal", "Meal"
    MOOD = "mood", "Mood"
    MEETING = "meeting", "Meeting"
    IDEA = "idea", "Idea"
    HABIT_CHECK = "habit_check", "Habit check"
    LEARNING = "learning", "Learning"
    EXPENSE = "expense", "Expense"
    TRIP = "trip", "Trip"
    HEALTH = "health", "Health"


class Event(models.Model):
    """The universal unit of the domain — see docs/data-model.md section 3."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events"
    )
    type = models.CharField(max_length=32, choices=EventType.choices)
    occurred_at = models.DateTimeField(help_text="When it happened, not when it was logged.")
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, default="")
    importance = models.SmallIntegerField(default=3)
    mood_valence = models.SmallIntegerField(
        null=True, blank=True, help_text="-2..+2 quick sentiment, if applicable."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["user", "occurred_at"]),
            models.Index(fields=["user", "type", "occurred_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.type}] {self.title}"


class TaskStatus(models.TextChoices):
    PLANNED = "planned", "Planned"
    IN_PROGRESS = "in_progress", "In progress"
    DONE = "done", "Done"
    SKIPPED = "skipped", "Skipped"


class TaskDetail(models.Model):
    """1:1 satellite table for `Event.type == EventType.TASK`."""

    event = models.OneToOneField(Event, on_delete=models.CASCADE, primary_key=True)
    status = models.CharField(
        max_length=16, choices=TaskStatus.choices, default=TaskStatus.PLANNED
    )
    due_at = models.DateTimeField(null=True, blank=True)
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"TaskDetail(status={self.status}) for {self.event_id}"
