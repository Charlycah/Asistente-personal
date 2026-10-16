from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProactivityKind(str, Enum):
    """Conservative next-step opportunities exposed by the Brain."""

    NONE = "none"
    WEATHER_FORECAST = "weather_forecast"
    CURRENT_AFFAIRS_SOURCES = "current_affairs_sources"


@dataclass(frozen=True)
class ProactivityDecision:
    kind: ProactivityKind
    suggestion: str | None = None

    @property
    def available(self) -> bool:
        return self.suggestion is not None


class ProactivityAnalyzer:
    """Suggest one bounded follow-up without executing it automatically."""

    def evaluate(self, *, response_text: str, rationale: str) -> ProactivityDecision:
        text = response_text.strip().casefold()
        normalized_rationale = rationale.strip().casefold()
        if not text or self._already_offers_next_step(text):
            return ProactivityDecision(kind=ProactivityKind.NONE)
        if normalized_rationale == "weather_completed":
            return ProactivityDecision(
                kind=ProactivityKind.WEATHER_FORECAST,
                suggestion="También puedo darte el pronóstico extendido.",
            )
        if normalized_rationale.startswith("current_affairs_web_retrieval_completed"):
            return ProactivityDecision(
                kind=ProactivityKind.CURRENT_AFFAIRS_SOURCES,
                suggestion="También puedo mostrarte las fuentes utilizadas.",
            )
        return ProactivityDecision(kind=ProactivityKind.NONE)

    @staticmethod
    def _already_offers_next_step(text: str) -> bool:
        return text.endswith("?") or any(
            marker in text
            for marker in (
                "también puedo",
                "si querés",
                "si quieres",
                "puedo darte",
                "puedo mostrarte",
            )
        )
