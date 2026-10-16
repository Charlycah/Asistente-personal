from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.positive_same_explanatory_model_continuity_consumer import (
    PositiveSameExplanatoryModelContinuityConsumerV1,
    PositiveSameExplanatoryModelContinuitySelection,
)
from core.governed_reasoning.longitudinal_intellectual_identity import (
    GovernedLongitudinalIntellectualIdentityAssessment,
    GovernedLongitudinalIntellectualIdentityFoundationV1,
)


class _ExplanatoryModel(Protocol):
    model_id: str


class _ExplanatoryModelConsumption(Protocol):
    model: _ExplanatoryModel


class _BoundedExplanatoryModelGateway(Protocol):
    def productive_explanatory_model_consumption(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> _ExplanatoryModelConsumption | None: ...


@dataclass(frozen=True)
class LongitudinalIntellectualIdentityProductiveResultV1:
    assessment: GovernedLongitudinalIntellectualIdentityAssessment
    selection: PositiveSameExplanatoryModelContinuitySelection | None


class LongitudinalIntellectualIdentityProductiveAdapterV1:
    """Reach bounded resident models without extending the protected gateway."""

    def __init__(self, gateway: _BoundedExplanatoryModelGateway) -> None:
        self._gateway = gateway
        self._identity = GovernedLongitudinalIntellectualIdentityFoundationV1()
        self._continuity = PositiveSameExplanatoryModelContinuityConsumerV1()

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        candidate_turn_id: str,
        current_artifact_reference: str,
        identity_evidence_references: tuple[str, ...] = (),
        shared_intellectual_subject_evidence_references: tuple[str, ...] = (),
        directed_prior_state_evidence_references: tuple[str, ...] = (),
        relational_evidence_references: tuple[str, ...] = (),
    ) -> GovernedLongitudinalIntellectualIdentityAssessment | None:
        result = self.assess_and_select(
            owner=owner,
            session_id=session_id,
            candidate_turn_id=candidate_turn_id,
            current_artifact_reference=current_artifact_reference,
            identity_evidence_references=identity_evidence_references,
            shared_intellectual_subject_evidence_references=(
                shared_intellectual_subject_evidence_references
            ),
            directed_prior_state_evidence_references=(
                directed_prior_state_evidence_references
            ),
            relational_evidence_references=relational_evidence_references,
        )
        return None if result is None else result.assessment

    def assess_and_select(
        self,
        *,
        owner: str,
        session_id: str,
        candidate_turn_id: str,
        current_artifact_reference: str,
        identity_evidence_references: tuple[str, ...] = (),
        shared_intellectual_subject_evidence_references: tuple[str, ...] = (),
        directed_prior_state_evidence_references: tuple[str, ...] = (),
        relational_evidence_references: tuple[str, ...] = (),
    ) -> LongitudinalIntellectualIdentityProductiveResultV1 | None:
        bounded_candidate = self._gateway.productive_explanatory_model_consumption(
            owner=owner,
            session_id=session_id,
            turn_id=candidate_turn_id,
        )
        if bounded_candidate is None:
            return None

        assessment = self._identity.assess(
            current_artifact_reference=current_artifact_reference,
            candidate_artifact_reference=bounded_candidate.model.model_id,
            identity_evidence_references=identity_evidence_references,
            shared_intellectual_subject_evidence_references=(
                shared_intellectual_subject_evidence_references
            ),
            directed_prior_state_evidence_references=(
                directed_prior_state_evidence_references
            ),
            relational_evidence_references=relational_evidence_references,
        )
        selection = self._continuity.consume(
            assessment=assessment,
            bounded_candidate=bounded_candidate,
        )
        return LongitudinalIntellectualIdentityProductiveResultV1(
            assessment=assessment,
            selection=selection,
        )
