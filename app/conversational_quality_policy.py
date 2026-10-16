from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationalQualitySnapshot:
    evaluations: int
    self_references_removed: int
    contextual_weather_openings: int
    exact_times_restored: int
    robotic_closings_removed: int


class ConversationalQualityPolicy:
    """Improves final household phrasing without changing capability semantics."""

    _TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3])[:.]([0-5]\d)\b")
    _FULL_TIME_RE = re.compile(r"\b(?P<hour>[01]?\d|2[0-3])[:.](?P<minute>[0-5]\d)\b")
    _BAD_DAY_TERMS = (
        "feo día",
        "feo dia",
        "día feo",
        "dia feo",
        "día gris",
        "dia gris",
        "qué gris",
        "que gris",
    )
    _ROBOTIC_CLOSINGS = (
        "¿Necesitas algo más?",
        "¿Necesitás algo más?",
        "¿Hay algo más en lo que pueda ayudarte?",
    )

    def __init__(self) -> None:
        self._evaluations = 0
        self._self_references_removed = 0
        self._contextual_weather_openings = 0
        self._exact_times_restored = 0
        self._robotic_closings_removed = 0

    @property
    def snapshot(self) -> ConversationalQualitySnapshot:
        return ConversationalQualitySnapshot(
            evaluations=self._evaluations,
            self_references_removed=self._self_references_removed,
            contextual_weather_openings=self._contextual_weather_openings,
            exact_times_restored=self._exact_times_restored,
            robotic_closings_removed=self._robotic_closings_removed,
        )

    def apply(self, *, request_text: str, response_text: str) -> str:
        self._evaluations += 1
        adjusted = response_text.strip()
        adjusted = self._remove_identity_openers(adjusted)
        adjusted = self._contextualize_weather(request_text, adjusted)
        adjusted = self._restore_explicit_time(request_text, adjusted)
        adjusted = self._remove_robotic_closing(adjusted)
        return adjusted.strip()

    def _remove_identity_openers(self, text: str) -> str:
        adjusted, count = re.subn(
            r"(?is)^\s*como\s+roby\s*,?\s*(?:soy\s+consciente\s+de\s+que\s+)?",
            "",
            text,
            count=1,
        )
        self._self_references_removed += count
        if adjusted:
            adjusted = adjusted[0].upper() + adjusted[1:]
        return adjusted

    def _contextualize_weather(self, request_text: str, text: str) -> str:
        request = request_text.casefold()
        if not any(term in request for term in self._BAD_DAY_TERMS):
            return text
        match = re.match(
            r"(?is)^ahora\s+en\s+(?P<location>.+?)\s+está\s+"
            r"(?P<condition>nublado|muy nublado|algo nublado|cubierto)"
            r"(?P<rest>,\s+con\s+.+)$",
            text,
        )
        if match is None:
            return text
        condition = match.group("condition").casefold()
        if condition == "nublado":
            opening = "Sí, hoy está bastante nublado"
        elif condition == "algo nublado":
            opening = "Sí, hoy está algo nublado"
        elif condition == "cubierto":
            opening = "Sí, hoy está completamente cubierto"
        else:
            opening = "Sí, hoy está muy nublado"
        self._contextual_weather_openings += 1
        return f"{opening} en {match.group('location')}{match.group('rest')}"

    def _restore_explicit_time(self, request_text: str, text: str) -> str:
        requested = list(self._FULL_TIME_RE.finditer(request_text))
        rendered = list(self._FULL_TIME_RE.finditer(text))
        if len(requested) != 1 or len(rendered) != 1:
            return text
        requested_time = self._canonical_time(requested[0])
        rendered_time = self._canonical_time(rendered[0])
        if requested_time == rendered_time:
            return text
        self._exact_times_restored += 1
        return (
            text[: rendered[0].start()]
            + requested_time
            + text[rendered[0].end() :]
        )

    @staticmethod
    def _canonical_time(match: re.Match[str]) -> str:
        return f"{int(match.group('hour')):02d}:{match.group('minute')}"

    def _remove_robotic_closing(self, text: str) -> str:
        adjusted = text.rstrip()
        for closing in self._ROBOTIC_CLOSINGS:
            if adjusted.casefold().endswith(closing.casefold()):
                self._robotic_closings_removed += 1
                return adjusted[: -len(closing)].rstrip()
        return text
