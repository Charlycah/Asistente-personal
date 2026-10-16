from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeAssociation,
    GovernedReasoningMethodOutcomeAssociationStatus,
)


class GovernedReasoningMethodEffectivenessAwarenessStatus(StrEnum):
    SUPPORTIVE_OBSERVED_RECORD = "supportive_observed_record"
    LIMITING_OBSERVED_RECORD = "limiting_observed_record"
    REVIEW_REQUIRED_OBSERVED_RECORD = "review_required_observed_record"
    MIXED_OBSERVED_RECORD = "mixed_observed_record"
    INSUFFICIENT_EVALUATIVE_EVIDENCE = "insufficient_evaluative_evidence"


@dataclass(frozen=True)
class GovernedReasoningMethodEffectivenessAwareness:
    awareness_id: str
    status: GovernedReasoningMethodEffectivenessAwarenessStatus
    method_fingerprint: str
    evaluation_scope: str
    source_association_id: str
    source_association_status: GovernedReasoningMethodOutcomeAssociationStatus
    observation_count: int
    adequate_count: int
    limited_count: int
    review_required_count: int
    sufficient_count: int
    insufficient_count: int
    indeterminate_count: int
    world_snapshot_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-reasoning-method-effectiveness-awareness-v1"
    )
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    derivational: bool = True
    consultative: bool = True
    evaluates_observed_support: bool = True
    evaluates_effectiveness: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    establishes_causality: bool = False
    attributes_outcome_to_method: bool = False
    establishes_global_effectiveness: bool = False
    compares_methods: bool = False
    establishes_method_superiority: bool = False
    assigns_probability: bool = False
    scores_methods: bool = False
    ranks_methods: bool = False
    selects_method: bool = False
    recommends_method: bool = False
    modifies_reasoning: bool = False
    reruns_reasoning: bool = False
    changes_reasoning_method: bool = False
    invokes_adaptive_reasoning: bool = False
    invokes_curiosity: bool = False
    invokes_reflection: bool = False
    creates_learning_candidate: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.awareness_id.startswith(
            "reasoning-method-effectiveness-awareness-"
        ):
            raise ValueError("method effectiveness awareness identifier is invalid")
        if not self.method_fingerprint.strip() or not self.evaluation_scope.strip():
            raise ValueError("method effectiveness awareness requires method and scope")
        if not self.source_association_id.startswith(
            "reasoning-method-outcome-association-"
        ):
            raise ValueError(
                "method effectiveness awareness requires association lineage"
            )
        if self.observation_count < 1:
            raise ValueError("method effectiveness awareness requires observations")
        if not self.rationale_codes or not self.source_fingerprint.strip():
            raise ValueError("method effectiveness awareness requires provenance")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("method effectiveness awareness must preserve authority")
        if not self.read_only or not self.derivational or not self.consultative:
            raise ValueError("method effectiveness awareness must remain read-only")
        if not self.evaluates_observed_support:
            raise ValueError(
                "method effectiveness awareness must evaluate observed support"
            )
        if any(
            (
                self.evaluates_effectiveness,
                self.establishes_truth,
                self.establishes_falsity,
                self.establishes_causality,
                self.attributes_outcome_to_method,
                self.establishes_global_effectiveness,
                self.compares_methods,
                self.establishes_method_superiority,
                self.assigns_probability,
                self.scores_methods,
                self.ranks_methods,
                self.selects_method,
                self.recommends_method,
                self.modifies_reasoning,
                self.reruns_reasoning,
                self.changes_reasoning_method,
                self.invokes_adaptive_reasoning,
                self.invokes_curiosity,
                self.invokes_reflection,
                self.creates_learning_candidate,
                self.persists_results,
                self.creates_memory,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("method effectiveness awareness violates governed limits")


class GovernedReasoningMethodEffectivenessAwarenessFoundationV1:
    """Interpret certified observed support without asserting effectiveness."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def assess(
        self,
        association: GovernedReasoningMethodOutcomeAssociation,
    ) -> GovernedReasoningMethodEffectivenessAwareness:
        self._validate_association(association)
        status, rationale = self._derive_status(association.status)
        source_fingerprint = sha256(
            repr(
                (
                    association.source_fingerprint,
                    status.value,
                    association.status.value,
                    association.observation_count,
                    association.adequate_count,
                    association.limited_count,
                    association.review_required_count,
                    association.sufficient_count,
                    association.insufficient_count,
                    association.indeterminate_count,
                    association.world_snapshot_ids,
                )
            ).encode("utf-8")
        ).hexdigest()
        identity_fingerprint = sha256(
            repr(
                (
                    "post-m409.1-reasoning-method-effectiveness-awareness-v1",
                    association.method_fingerprint,
                    association.source_reference,
                    association.association_id,
                    association.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedReasoningMethodEffectivenessAwareness(
            awareness_id=(
                "reasoning-method-effectiveness-awareness-"
                f"{identity_fingerprint[:24]}"
            ),
            status=status,
            method_fingerprint=association.method_fingerprint,
            evaluation_scope=association.source_reference,
            source_association_id=association.association_id,
            source_association_status=association.status,
            observation_count=association.observation_count,
            adequate_count=association.adequate_count,
            limited_count=association.limited_count,
            review_required_count=association.review_required_count,
            sufficient_count=association.sufficient_count,
            insufficient_count=association.insufficient_count,
            indeterminate_count=association.indeterminate_count,
            world_snapshot_ids=association.world_snapshot_ids,
            rationale_codes=rationale,
            source_fingerprint=source_fingerprint,
        )

    @classmethod
    def _validate_association(
        cls,
        association: GovernedReasoningMethodOutcomeAssociation,
    ) -> None:
        if association.canonical_authority != cls.CANONICAL_AUTHORITY:
            raise ValueError(
                "method effectiveness awareness requires reasoning authority"
            )
        if (
            not association.read_only
            or not association.derivational
            or not association.consultative
        ):
            raise ValueError(
                "method effectiveness awareness requires read-only association"
            )
        if not association.method_fingerprint.strip():
            raise ValueError("method effectiveness awareness requires method identity")
        if not association.source_reference.strip():
            raise ValueError("method effectiveness awareness requires evaluation scope")

    @staticmethod
    def _derive_status(
        source_status: GovernedReasoningMethodOutcomeAssociationStatus,
    ) -> tuple[
        GovernedReasoningMethodEffectivenessAwarenessStatus,
        tuple[str, ...],
    ]:
        status_type = GovernedReasoningMethodEffectivenessAwarenessStatus
        source_type = GovernedReasoningMethodOutcomeAssociationStatus
        mapping = {
            source_type.CONSISTENTLY_ADEQUATE: (
                status_type.SUPPORTIVE_OBSERVED_RECORD,
                (
                    "method_effectiveness:observed_record_supports_adequacy",
                    "method_effectiveness:support_is_scope_bound",
                    "method_effectiveness:support_is_not_causality",
                    "method_effectiveness:support_is_not_global_effectiveness",
                ),
            ),
            source_type.RECURRENT_LIMITATION: (
                status_type.LIMITING_OBSERVED_RECORD,
                (
                    "method_effectiveness:observed_record_indicates_limitation",
                    "method_effectiveness:limitation_is_scope_bound",
                    "method_effectiveness:limitation_is_not_causality",
                    "method_effectiveness:limitation_is_not_global_ineffectiveness",
                ),
            ),
            source_type.RECURRENT_REVIEW_REQUIRED: (
                status_type.REVIEW_REQUIRED_OBSERVED_RECORD,
                (
                    "method_effectiveness:observed_record_requires_review",
                    "method_effectiveness:review_is_not_ineffectiveness",
                    "method_effectiveness:review_is_scope_bound",
                    "method_effectiveness:review_does_not_invoke_reflection",
                ),
            ),
            source_type.MIXED: (
                status_type.MIXED_OBSERVED_RECORD,
                (
                    "method_effectiveness:observed_record_is_mixed",
                    "method_effectiveness:mixed_record_blocks_directional_claim",
                    "method_effectiveness:mixed_record_is_scope_bound",
                    "method_effectiveness:mixed_record_is_not_global_effectiveness",
                ),
            ),
            source_type.INSUFFICIENT_EVIDENCE: (
                status_type.INSUFFICIENT_EVALUATIVE_EVIDENCE,
                (
                    "method_effectiveness:insufficient_evaluative_evidence",
                    "method_effectiveness:no_support_inference",
                    "method_effectiveness:no_effectiveness_claim",
                ),
            ),
        }
        return mapping[source_status]
