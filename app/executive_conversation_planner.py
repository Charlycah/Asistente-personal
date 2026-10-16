from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from core.capability_registry import CapabilityRisk
from core.cognitive_maturity import PlanningDecisionEvidenceAdapter
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

from .runtime_capability_registry import PlanningCapabilityEvidence


@dataclass(frozen=True)
class ExecutivePlanStep:
    kind: str
    request_text: str
    depends_on: int | None = None
    condition: str | None = None


@dataclass(frozen=True)
class ExecutiveConversationPlan:
    steps: tuple[ExecutivePlanStep, ...]


@dataclass(frozen=True)
class ExecutivePlannerSnapshot:
    evaluations: int
    planned_turns: int
    executed_steps: int
    skipped_steps: int
    last_step_count: int


class ExecutiveConversationPlanner:
    """Build and execute small governed plans over official capabilities."""

    _CONDITIONAL = re.compile(
        r"^\s*(?P<query>.+?)\s*[,;.]?\s+si\s+(?P<condition>.+?)\s*[,;.]\s*"
        r"(?P<action>.+?)\s*$",
        flags=re.IGNORECASE,
    )
    _LEADING_CONDITIONAL = re.compile(
        r"^\s*si\s+(?P<condition>.+?)\s*[,;.]\s*(?P<action>.+?)\s*$",
        flags=re.IGNORECASE,
    )
    _ACTIONABLE_PREFIXES = (
        "recordame ",
        "recordarme ",
        "recordá ",
        "recorda ",
        "avisame ",
        "avisarme ",
        "avisá ",
        "avisa ",
        "creá ",
        "crea ",
        "agregá ",
        "agrega ",
        "añadí ",
        "anadí ",
        "anadi ",
        "enviá ",
        "envia ",
        "mandá ",
        "manda ",
        "activá ",
        "activa ",
        "desactivá ",
        "desactiva ",
        "abrí ",
        "abri ",
        "cerrá ",
        "cerra ",
        "programá ",
        "programa ",
        "agendá ",
        "agenda ",
    )
    _PERFORMATIVE_WRAPPER = re.compile(
        r"^¿?\s*(?:pod[eé]s|podr[ií]as)\s+(?P<request>.+?)\??\s*$",
        flags=re.IGNORECASE,
    )

    def __init__(self, registry) -> None:
        self.registry = registry
        self._evaluations = 0
        self._planned_turns = 0
        self._executed_steps = 0
        self._skipped_steps = 0
        self._last_step_count = 0

    @property
    def snapshot(self) -> ExecutivePlannerSnapshot:
        return ExecutivePlannerSnapshot(
            evaluations=self._evaluations,
            planned_turns=self._planned_turns,
            executed_steps=self._executed_steps,
            skipped_steps=self._skipped_steps,
            last_step_count=self._last_step_count,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        self._evaluations += 1
        plan = self._build_plan(request.text)
        self._last_step_count = len(plan.steps) if plan is not None else 0
        if plan is None:
            return None

        self._planned_turns += 1
        executed_before = self._executed_steps
        responses: list[str] = []
        outcomes: list[bool] = []
        for index, step in enumerate(plan.steps):
            if step.depends_on is not None:
                dependency_ok = outcomes[step.depends_on]
                if step.condition == "truthy" and not dependency_ok:
                    self._skipped_steps += 1
                    responses.append(
                        "No ejecute la accion condicionada porque la condicion "
                        "no se cumplio."
                    )
                    outcomes.append(False)
                    continue

            result = self._execute_step(request, step.request_text, now)
            if result is None:
                responses.append(
                    "No encontre una capacidad oficial segura para una parte del plan."
                )
                outcomes.append(False)
                continue

            self._executed_steps += 1
            responses.append(result.response_text)
            if index == 0 and step.kind == "condition":
                outcomes.append(self._condition_is_true(result.response_text))
            else:
                outcomes.append(True)

        PlanningDecisionEvidenceAdapter().observe_direct_plan(
            safe_step_executed=self._executed_steps > executed_before
        )
        return GovernedOperationalInterception(
            response_text="\n\n".join(responses),
            rationale="executive_conversation_plan_completed",
        )

    def _build_plan(self, text: str) -> ExecutiveConversationPlan | None:
        match = self._CONDITIONAL.match(text)
        if match is not None:
            query = match.group("query").strip(" ,.")
            condition = match.group("condition").strip(" ,.")
            action = match.group("action").strip(" ,.")
            if not self._is_actionable_consequent(action):
                return None
            condition_request = self._condition_request(query, condition)
            return ExecutiveConversationPlan(
                steps=(
                    ExecutivePlanStep("condition", condition_request),
                    ExecutivePlanStep(
                        "action",
                        action,
                        depends_on=0,
                        condition="truthy",
                    ),
                )
            )

        match = self._LEADING_CONDITIONAL.match(text)
        if match is None:
            return None
        condition = match.group("condition").strip(" ,.")
        action = match.group("action").strip(" ,.")
        if not self._is_actionable_consequent(action):
            return None
        return ExecutiveConversationPlan(
            steps=(
                ExecutivePlanStep("condition", condition),
                ExecutivePlanStep(
                    "action",
                    action,
                    depends_on=0,
                    condition="truthy",
                ),
            )
        )

    @classmethod
    def _is_actionable_consequent(cls, text: str) -> bool:
        normalized = text.strip().casefold().lstrip("¿¡")
        if normalized.startswith(cls._ACTIONABLE_PREFIXES):
            return True
        wrapper = cls._PERFORMATIVE_WRAPPER.match(text.strip())
        if wrapper is None:
            return False
        request = wrapper.group("request").strip().casefold().lstrip("¿¡")
        return request.startswith(cls._ACTIONABLE_PREFIXES)

    @staticmethod
    def _condition_request(query: str, condition: str) -> str:
        normalized = condition.casefold()
        if "lluev" in normalized or "lluvia" in normalized:
            return query
        return condition

    def _execute_step(
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
        for evidence in self.registry.planning_capability_evidence():
            if not evidence.enabled or not self._safe_for_implicit_use(evidence):
                continue
            registration = self.registry.registration_for(evidence.name)
            if registration is None:
                continue
            result = self.registry.execute_registration(
                registration, request, now=now, origin="planner"
            )
            if result is not None:
                return result
        return None

    @staticmethod
    def _safe_for_implicit_use(evidence: PlanningCapabilityEvidence) -> bool:
        if evidence.requires_confirmation:
            return False
        return evidence.risk in {
            CapabilityRisk.LOW,
            CapabilityRisk.MEDIUM,
        }

    @staticmethod
    def _condition_is_true(response_text: str) -> bool:
        normalized = response_text.casefold()
        if any(
            phrase in normalized
            for phrase in ("no va a llover", "sin lluvia", "lluvia 0%")
        ):
            return False
        percentages = re.findall(r"lluvia\s+(\d+)%", normalized)
        if percentages:
            return any(int(value) > 0 for value in percentages)
        return "llueve" in normalized or "lluvia" in normalized
