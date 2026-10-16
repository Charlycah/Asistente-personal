from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from core.capability_registry import CapabilityRisk
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class CognitiveDirection:
    situation: str
    requests: tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveCognitiveDirectorSnapshot:
    evaluations: int
    directed_turns: int
    executed_requests: int
    last_situation: str | None
    last_request_count: int


class ExecutiveCognitiveDirector:
    """Infers small, safe information needs from implicit user situations."""

    _EARLY_DEPARTURE = re.compile(
        r"\b(?:manana|mañana)\b.*\b(?:salir|irme|viajar)\b.*\btemprano\b|"
        r"\b(?:salir|irme|viajar)\b.*\btemprano\b.*\b(?:manana|mañana)\b",
        flags=re.IGNORECASE,
    )
    _TRAVEL = re.compile(
        r"\b(?:tengo que|voy a|debo)\s+(?:viajar|salir de viaje)\b",
        flags=re.IGNORECASE,
    )

    def __init__(self, registry) -> None:
        self.registry = registry
        self._evaluations = 0
        self._directed_turns = 0
        self._executed_requests = 0
        self._last_situation: str | None = None
        self._last_request_count = 0

    @property
    def snapshot(self) -> ExecutiveCognitiveDirectorSnapshot:
        return ExecutiveCognitiveDirectorSnapshot(
            evaluations=self._evaluations,
            directed_turns=self._directed_turns,
            executed_requests=self._executed_requests,
            last_situation=self._last_situation,
            last_request_count=self._last_request_count,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        self._evaluations += 1
        direction = self._direct(request.text)
        self._last_situation = direction.situation if direction else None
        self._last_request_count = len(direction.requests) if direction else 0
        if direction is None:
            return None

        responses: list[str] = []
        for inferred_request in direction.requests:
            result = self._execute_safe_request(request, inferred_request, now)
            if result is not None:
                responses.append(result.response_text)
                self._executed_requests += 1

        if not responses:
            return None

        self._directed_turns += 1
        return GovernedOperationalInterception(
            response_text=self._merge(direction.situation, responses),
            rationale="executive_cognitive_direction_completed",
        )

    def _direct(self, text: str) -> CognitiveDirection | None:
        normalized = " ".join(text.strip().split())
        if not normalized or self._looks_like_explicit_question(normalized):
            return None
        if self._EARLY_DEPARTURE.search(normalized):
            return CognitiveDirection(
                situation="salida_temprana",
                requests=(
                    "dame el pronostico para manana",
                    "que tengo hoy",
                ),
            )
        if self._TRAVEL.search(normalized):
            return CognitiveDirection(
                situation="viaje",
                requests=(
                    "dame el pronostico extendido",
                    "dame el resumen del dia",
                ),
            )
        return None

    def _execute_safe_request(
        self,
        original: GovernedConversationPipelineRequest,
        text: str,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        request = GovernedConversationPipelineRequest(
            owner=original.owner,
            session_id=original.session_id,
            text=text,
        )
        for registration in self.registry.registrations:
            descriptor = registration.descriptor
            if not descriptor.enabled or not self._safe_for_implicit_use(descriptor):
                continue
            result = self.registry.execute_registration(
                registration, request, now=now, origin="director"
            )
            if result is not None:
                return result
        return None

    @staticmethod
    def _looks_like_explicit_question(text: str) -> bool:
        normalized = text.casefold()
        if text.rstrip().endswith("?"):
            return True
        return normalized.startswith(
            (
                "como ",
                "cuando ",
                "donde ",
                "que ",
                "cual ",
                "decime ",
                "mostrame ",
                "recordame ",
            )
        )

    @staticmethod
    def _safe_for_implicit_use(descriptor) -> bool:
        if descriptor.requires_confirmation:
            return False
        return descriptor.normalized_risk in {
            CapabilityRisk.LOW,
            CapabilityRisk.MEDIUM,
        }

    @staticmethod
    def _merge(situation: str, responses: list[str]) -> str:
        introductions = {
            "salida_temprana": "Para esa salida temprana, revise lo relevante:",
            "viaje": "Para preparar el viaje, revise lo relevante:",
        }
        sections = [introductions.get(situation, "Revise lo relevante:")]
        sections.extend(responses)
        return "\n\n".join(sections)
