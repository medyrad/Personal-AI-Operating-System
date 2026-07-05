"""Core Event model and its satellite detail tables, plus JournalEntry.

Task, Conversation, and Mood detail tables are implemented; Health, Learning, Expense,
and Trip follow the exact same pattern (see docs/data-model.md) and are added when the
feature that needs them is built, not before.
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
    source_journal_entry = models.ForeignKey(
        "JournalEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="extracted_events",
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


class ConversationOutcome(models.TextChoices):
    AGREEMENT = "agreement", "Agreement"
    DISAGREEMENT = "disagreement", "Disagreement"
    UNRESOLVED = "unresolved", "Unresolved"


class ConversationDetail(models.Model):
    """1:1 satellite table for `Event.type == EventType.CONVERSATION`."""

    event = models.OneToOneField(Event, on_delete=models.CASCADE, primary_key=True)
    emotion = models.CharField(max_length=64, blank=True, default="")
    topic = models.CharField(max_length=255, blank=True, default="")
    outcome = models.CharField(
        max_length=16, choices=ConversationOutcome.choices, blank=True, default=""
    )
    relationship_delta = models.SmallIntegerField(
        null=True, blank=True, help_text="-2..+2 change in relationship quality."
    )

    def __str__(self) -> str:
        return f"ConversationDetail(topic={self.topic!r}) for {self.event_id}"


class MoodDetail(models.Model):
    """1:1 satellite table for `Event.type == EventType.MOOD`."""

    event = models.OneToOneField(Event, on_delete=models.CASCADE, primary_key=True)
    label = models.CharField(max_length=64)
    intensity = models.SmallIntegerField(help_text="1..5")
    trigger = models.CharField(max_length=255, blank=True, default="")

    def __str__(self) -> str:
        return f"MoodDetail(label={self.label!r}) for {self.event_id}"


class JournalEntry(models.Model):
    """The raw daily narrative — never mutated after extraction; see docs/data-model.md."""

    class Source(models.TextChoices):
        VOICE = "voice", "Voice"
        TEXT = "text", "Text"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries"
    )
    entry_date = models.DateField()
    raw_text = models.TextField()
    source = models.CharField(max_length=8, choices=Source.choices, default=Source.TEXT)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-entry_date"]
        verbose_name_plural = "journal entries"

    def __str__(self) -> str:
        return f"JournalEntry({self.entry_date}) for {self.user_id}"
