"""Minimal RRULE interpretation — just enough to decide "is this routine due today".

A full RRULE parser (via `dateutil.rrule` or similar) is deferred until a routine
actually needs monthly/yearly recurrence — daily and weekly-by-day cover every routine
in the product vision's examples (morning workout, evening reading).
"""

import datetime

from .models import OccurrenceStatus, Routine, RoutineOccurrence

_WEEKDAY_CODES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def is_due_on(routine: Routine, date: datetime.date) -> bool:
    rule = routine.schedule_rule.upper()
    if "FREQ=DAILY" in rule:
        return True
    if "FREQ=WEEKLY" in rule and "BYDAY=" in rule:
        days_part = rule.split("BYDAY=")[1].split(";")[0]
        days = days_part.split(",")
        return _WEEKDAY_CODES[date.weekday()] in days
    return False


def ensure_occurrence_for(routine: Routine, date: datetime.date) -> RoutineOccurrence | None:
    """Idempotently creates today's occurrence if the routine is due and active."""
    if not routine.active or not is_due_on(routine, date):
        return None
    occurrence, _ = RoutineOccurrence.objects.get_or_create(
        routine=routine,
        expected_date=date,
        defaults={"status": OccurrenceStatus.PENDING},
    )
    return occurrence
