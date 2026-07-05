"""First vertical slice API: create a task, list today's tasks, mark one complete.

Auth is intentionally deferred: every request operates against a single dev user that is
get-or-created on demand. Real auth (session or JWT, per the frozen stack decision) lands
in its own PR once there's more than one user of this API — see docs/adr/ once written.
"""

from datetime import datetime

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone as dj_timezone
from ninja import NinjaAPI, Schema

from chronos_backend.accounts.models import User

from .extraction import get_extractor
from .models import Event, EventType, JournalEntry, MoodDetail, TaskDetail, TaskStatus

api = NinjaAPI(title="Chronos API", version="0.1.0")


class TaskCreateSchema(Schema):
    title: str
    due_at: datetime | None = None
    estimated_minutes: int | None = None
    importance: int = 3


class TaskOutSchema(Schema):
    id: str
    title: str
    status: str
    occurred_at: datetime
    due_at: datetime | None = None
    estimated_minutes: int | None = None
    importance: int


def _dev_user() -> User:
    user, _ = User.objects.get_or_create(username="dev", defaults={"timezone": "Europe/Berlin"})
    return user


def _serialize(event: Event, detail: TaskDetail) -> TaskOutSchema:
    return TaskOutSchema(
        id=str(event.id),
        title=event.title,
        status=detail.status,
        occurred_at=event.occurred_at,
        due_at=detail.due_at,
        estimated_minutes=detail.estimated_minutes,
        importance=event.importance,
    )


@api.post("/events/tasks", response=TaskOutSchema)
def create_task(request: HttpRequest, payload: TaskCreateSchema) -> TaskOutSchema:
    user = _dev_user()
    event = Event.objects.create(
        user=user,
        type=EventType.TASK,
        occurred_at=dj_timezone.now(),
        title=payload.title,
        importance=payload.importance,
    )
    detail = TaskDetail.objects.create(
        event=event,
        due_at=payload.due_at,
        estimated_minutes=payload.estimated_minutes,
    )
    return _serialize(event, detail)


@api.get("/events/today", response=list[TaskOutSchema])
def list_today_tasks(request: HttpRequest) -> list[TaskOutSchema]:
    user = _dev_user()
    today = dj_timezone.localdate()
    events = (
        Event.objects.filter(user=user, type=EventType.TASK, occurred_at__date=today)
        .select_related("taskdetail")
        .order_by("occurred_at")
    )
    return [_serialize(event, event.taskdetail) for event in events]


@api.post("/events/tasks/{event_id}/complete", response=TaskOutSchema)
def complete_task(request: HttpRequest, event_id: str) -> TaskOutSchema:
    event = get_object_or_404(Event, id=event_id, type=EventType.TASK)
    detail = event.taskdetail
    detail.status = TaskStatus.DONE
    detail.save(update_fields=["status"])
    return _serialize(event, detail)


class JournalCreateSchema(Schema):
    raw_text: str


class ExtractedEventOutSchema(Schema):
    id: str
    type: str
    title: str
    mood_valence: int | None = None


class JournalOutSchema(Schema):
    id: str
    entry_date: str
    raw_text: str
    extracted_events: list[ExtractedEventOutSchema]


@api.post("/journal", response=JournalOutSchema)
def create_journal_entry(request: HttpRequest, payload: JournalCreateSchema) -> JournalOutSchema:
    user = _dev_user()
    now = dj_timezone.now()

    entry = JournalEntry.objects.create(
        user=user,
        entry_date=dj_timezone.localdate(),
        raw_text=payload.raw_text,
    )

    extracted = get_extractor().extract(payload.raw_text)
    created_events: list[Event] = []

    for item in extracted:
        event = Event.objects.create(
            user=user,
            type=item.type,
            occurred_at=now,
            title=item.title,
            mood_valence=item.mood_valence,
            source_journal_entry=entry,
        )
        if item.type == EventType.MOOD:
            MoodDetail.objects.create(
                event=event,
                label=item.mood_label or "",
                intensity=abs(item.mood_valence or 0) or 1,
            )
        created_events.append(event)

    entry.processed_at = dj_timezone.now()
    entry.save(update_fields=["processed_at"])

    return JournalOutSchema(
        id=str(entry.id),
        entry_date=entry.entry_date.isoformat(),
        raw_text=entry.raw_text,
        extracted_events=[
            ExtractedEventOutSchema(
                id=str(e.id), type=e.type, title=e.title, mood_valence=e.mood_valence
            )
            for e in created_events
        ],
    )
