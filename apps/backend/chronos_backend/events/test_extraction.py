from chronos_backend.events.extraction import HeuristicExtractor
from chronos_backend.events.models import EventType


def test_extracts_mood_from_text() -> None:
    events = HeuristicExtractor().extract("Today was a terrible day, I felt so stressed.")
    types = [e.type for e in events]
    assert EventType.MOOD in types


def test_extracts_workout_mention() -> None:
    events = HeuristicExtractor().extract("Went for a great run this morning.")
    types = [e.type for e in events]
    assert EventType.WORKOUT in types
    assert EventType.MOOD in types  # "great" also triggers a mood event


def test_no_false_positive_on_neutral_text() -> None:
    events = HeuristicExtractor().extract("Reviewed the quarterly budget spreadsheet.")
    assert events == []
