from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from core.capability_registry import CapabilityRisk
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.governed_reasoning import GovernedReasoningStatus
from core.reasoning_runtime_integration import GovernedReasoningSource


@dataclass(frozen=True)
class CompanionSituation:
    kind: str
    subject: str
    requests: tuple[str, ...]


@dataclass(frozen=True)
class LivingCompanionSnapshot:
    evaluations: int
    accompanied_turns: int
    active_contexts: int
    executed_capabilities: tuple[str, ...]
    last_situation: str | None


class LivingCompanionRuntime:
    """Understands situations and coordinates safe companion context."""

    _IMPORTANT_MEETING = re.compile(
        r"\b(?:manana|mañana|hoy)\b.*\b(?:reunion|entrevista|turno)\b"
        r".*\b(?:importante|temprano)\b|"
        r"\b(?:reunion|entrevista|turno)\b.*\b(?:importante|temprano)\b",
        flags=re.IGNORECASE,
    )
    _TRAVEL = re.compile(
        r"\b(?:estoy preparando|estoy organizando|tengo que preparar)\b"
        r".*\b(?:viaje|salida)\b",
        flags=re.IGNORECASE,
    )
    _BUSY_DAY = re.compile(
        r"\b(?:tengo|se viene|va a ser)\b.*\b(?:dia|día)\b"
        r".*\b(?:complicado|ocupado|cargado)\b",
        flags=re.IGNORECASE,
    )

    _REASONING_CONFIDENCE_THRESHOLD = 0.75
    _GENERAL_SITUATION = re.compile(
        r"\b(?:preparaci[oó]n|organizaci[oó]n|coordinaci[oó]n)\b",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        registry,
        *,
        reasoning_source: GovernedReasoningSource | None = None,
    ) -> None:
        self.registry = registry
        self.reasoning_source = reasoning_source
        self._contexts: dict[tuple[str, str], CompanionSituation] = {}
        self._evaluations = 0
        self._accompanied_turns = 0
        self._executed_capabilities: tuple[str, ...] = ()
        self._last_situation: str | None = None

    @property
    def snapshot(self) -> LivingCompanionSnapshot:
        return LivingCompanionSnapshot(
            evaluations=self._evaluations,
            accompanied_turns=self._accompanied_turns,
            active_contexts=len(self._contexts),
            executed_capabilities=self._executed_capabilities,
            last_situation=self._last_situation,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        self._evaluations += 1
        self._executed_capabilities = ()
        situation = self._understand(request, now=now)
        self._last_situation = situation.kind if situation else None
        if situation is None:
            return None

        self._contexts[self._key(request)] = situation
        results: list[tuple[str, str]] = []
        for query in situation.requests:
            execution = self._execute_safe(request, query, now)
            if execution is not None:
                results.append(execution)

        if not results:
            return None

        self._accompanied_turns += 1
        self._executed_capabilities = tuple(name for name, _ in results)
        return GovernedOperationalInterception(
            response_text=self._respond(situation, results),
            rationale="living_companion_situation_accompanied",
        )

    def context_for(
        self,
        *,
        owner: str,
        session_id: str,
    ) -> CompanionSituation | None:
        return self._contexts.get(
            (owner.strip().casefold(), session_id.strip().casefold())
        )

    def _understand(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> CompanionSituation | None:
        normalized = " ".join(request.text.strip().split())
        if not normalized or self._explicit_question(normalized):
            return None
        if self._IMPORTANT_MEETING.search(normalized):
            return CompanionSituation(
                kind="important_commitment",
                subject="ese compromiso",
                requests=(
                    "dame el pronostico para manana",
                    "dame el resumen del dia",
                    "que recordatorios tengo",
                ),
            )
        if self._TRAVEL.search(normalized):
            return CompanionSituation(
                kind="travel_preparation",
                subject="el viaje",
                requests=(
                    "dame el pronostico extendido",
                    "que proyectos tenemos",
                    "que objetivos ejecutivos tengo",
                    "que recordatorios tengo",
                ),
            )
        if self._BUSY_DAY.search(normalized):
            return CompanionSituation(
                kind="busy_day",
                subject="el dia",
                requests=(
                    "dame el resumen del dia",
                    "como esta el clima",
                    "que recordatorios tengo",
                ),
            )
        return self._understand_from_reasoning(request, now=now)

    def _understand_from_reasoning(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> CompanionSituation | None:
        if self.reasoning_source is None:
            return None
        result = self.reasoning_source(
            owner=request.owner,
            session_id=request.session_id,
            text=request.text,
            now=now,
        )
        if result is None:
            return None
        if (
            GovernedReasoningStatus(result.status)
            is not GovernedReasoningStatus.COMPLETED
        ):
            return None
        if result.decision.confidence_score < self._REASONING_CONFIDENCE_THRESHOLD:
            return None
        conclusion = " ".join(result.decision.conclusion.strip().split())
        if not self._GENERAL_SITUATION.search(conclusion):
            return None
        return CompanionSituation(
            kind="general_situational_support",
            subject="la situacion",
            requests=(
                "dame el resumen del dia",
                "que recordatorios tengo",
            ),
        )

    def _execute_safe(self, original, text: str, now: datetime):
        request = GovernedConversationPipelineRequest(
            owner=original.owner,
            session_id=original.session_id,
            text=text,
        )
        for registration in self.registry.registrations:
            descriptor = registration.descriptor
            if not descriptor.enabled or not self._safe(descriptor):
                continue
            result = self.registry.execute_registration(
                registration, request, now=now, origin="companion"
            )
            if result is not None:
                return descriptor.name, result.response_text
        return None

    @staticmethod
    def _safe(descriptor) -> bool:
        return not descriptor.requires_confirmation and descriptor.normalized_risk in {
            CapabilityRisk.LOW,
            CapabilityRisk.MEDIUM,
        }

    @staticmethod
    def _respond(
        situation: CompanionSituation,
        results: list[tuple[str, str]],
    ) -> str:
        openings = {
            "important_commitment": "Revise lo importante para ese compromiso.",
            "travel_preparation": "Revise lo importante para el viaje.",
            "busy_day": "Ordene lo mas relevante para el dia.",
            "general_situational_support": (
                "Revise lo mas relevante para esa situacion."
            ),
        }
        sections = [openings[situation.kind]]
        seen: set[str] = set()
        for _, response in results:
            key = " ".join(response.casefold().split())
            if key in seen:
                continue
            seen.add(key)
            sections.append(response.strip())
        return "\n\n".join(sections)

    @staticmethod
    def _explicit_question(text: str) -> bool:
        normalized = text.strip().casefold()
        return text.rstrip().endswith("?") or normalized.startswith(
            ("como ", "que ", "cuando ", "donde ", "cual ", "cuanto ")
        )

    @staticmethod
    def _key(request: GovernedConversationPipelineRequest) -> tuple[str, str]:
        return (
            request.owner.strip().casefold(),
            request.session_id.strip().casefold(),
        )
