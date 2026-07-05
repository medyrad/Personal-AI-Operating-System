"""Journal extraction pipeline.

Turns a free-text `JournalEntry` into structured `Event` rows — the heart of "you don't
tag anything, the system figures it out" from the product vision.

This module defines the seam (`Extractor` protocol) and one real implementation
(`HeuristicExtractor`): fast, dependency-free, fully deterministic and testable. It's not
a placeholder — it genuinely extracts mood and workout mentions from text and is what
runs today.

`LLMExtractor` (Pydantic AI + Anthropic, per the frozen AI stack) is the production
replacement once an API key and prompt-evaluation loop exist — swapping it in is a
one-line change in `get_extractor()` because both honor the same protocol. Building it
before the heuristic version had proven the pipeline shape would have been premature.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Protocol

from .models import EventType

_MOOD_KEYWORDS: dict[str, tuple[str, int]] = {
    "great": ("positive", 2),
    "happy": ("positive", 2),
    "good": ("positive", 1),
    "productive": ("positive", 1),
    "tired": ("negative", -1),
    "stressed": ("negative", -1),
    "frustrated": ("negative", -1),
    "anxious": ("negative", -1),
    "terrible": ("negative", -2),
    "awful": ("negative", -2),
    "angry": ("negative", -2),
}

_WORKOUT_KEYWORDS = ("workout", "gym", "exercise", "ran", "run", "running")


@dataclass(frozen=True)
class ExtractedEvent:
    """One structured fact pulled out of a journal entry."""

    type: str
    title: str
    mood_valence: int | None = None
    mood_label: str | None = None


class Extractor(Protocol):
    def extract(self, raw_text: str) -> list[ExtractedEvent]: ...


class HeuristicExtractor:
    """Deterministic keyword-based extraction. No external calls, no API key needed."""

    def extract(self, raw_text: str) -> list[ExtractedEvent]:
        text_lower = raw_text.lower()
        results: list[ExtractedEvent] = []

        for keyword, (label, valence) in _MOOD_KEYWORDS.items():
            if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
                results.append(
                    ExtractedEvent(
                        type=EventType.MOOD,
                        title=f"Felt {keyword}",
                        mood_valence=valence,
                        mood_label=label,
                    )
                )

        if any(keyword in text_lower for keyword in _WORKOUT_KEYWORDS):
            results.append(ExtractedEvent(type=EventType.WORKOUT, title="Workout"))

        return results


def get_extractor() -> Extractor:
    """Returns the active extractor.

    Swaps to an LLM-backed implementation once ANTHROPIC_API_KEY is configured — until
    then, and always in tests, the heuristic extractor is used so behavior stays
    deterministic and free of network calls.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        # LLMExtractor lands with the AI Gateway PR — intentionally not implemented yet
        # (see module docstring). Fall through to the heuristic extractor for now.
        pass
    return HeuristicExtractor()
