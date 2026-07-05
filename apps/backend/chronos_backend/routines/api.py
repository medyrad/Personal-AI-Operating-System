"""API surface for routines. Mounted at /api/routines in chronos_backend/urls.py."""

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone as dj_timezone
from ninja import Router, Schema

from chronos_backend.accounts.devuser import get_dev_user
from chronos_backend.events.models import Event, EventType

from .models import Routine, RoutineOccurrence
from .services import ensure_occurrence_for

router = Router()


class RoutineCreateSchema(Schema):
    name: str
    category: str = ""
    schedule_rule: str = "FREQ=DAILY"
    expected_duration_minutes: int | None = None


class RoutineOutSchema(Schema):
    id: str
    name: str
    category: str
    schedule_rule: str
    expected_duration_minutes: int | None = None
    active: bool


class OccurrenceOutSchema(Schema):
    id: str
    routine_id: str
    expected_date: str
    status: str
    skip_reason: str


class SkipSchema(Schema):
    reason: str


def _serialize_routine(routine: Routine) -> RoutineOutSchema:
    return RoutineOutSchema(
        id=str(routine.id),
        name=routine.name,
        category=routine.category,
        schedule_rule=routine.schedule_rule,
        expected_duration_minutes=routine.expected_duration_minutes,
        active=routine.active,
    )


def _serialize_occurrence(occurrence: RoutineOccurrence) -> OccurrenceOutSchema:
    return OccurrenceOutSchema(
        id=str(occurrence.id),
        routine_id=str(occurrence.routine_id),
        expected_date=occurrence.expected_date.isoformat(),
        status=occurrence.status,
        skip_reason=occurrence.skip_reason,
    )


@router.post("/", response=RoutineOutSchema)
def create_routine(request: HttpRequest, payload: RoutineCreateSchema) -> RoutineOutSchema:
    routine = Routine.objects.create(user=get_dev_user(), **payload.dict())
    return _serialize_routine(routine)


@router.get("/", response=list[RoutineOutSchema])
def list_routines(request: HttpRequest) -> list[RoutineOutSchema]:
    routines = Routine.objects.filter(user=get_dev_user(), active=True)
    return [_serialize_routine(r) for r in routines]


@router.post("/{routine_id}/today", response=OccurrenceOutSchema | None)
def ensure_today(request: HttpRequest, routine_id: str):  # type: ignore[no-untyped-def]
    routine = get_object_or_404(Routine, id=routine_id, user=get_dev_user())
    occurrence = ensure_occurrence_for(routine, dj_timezone.localdate())
    return _serialize_occurrence(occurrence) if occurrence else None


@router.post("/occurrences/{occurrence_id}/fulfill", response=OccurrenceOutSchema)
def fulfill_occurrence(request: HttpRequest, occurrence_id: str) -> OccurrenceOutSchema:
    occurrence = get_object_or_404(
        RoutineOccurrence, id=occurrence_id, routine__user=get_dev_user()
    )
    event = Event.objects.create(
        user=get_dev_user(),
        type=EventType.HABIT_CHECK,
        occurred_at=dj_timezone.now(),
        title=occurrence.routine.name,
        routine_occurrence=occurrence,
    )
    occurrence.status = "fulfilled"
    occurrence.fulfilling_event = event
    occurrence.save(update_fields=["status", "fulfilling_event"])
    return _serialize_occurrence(occurrence)


@router.post("/occurrences/{occurrence_id}/skip", response=OccurrenceOutSchema)
def skip_occurrence(
    request: HttpRequest, occurrence_id: str, payload: SkipSchema
) -> OccurrenceOutSchema:
    occurrence = get_object_or_404(
        RoutineOccurrence, id=occurrence_id, routine__user=get_dev_user()
    )
    occurrence.status = "skipped"
    occurrence.skip_reason = payload.reason
    occurrence.save(update_fields=["status", "skip_reason"])
    return _serialize_occurrence(occurrence)
