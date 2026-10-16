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
class CapabilityExecution:
    capability_name: str
    request_text: str
    response_text: str
    rationale: str


@dataclass(frozen=True)
class CapabilityOrchestrationSnapshot:
    evaluations: int
    composed_turns: int
    last_capabilities: tuple[str, ...]
    last_clause_count: int


class UnifiedCapabilityOrchestrator:
    """Combines safe official capabilities before the provider fallback."""

    _SEPARATOR = re.compile(
        r"\s*(?:\n+|;|\by\s+(?:despues|tambien|ademas)\b|\bdespues\b|"
        r"\btambien\b|\bademas\b)\s*",
        flags=re.IGNORECASE,
    )

    def __init__(self, registry) -> None:
        self.registry = registry
        self._evaluations = 0
        self._composed_turns = 0
        self._last_capabilities: tuple[str, ...] = ()
        self._last_clause_count = 0

    def is_composed_request(self, text: str) -> bool:
        """Report whether the existing composition boundary sees multiple clauses."""
        return len(self._split_clauses(text)) > 1

    @property
    def snapshot(self) -> CapabilityOrchestrationSnapshot:
        return CapabilityOrchestrationSnapshot(
            evaluations=self._evaluations,
            composed_turns=self._composed_turns,
            last_capabilities=self._last_capabilities,
            last_clause_count=self._last_clause_count,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        clauses = self._split_clauses(request.text)
        self._evaluations += 1
        self._last_clause_count = len(clauses)
        self._last_capabilities = ()
        if len(clauses) < 2:
            return None

        executions: list[CapabilityExecution] = []
        for index, clause in enumerate(clauses):
            execution = self._execute_clause(request, clause, now)
            if execution is None:
                continue
            executions.append(execution)
            if self._provides_local_document_evidence(execution):
                reasoning = self._reason_over_surviving_clauses(
                    request,
                    evidence=execution,
                    clauses=clauses[index + 1 :],
                    now=now,
                )
                if reasoning is not None:
                    executions.append(reasoning)
                    break

        if not executions:
            return None

        self._last_capabilities = tuple(item.capability_name for item in executions)
        if len(executions) > 1:
            self._composed_turns += 1
        return GovernedOperationalInterception(
            response_text=self._merge(executions, len(clauses)),
            rationale="unified_capability_orchestration_completed",
        )

    def _execute_clause(
        self,
        original: GovernedConversationPipelineRequest,
        clause: str,
        now: datetime,
    ) -> CapabilityExecution | None:
        request = GovernedConversationPipelineRequest(
            owner=original.owner,
            session_id=original.session_id,
            text=clause,
        )
        semantic_routing = any(
            registration.descriptor.semantic_triggers
            for registration in self.registry.registrations
        )
        normalized = clause.casefold()
        for registration in self.registry.registrations:
            descriptor = registration.descriptor
            if semantic_routing and not any(
                trigger.strip().casefold() in normalized
                for trigger in descriptor.semantic_triggers
                if trigger.strip()
            ):
                continue
            if not descriptor.enabled or not self._safe_for_implicit_use(descriptor):
                continue
            result = self.registry.execute_registration(
                registration, request, now=now, origin="orchestrator"
            )
            if result is None:
                continue
            return CapabilityExecution(
                capability_name=descriptor.name,
                request_text=clause,
                response_text=result.response_text,
                rationale=result.rationale,
            )
        return None

    def _provides_local_document_evidence(
        self, execution: CapabilityExecution
    ) -> bool:
        for registration in self.registry.registrations:
            if registration.descriptor.name != execution.capability_name:
                continue
            return "local_document_content" in registration.descriptor.evidence_outputs
        return False

    def _reason_over_surviving_clauses(
        self,
        original: GovernedConversationPipelineRequest,
        *,
        evidence: CapabilityExecution,
        clauses: tuple[str, ...],
        now: datetime,
    ) -> CapabilityExecution | None:
        instructions = tuple(clause for clause in clauses if clause.strip())
        if not instructions:
            return None
        registration = next(
            (
                item
                for item in self.registry.registrations
                if item.descriptor.name == "reasoning.governed_runtime"
                and item.descriptor.enabled
            ),
            None,
        )
        if registration is None:
            return None
        evaluate_text = getattr(registration.interceptor, "evaluate_text", None)
        if not callable(evaluate_text):
            return None
        reasoning_text = "\n\n".join(
            (
                "Evidencia recuperada por la capacidad gobernada:",
                evidence.response_text,
                "Instrucciones sobrevivientes de la misma solicitud:",
                *instructions,
            )
        )
        result = evaluate_text(
            owner=original.owner,
            text=reasoning_text,
            now=now,
            observe_productive_intake=False,
        )
        status = getattr(result.status, "value", str(result.status))
        if status == "abstained":
            response = (
                "Evidencia local insuficiente para completar con seguridad "
                "las instrucciones restantes."
            )
        else:
            response = result.explanation.summary
        return CapabilityExecution(
            capability_name=registration.descriptor.name,
            request_text="\n\n".join(instructions),
            response_text=response,
            rationale=f"governed_reasoning_reentry:{status}",
        )

    @staticmethod
    def _safe_for_implicit_use(descriptor) -> bool:
        if descriptor.requires_confirmation:
            return False
        return descriptor.normalized_risk in {
            CapabilityRisk.LOW,
            CapabilityRisk.MEDIUM,
        }

    @classmethod
    def _split_clauses(cls, text: str) -> tuple[str, ...]:
        normalized = text.strip()
        if not normalized:
            return ()
        parts = tuple(
            part.strip(" ,.")
            for part in cls._SEPARATOR.split(normalized)
            if part.strip(" ,.")
        )
        return parts

    @staticmethod
    def _merge(
        executions: list[CapabilityExecution],
        clause_count: int,
    ) -> str:
        if len(executions) == 1:
            response = executions[0].response_text
            if clause_count > 1:
                return (
                    f"{response}\n\n"
                    "La otra parte de la solicitud no tuvo una capacidad "
                    "especializada disponible."
                )
            return response
        sections = []
        for execution in executions:
            title = execution.capability_name.replace(".", " ").strip().title()
            sections.append(f"{title}:\n{execution.response_text}")
        return "\n\n".join(sections)
