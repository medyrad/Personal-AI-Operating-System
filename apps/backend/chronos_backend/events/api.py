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

from .models import Event, EventType, TaskDetail, TaskStatus

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
