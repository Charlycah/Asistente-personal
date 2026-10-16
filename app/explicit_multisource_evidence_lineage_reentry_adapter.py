from __future__ import annotations

from typing import Protocol

from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
)

from .explicit_multisource_productive_continuity_adapter import (
    ExplicitMultisourceProductiveContinuityV1,
)
from .governed_explanatory_model_revision import GovernedExplanatoryModelRevision
from .governed_level2_reasoning_reentry import GovernedLevel2ReasoningReentryResult


class ExplicitMultisourceEvidenceLineageRevisionConsumerV1(Protocol):
    """Existing revision consumer for governed evidence-lineage artifacts."""

    def bind_productive_explanatory_model_revision(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        source_turn_id: str,
        reentry: GovernedLevel2ReasoningReentryResult,
        revised_report: GovernedHypothesisDeepeningReport,
    ) -> GovernedExplanatoryModelRevision: ...


class ExplicitMultisourceEvidenceLineageReentryAdapterV1:
    """Deliver existing lineage artifacts to the existing revision consumer."""

    def deliver(
        self,
        *,
        continuity: ExplicitMultisourceProductiveContinuityV1,
        source_turn_id: str,
        reentry: GovernedLevel2ReasoningReentryResult,
        revised_report: GovernedHypothesisDeepeningReport,
        consumer: ExplicitMultisourceEvidenceLineageRevisionConsumerV1,
    ) -> GovernedExplanatoryModelRevision:
        if not source_turn_id.strip():
            raise ValueError("source_turn_id must be non-empty")
        return consumer.bind_productive_explanatory_model_revision(
            owner=continuity.owner,
            session_id=continuity.session_id,
            turn_id=continuity.turn_id,
            source_turn_id=source_turn_id,
            reentry=reentry,
            revised_report=revised_report,
        )
