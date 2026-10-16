from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from core.adaptive_cognition import (
    CoordinationStatus,
    ExecutiveCoordination,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest

ExecutiveCoordinationSource = Callable[..., ExecutiveCoordination | None]


@dataclass(frozen=True)
class ExecutiveCognitiveRuntimeContributor:
    """Project governed executive coordination into the current turn."""

    source: ExecutiveCoordinationSource
    name: str = "executive"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del request
        coordination = self.source(
            owner=owner,
            session_id=session_id,
            text=text,
            now=now,
        )
        if coordination is None:
            return self._skipped("executive_coordination_unavailable")
        if coordination.owner.casefold() != owner.casefold():
            raise ValueError("executive coordination owner must match runtime owner")

        status = coordination.normalized_status
        references = self._references(coordination)
        if coordination.requires_review:
            return self._skipped(
                "executive_coordination_requires_review",
                references,
            )
        if status not in {
            CoordinationStatus.APPROVED,
            CoordinationStatus.ACTIVE,
        }:
            return self._skipped(
                f"executive_coordination_{status.value}",
                references,
            )

        lines = [
            (
                "Coordinación ejecutiva gobernada: "
                f"estado {status.value}, revisión {coordination.revision}."
            ),
            (
                "Usar las directivas solo para coordinar la respuesta; "
                "no ejecutar herramientas, tareas ni acciones."
            ),
        ]
        if coordination.constraints:
            lines.append(
                "Restricciones ejecutivas: " + "; ".join(coordination.constraints)
            )
        for directive in coordination.directives[:8]:
            dependencies = ""
            if directive.dependencies:
                dependencies = (
                    f" Dependencias gobernadas: {len(directive.dependencies)}."
                )
            constraints = ""
            if directive.constraints:
                constraints = " Restricciones: " + "; ".join(directive.constraints)
            lines.append(
                "Directiva ejecutiva "
                f"{directive.sequence}: {directive.title}. "
                f"Subsistema {directive.normalized_subsystem.value}; "
                f"prioridad {directive.priority.value}; "
                f"estado {directive.normalized_status.value}."
                f"{dependencies}{constraints}"
            )

        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=tuple(lines),
            reference_ids=references,
            rationale=("executive_coordination_context_applied",),
        )

    def _references(
        self,
        coordination: ExecutiveCoordination,
    ) -> tuple[str, ...]:
        values = (
            coordination.coordination_id,
            coordination.plan_id,
            *(item.directive_id for item in coordination.directives),
            *(item.milestone_id for item in coordination.directives),
        )
        return tuple(dict.fromkeys(values))

    def _skipped(
        self,
        rationale: str,
        reference_ids: tuple[str, ...] = (),
    ) -> CognitiveRuntimeContribution:
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.SKIPPED,
            reference_ids=reference_ids,
            rationale=(rationale,),
        )
