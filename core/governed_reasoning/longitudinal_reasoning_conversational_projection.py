from __future__ import annotations

from dataclasses import dataclass

from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessment,
    GovernedLongitudinalReasoningStatus,
)


@dataclass(frozen=True)
class GovernedLongitudinalReasoningConversationalProjection:
    """Bounded descriptive view of a canonical longitudinal assessment."""

    status: GovernedLongitudinalReasoningStatus
    episode_count: int
    conversation_context: str
    source_assessment_id: str
    source_reference: str
    source_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    derivational: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.status, GovernedLongitudinalReasoningStatus):
            raise ValueError("projection requires canonical longitudinal status")
        if self.episode_count <= 0:
            raise ValueError("projection requires positive episode support")
        if not self.conversation_context.strip():
            raise ValueError("projection requires bounded conversational context")
        if not self.source_assessment_id.startswith("longitudinal-reasoning-"):
            raise ValueError("projection requires canonical assessment lineage")
        if not self.source_reference.strip() or not self.source_fingerprint.strip():
            raise ValueError("projection requires source provenance")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("projection must preserve reasoning authority")
        if not self.read_only or not self.consultative or not self.derivational:
            raise ValueError("projection must remain derived and read-only")
        if any(
            (
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
            )
        ):
            raise ValueError("projection violates governed persistence limits")


class GovernedLongitudinalReasoningConversationalProjectorV1:
    """Project a canonical assessment into bounded descriptive conversation context."""

    _CONTEXT_BY_STATUS = {
        "insufficient_history": (
            "Comparable reasoning history is insufficient to establish a recurring "
            "assessment pattern."
        ),
        "consistently_adequate": (
            "Comparable reasoning assessments show a consistently adequate observed "
            "pattern; this does not establish correctness or truth."
        ),
        "recurrent_limitation": (
            "Comparable reasoning assessments show a recurrent limitation pattern; "
            "this is descriptive rather than a reasoning-failure claim."
        ),
        "recurrent_review_required": (
            "Comparable reasoning assessments carry a recurrent-review-required "
            "assessment state; this description does not grant review authority."
        ),
        "mixed": (
            "Comparable reasoning assessments show a mixed pattern without a "
            "directional or temporal conclusion."
        ),
    }

    def project(
        self,
        assessment: GovernedLongitudinalReasoningAssessment,
    ) -> GovernedLongitudinalReasoningConversationalProjection:
        if type(assessment) is not GovernedLongitudinalReasoningAssessment:
            raise TypeError("projection requires canonical longitudinal assessment")
        if assessment.canonical_authority != "governed_reasoning":
            raise ValueError("projection requires governed reasoning authority")
        if not assessment.read_only or not assessment.consultative:
            raise ValueError("projection requires read-only consultative source")
        if not assessment.derivational or assessment.persists_results:
            raise ValueError("projection requires derived nonpersistent source")

        conversation_context = self._CONTEXT_BY_STATUS[assessment.status.value]
        episode_count = len(assessment.source_reasoning_quality_assessment_ids)
        return GovernedLongitudinalReasoningConversationalProjection(
            status=assessment.status,
            episode_count=episode_count,
            conversation_context=conversation_context,
            source_assessment_id=assessment.assessment_id,
            source_reference=assessment.source_reference,
            source_fingerprint=assessment.source_fingerprint,
        )
