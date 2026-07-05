"""API surface for the AI layer. Mounted at /api/ai in chronos_backend/urls.py."""

from django.http import HttpRequest
from ninja import Router, Schema

from chronos_backend.accounts.models import User
from chronos_backend.events.models import Event, EventType, TaskStatus

from .gateway import GatewayNotConfigured
from .planner import PendingTask, plan_tomorrow

router = Router()


class TimeBlockOutSchema(Schema):
    start: str
    end: str
    activity: str
    reason: str


class DayPlanOutSchema(Schema):
    blocks: list[TimeBlockOutSchema]


class GatewayErrorSchema(Schema):
    detail: str


def _dev_user() -> User:
    user, _ = User.objects.get_or_create(
        username="dev",
        defaults={"timezone": "Europe/Berlin", "wake_time_default": "07:00"},
    )
    return user


def _pending_tasks_for(user: User) -> list[PendingTask]:
    events = Event.objects.filter(user=user, type=EventType.TASK).exclude(
        taskdetail__status=TaskStatus.DONE
    )
    return [
        PendingTask(
            title=event.title,
            estimated_minutes=event.taskdetail.estimated_minutes,
            importance=event.importance,
        )
        for event in events
    ]


@router.post(
    "/planner/tomorrow",
    response={200: DayPlanOutSchema, 503: GatewayErrorSchema},
)
def plan_tomorrow_view(request: HttpRequest):  # type: ignore[no-untyped-def]
    user = _dev_user()
    wake = str(user.wake_time_default or "07:00")
    sleep = str(user.sleep_time_default or "23:00")
    tasks = _pending_tasks_for(user)

    try:
        plan = plan_tomorrow(wake_time=wake, sleep_time=sleep, tasks=tasks)
    except GatewayNotConfigured as exc:
        return 503, GatewayErrorSchema(detail=str(exc))

    return 200, DayPlanOutSchema(
        blocks=[
            TimeBlockOutSchema(start=b.start, end=b.end, activity=b.activity, reason=b.reason)
            for b in plan.blocks
        ]
    )
