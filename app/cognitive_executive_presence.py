from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.ambient_proactive_coordination import AmbientObservation, AmbientSignalKind
from app.conversational_self_analysis import ConversationalSelfAnalysisReport


class ExecutivePresencePriority(str, Enum):
    ROUTINE = "routine"
    IMPORTANT = "important"
    URGENT = "urgent"


@dataclass(frozen=True)
class ExecutivePresencePolicy:
    max_recent_interventions: int = 2

    def __post_init__(self) -> None:
        if self.max_recent_interventions < 1:
            raise ValueError("max recent interventions must be positive")


@dataclass(frozen=True)
class ExecutivePresenceAssessment:
    priority: ExecutivePresencePriority
    allow_comment: bool
    allow_visual_capture: bool
    rationale: str
    self_analysis_considered: bool


class CognitiveExecutivePresence:
    """Coordinates timing and restraint across existing companion signals."""

    def __init__(self, policy: ExecutivePresencePolicy | None = None) -> None:
        self.policy = policy or ExecutivePresencePolicy()

    def assess(
        self,
        observation: AmbientObservation,
        *,
        self_analysis: ConversationalSelfAnalysisReport | None = None,
        recent_interventions: int = 0,
    ) -> ExecutivePresenceAssessment:
        priority = self._priority_for(observation)
        repair_active = self_analysis is not None and any(
            finding.dimension in {"repair", "context"}
            for finding in self_analysis.findings
        )

        if priority is ExecutivePresencePriority.URGENT:
            return ExecutivePresenceAssessment(
                priority=priority,
                allow_comment=True,
                allow_visual_capture=True,
                rationale="urgent_household_signal_overrides_routine_restraint",
                self_analysis_considered=self_analysis is not None,
            )

        if repair_active:
            return ExecutivePresenceAssessment(
                priority=priority,
                allow_comment=False,
                allow_visual_capture=False,
                rationale="conversation_repair_has_current_executive_priority",
                self_analysis_considered=True,
            )

        if recent_interventions >= self.policy.max_recent_interventions:
            return ExecutivePresenceAssessment(
                priority=priority,
                allow_comment=False,
                allow_visual_capture=False,
                rationale="recent_intervention_budget_exhausted",
                self_analysis_considered=self_analysis is not None,
            )

        return ExecutivePresenceAssessment(
            priority=priority,
            allow_comment=True,
            allow_visual_capture=True,
            rationale="executive_presence_allows_low_intrusion_action",
            self_analysis_considered=self_analysis is not None,
        )

    @staticmethod
    def _priority_for(
        observation: AmbientObservation,
    ) -> ExecutivePresencePriority:
        if observation.kind is AmbientSignalKind.DISTRESS:
            return ExecutivePresencePriority.URGENT
        if observation.kind in {
            AmbientSignalKind.IMPACT,
            AmbientSignalKind.VISUAL_UNCERTAINTY,
        }:
            return ExecutivePresencePriority.IMPORTANT
        return ExecutivePresencePriority.ROUTINE
