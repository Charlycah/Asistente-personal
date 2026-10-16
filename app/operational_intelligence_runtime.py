from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.executive_goal_manager import (
    ExecutiveGoalManager,
    ExecutiveGoalPriority,
    ExecutiveGoalStatus,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


class OperationalOutcome(str, Enum):
    SUCCESS = "success"
    DEGRADED = "degraded"
    FAILURE = "failure"


@dataclass(frozen=True)
class OperationalObservation:
    capability: str
    outcome: OperationalOutcome
    rationale: str
    observed_at: datetime


@dataclass(frozen=True)
class OperationalIntelligenceSnapshot:
    evaluations: int
    observed_results: int
    successes: int
    degradations: int
    failures: int
    active_conversations: int
    last_recommendation: str | None


class OperationalIntelligenceRuntime:
    """Learns from temporary operational outcomes without persistent mutation."""

    _STATUS_TRIGGERS = (
        "estado operativo",
        "como esta funcionando roby",
        "como viene funcionando roby",
        "resultado operativo",
    )
    _PRIORITY_TRIGGERS = (
        "que conviene priorizar",
        "cual es la prioridad ahora",
        "por donde conviene seguir",
        "que hacemos primero",
    )
    _MAX_HISTORY = 24

    def __init__(self, goal_manager: ExecutiveGoalManager) -> None:
        self.goal_manager = goal_manager
        self._history: dict[tuple[str, str], deque[OperationalObservation]] = {}
        self._evaluations = 0
        self._observed_results = 0
        self._successes = 0
        self._degradations = 0
        self._failures = 0
        self._last_recommendation: str | None = None

    @property
    def snapshot(self) -> OperationalIntelligenceSnapshot:
        return OperationalIntelligenceSnapshot(
            evaluations=self._evaluations,
            observed_results=self._observed_results,
            successes=self._successes,
            degradations=self._degradations,
            failures=self._failures,
            active_conversations=len(self._history),
            last_recommendation=self._last_recommendation,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        del now
        self._evaluations += 1
        normalized = self._normalize(request.text)
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._render_status(request),
                rationale="operational_intelligence_status_completed",
            )
        if any(trigger in normalized for trigger in self._PRIORITY_TRIGGERS):
            recommendation = self._recommend(request)
            self._last_recommendation = recommendation
            return GovernedOperationalInterception(
                response_text=recommendation,
                rationale="operational_intelligence_priority_recommended",
            )
        return None

    def observe_result(
        self,
        request: GovernedConversationPipelineRequest,
        result: GovernedOperationalInterception,
        *,
        now: datetime,
    ) -> None:
        rationale = result.rationale or "operational_result"
        if rationale.startswith("operational_intelligence_"):
            return
        outcome = self._classify(result)
        observation = OperationalObservation(
            capability=self._capability_from(rationale),
            outcome=outcome,
            rationale=rationale,
            observed_at=now,
        )
        history = self._history.setdefault(
            self._key(request),
            deque(maxlen=self._MAX_HISTORY),
        )
        history.append(observation)
        self._observed_results += 1
        if outcome is OperationalOutcome.SUCCESS:
            self._successes += 1
        elif outcome is OperationalOutcome.DEGRADED:
            self._degradations += 1
        else:
            self._failures += 1

    def observations_for(
        self,
        *,
        owner: str,
        session_id: str,
    ) -> tuple[OperationalObservation, ...]:
        key = (owner.strip().casefold(), session_id.strip().casefold())
        return tuple(self._history.get(key, ()))

    def _render_status(self, request: GovernedConversationPipelineRequest) -> str:
        history = self._history.get(self._key(request), ())
        if not history:
            return "Todavia no hay resultados operativos suficientes para evaluar."
        counts = Counter(item.outcome for item in history)
        repeated = self._repeated_degradation(history)
        lines = [
            "Estado operativo reciente:",
            f"- Resultados correctos: {counts[OperationalOutcome.SUCCESS]}.",
            f"- Degradaciones controladas: {counts[OperationalOutcome.DEGRADED]}.",
            f"- Fallos: {counts[OperationalOutcome.FAILURE]}.",
        ]
        if repeated is not None:
            lines.append(f"- Conviene revisar {repeated}: tuvo problemas repetidos.")
        else:
            lines.append("- No detecte problemas repetidos.")
        return "\n".join(lines)

    def _recommend(self, request: GovernedConversationPipelineRequest) -> str:
        goals = self.goal_manager.goals_for(
            owner=request.owner,
            session_id=request.session_id,
        )
        active = [goal for goal in goals if goal.status is ExecutiveGoalStatus.ACTIVE]
        if active:
            ranked = sorted(
                active,
                key=lambda goal: (
                    self._priority_rank(goal.priority),
                    goal.updated_at or goal.created_at,
                ),
                reverse=True,
            )
            goal = ranked[0]
            return (
                f"Conviene priorizar {goal.name}. El proximo paso es {goal.next_step}."
            )
        history = self._history.get(self._key(request), ())
        repeated = self._repeated_degradation(history)
        if repeated is not None:
            return f"Conviene revisar {repeated} antes de seguir agregando trabajo."
        return "No hay una prioridad operativa clara ahora."

    @staticmethod
    def _priority_rank(priority: ExecutiveGoalPriority) -> int:
        return {
            ExecutiveGoalPriority.LOW: 1,
            ExecutiveGoalPriority.MEDIUM: 2,
            ExecutiveGoalPriority.HIGH: 3,
        }[priority]

    @staticmethod
    def _classify(
        result: GovernedOperationalInterception,
    ) -> OperationalOutcome:
        text = result.response_text.casefold()
        rationale = (result.rationale or "").casefold()
        failure_terms = (
            "failure",
            "failed",
            "error",
            "no pudo completar",
            "no se pudo completar",
        )
        degraded_terms = (
            "degraded",
            "unavailable",
            "no esta disponible",
            "no respondio",
            "parcial",
        )
        if any(term in rationale or term in text for term in failure_terms):
            return OperationalOutcome.FAILURE
        if any(term in rationale or term in text for term in degraded_terms):
            return OperationalOutcome.DEGRADED
        return OperationalOutcome.SUCCESS

    @staticmethod
    def _capability_from(rationale: str) -> str:
        parts = rationale.split("_")
        ignored = {
            "completed",
            "intercepted",
            "executed",
            "response",
            "runtime",
        }
        useful = [part for part in parts if part and part not in ignored]
        return ".".join(useful[:3]) or "operacion"

    @staticmethod
    def _repeated_degradation(history) -> str | None:
        counts = Counter(
            item.capability
            for item in history
            if item.outcome
            in {
                OperationalOutcome.DEGRADED,
                OperationalOutcome.FAILURE,
            }
        )
        capability, count = counts.most_common(1)[0] if counts else (None, 0)
        return capability if capability is not None and count >= 2 else None

    @staticmethod
    def _key(
        request: GovernedConversationPipelineRequest,
    ) -> tuple[str, str]:
        return (
            request.owner.strip().casefold(),
            request.session_id.strip().casefold(),
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().casefold().split())
