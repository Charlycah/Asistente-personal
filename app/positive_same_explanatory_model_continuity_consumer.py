from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.governed_reasoning.longitudinal_intellectual_identity import (
    GovernedLongitudinalIntellectualIdentityAssessment,
    LongitudinalIntellectualIdentityStatus,
)


class _ExplanatoryModel(Protocol):
    model_id: str


class _BoundedExplanatoryModelCandidate(Protocol):
    model: _ExplanatoryModel


@dataclass(frozen=True)
class PositiveSameExplanatoryModelContinuitySelection:
    """Transient selection of an exact bounded candidate already assessed SAME."""

    candidate_model_id: str
    assessment_id: str
    selection_status: str = "selected_continuous_prior"
    read_only: bool = True
    consultative: bool = True
    transient: bool = True
    persists: bool = False
    creates_learning: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    opens_investigation: bool = False
    authorizes_revision: bool = False
    creates_initiative: bool = False
    executes_actions: bool = False
    grants_authority: bool = False


class PositiveSameExplanatoryModelContinuityConsumerV1:
    """Select the exact bounded SAME candidate without granting new authority."""

    def consume(
        self,
        *,
        assessment: GovernedLongitudinalIntellectualIdentityAssessment,
        bounded_candidate: _BoundedExplanatoryModelCandidate,
    ) -> PositiveSameExplanatoryModelContinuitySelection | None:
        if assessment.status is not LongitudinalIntellectualIdentityStatus.SAME:
            return None

        candidate_model_id = bounded_candidate.model.model_id
        if assessment.candidate_artifact_reference != candidate_model_id:
            return None

        return PositiveSameExplanatoryModelContinuitySelection(
            candidate_model_id=candidate_model_id,
            assessment_id=assessment.assessment_id,
        )
