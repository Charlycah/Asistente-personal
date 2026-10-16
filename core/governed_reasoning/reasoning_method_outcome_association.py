from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)
from core.governed_reasoning.reasoning_method_provenance import (
    GovernedReasoningMethodProvenance,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityStatus,
)


class GovernedReasoningMethodOutcomeAssociationStatus(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CONSISTENTLY_ADEQUATE = "consistently_adequate"
    RECURRENT_LIMITATION = "recurrent_limitation"
    RECURRENT_REVIEW_REQUIRED = "recurrent_review_required"
    MIXED = "mixed"


@dataclass(frozen=True)
class GovernedReasoningMethodOutcomeObservation:
    observation_id: str
    method_provenance_id: str
    method_fingerprint: str
    quality_assessment_id: str
    quality_status: GovernedReasoningQualityStatus
    sufficiency_assessment_id: str
    sufficiency_status: EpistemicSufficiencyStatus
    source_reference: str
    world_snapshot_id: str
    method_source_fingerprint: str
    quality_source_fingerprint: str
    sufficiency_source_fingerprint: str
    source_fingerprint: str
    schema_version: str = "post-m409.1-reasoning-method-outcome-observation-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    derivational: bool = True
    consultative: bool = True

    def __post_init__(self) -> None:
        if not self.observation_id.startswith(
            "reasoning-method-outcome-observation-"
        ):
            raise ValueError(
                "reasoning method outcome observation identifier is invalid"
            )
        if (
            not self.method_provenance_id.strip()
            or not self.method_fingerprint.strip()
        ):
            raise ValueError(
                "reasoning method outcome observation requires method lineage"
            )
        if (
            not self.quality_assessment_id.strip()
            or not self.sufficiency_assessment_id.strip()
        ):
            raise ValueError(
                "reasoning method outcome observation requires outcome lineage"
            )
        if (
            not self.source_reference.strip()
            or not self.world_snapshot_id.strip()
        ):
            raise ValueError(
                "reasoning method outcome observation requires source lineage"
            )
        fingerprints = (
            self.method_source_fingerprint,
            self.quality_source_fingerprint,
            self.sufficiency_source_fingerprint,
            self.source_fingerprint,
        )
        if any(not item.strip() for item in fingerprints):
            raise ValueError(
                "reasoning method outcome observation requires fingerprints"
            )
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "reasoning method outcome observation must preserve authority"
            )
        if not self.read_only or not self.derivational or not self.consultative:
            raise ValueError(
                "reasoning method outcome observation must remain read-only"
            )

    @classmethod
    def from_artifacts(
        cls,
        method_provenance: GovernedReasoningMethodProvenance,
        quality: GovernedReasoningQualityAssessment,
        sufficiency: GovernedEpistemicSufficiencyAssessment,
    ) -> GovernedReasoningMethodOutcomeObservation:
        cls._validate_artifacts(method_provenance, quality, sufficiency)
        source_fingerprint = sha256(
            repr(
                (
                    method_provenance.provenance_id,
                    method_provenance.method_fingerprint,
                    quality.assessment_id,
                    quality.status.value,
                    sufficiency.assessment_id,
                    sufficiency.status.value,
                    quality.source_reference,
                    quality.world_snapshot_id,
                    method_provenance.source_fingerprint,
                    quality.source_fingerprint,
                    sufficiency.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        return cls(
            observation_id=(
                f"reasoning-method-outcome-observation-{source_fingerprint[:24]}"
            ),
            method_provenance_id=method_provenance.provenance_id,
            method_fingerprint=method_provenance.method_fingerprint,
            quality_assessment_id=quality.assessment_id,
            quality_status=quality.status,
            sufficiency_assessment_id=sufficiency.assessment_id,
            sufficiency_status=sufficiency.status,
            source_reference=quality.source_reference,
            world_snapshot_id=quality.world_snapshot_id,
            method_source_fingerprint=method_provenance.source_fingerprint,
            quality_source_fingerprint=quality.source_fingerprint,
            sufficiency_source_fingerprint=sufficiency.source_fingerprint,
            source_fingerprint=source_fingerprint,
        )

    @staticmethod
    def _validate_artifacts(
        method_provenance: GovernedReasoningMethodProvenance,
        quality: GovernedReasoningQualityAssessment,
        sufficiency: GovernedEpistemicSufficiencyAssessment,
    ) -> None:
        artifacts = (method_provenance, quality, sufficiency)
        if any(item.canonical_authority != "governed_reasoning" for item in artifacts):
            raise ValueError("method outcome observation requires reasoning authority")
        if any(not item.read_only or not item.consultative for item in artifacts):
            raise ValueError("method outcome observation requires read-only artifacts")
        if (
            quality.source_epistemic_sufficiency_assessment_id
            != sufficiency.assessment_id
        ):
            raise ValueError("method outcome quality/sufficiency lineage mismatch")
        if method_provenance.source_epistemic_sufficiency_assessment_id != (
            sufficiency.assessment_id
        ):
            raise ValueError("method outcome provenance/sufficiency lineage mismatch")
        if (
            method_provenance.source_reasoning_quality_assessment_id
            != quality.assessment_id
        ):
            raise ValueError("method outcome provenance/quality lineage mismatch")
        if len(
            {
                method_provenance.source_reference,
                quality.source_reference,
                sufficiency.source_reference,
            }
        ) != 1:
            raise ValueError("method outcome source lineage mismatch")
        if len(
            {
                method_provenance.world_snapshot_id,
                quality.world_snapshot_id,
                sufficiency.world_snapshot_id,
            }
        ) != 1:
            raise ValueError("method outcome snapshot lineage mismatch")
        if method_provenance.source_hypothesis_deepening_report_id != (
            quality.source_hypothesis_deepening_report_id
        ) or quality.source_hypothesis_deepening_report_id != (
            sufficiency.source_hypothesis_deepening_report_id
        ):
            raise ValueError("method outcome deepening lineage mismatch")
        if method_provenance.source_multi_hypothesis_discrimination_report_id != (
            quality.source_multi_hypothesis_discrimination_report_id
        ) or quality.source_multi_hypothesis_discrimination_report_id != (
            sufficiency.source_multi_hypothesis_discrimination_report_id
        ):
            raise ValueError("method outcome discrimination lineage mismatch")
        if method_provenance.source_hypothesis_update_semantics_report_id != (
            quality.source_hypothesis_update_semantics_report_id
        ) or quality.source_hypothesis_update_semantics_report_id != (
            sufficiency.source_hypothesis_update_semantics_report_id
        ):
            raise ValueError("method outcome update lineage mismatch")


@dataclass(frozen=True)
class GovernedReasoningMethodOutcomeAssociation:
    association_id: str
    status: GovernedReasoningMethodOutcomeAssociationStatus
    method_fingerprint: str
    source_reference: str
    observation_ids: tuple[str, ...]
    method_provenance_ids: tuple[str, ...]
    quality_assessment_ids: tuple[str, ...]
    sufficiency_assessment_ids: tuple[str, ...]
    world_snapshot_ids: tuple[str, ...]
    observation_count: int
    adequate_count: int
    limited_count: int
    review_required_count: int
    sufficient_count: int
    insufficient_count: int
    indeterminate_count: int
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-reasoning-method-outcome-association-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    derivational: bool = True
    consultative: bool = True
    establishes_truth: bool = False
    establishes_falsity: bool = False
    establishes_causality: bool = False
    assigns_probability: bool = False
    evaluates_effectiveness: bool = False
    compares_methods: bool = False
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
        if not self.association_id.startswith(
            "reasoning-method-outcome-association-"
        ):
            raise ValueError(
                "reasoning method outcome association identifier is invalid"
            )
        if (
            not self.method_fingerprint.strip()
            or not self.source_reference.strip()
        ):
            raise ValueError(
                "reasoning method outcome association requires comparison key"
            )
        if self.observation_count != len(self.observation_ids):
            raise ValueError("reasoning method outcome association count mismatch")
        if not self.rationale_codes or not self.source_fingerprint.strip():
            raise ValueError("reasoning method outcome association requires provenance")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "reasoning method outcome association must preserve authority"
            )
        if not self.read_only or not self.derivational or not self.consultative:
            raise ValueError(
                "reasoning method outcome association must remain read-only"
            )
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.establishes_causality,
                self.assigns_probability,
                self.evaluates_effectiveness,
                self.compares_methods,
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
            raise ValueError(
                "reasoning method outcome association violates governed limits"
            )


class GovernedReasoningMethodOutcomeAssociationFoundationV1:
    """Describe repeated epistemic outcomes under one explicit reasoning method."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def assess(
        self,
        observations: tuple[GovernedReasoningMethodOutcomeObservation, ...],
    ) -> GovernedReasoningMethodOutcomeAssociation:
        if not observations:
            raise ValueError(
                "method outcome association requires explicit observations"
            )
        ordered = tuple(sorted(observations, key=lambda item: item.observation_id))
        self._validate_series(ordered)

        adequate = sum(
            item.quality_status is GovernedReasoningQualityStatus.ADEQUATE
            for item in ordered
        )
        limited = sum(
            item.quality_status is GovernedReasoningQualityStatus.LIMITED
            for item in ordered
        )
        review = sum(
            item.quality_status is GovernedReasoningQualityStatus.REVIEW_REQUIRED
            for item in ordered
        )
        sufficient = sum(
            item.sufficiency_status is EpistemicSufficiencyStatus.SUFFICIENT
            for item in ordered
        )
        insufficient = sum(
            item.sufficiency_status is EpistemicSufficiencyStatus.INSUFFICIENT
            for item in ordered
        )
        indeterminate = sum(
            item.sufficiency_status is EpistemicSufficiencyStatus.INDETERMINATE
            for item in ordered
        )
        status, rationale = self._derive_status(
            len(ordered),
            adequate=adequate,
            limited=limited,
            review=review,
            sufficient=sufficient,
            insufficient=insufficient,
            indeterminate=indeterminate,
        )
        method_fingerprint = ordered[0].method_fingerprint
        source_reference = ordered[0].source_reference
        observation_ids = tuple(item.observation_id for item in ordered)
        method_ids = tuple(item.method_provenance_id for item in ordered)
        quality_ids = tuple(item.quality_assessment_id for item in ordered)
        sufficiency_ids = tuple(item.sufficiency_assessment_id for item in ordered)
        snapshot_ids = tuple(item.world_snapshot_id for item in ordered)
        source_fingerprint = sha256(
            repr(
                (
                    method_fingerprint,
                    source_reference,
                    tuple(item.source_fingerprint for item in ordered),
                    status.value,
                    adequate,
                    limited,
                    review,
                    sufficient,
                    insufficient,
                    indeterminate,
                )
            ).encode("utf-8")
        ).hexdigest()
        identity_fingerprint = sha256(
            repr(
                (
                    "post-m409.1-reasoning-method-outcome-association-v1",
                    method_fingerprint,
                    source_reference,
                    observation_ids,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedReasoningMethodOutcomeAssociation(
            association_id=(
                f"reasoning-method-outcome-association-{identity_fingerprint[:24]}"
            ),
            status=status,
            method_fingerprint=method_fingerprint,
            source_reference=source_reference,
            observation_ids=observation_ids,
            method_provenance_ids=method_ids,
            quality_assessment_ids=quality_ids,
            sufficiency_assessment_ids=sufficiency_ids,
            world_snapshot_ids=snapshot_ids,
            observation_count=len(ordered),
            adequate_count=adequate,
            limited_count=limited,
            review_required_count=review,
            sufficient_count=sufficient,
            insufficient_count=insufficient,
            indeterminate_count=indeterminate,
            rationale_codes=rationale,
            source_fingerprint=source_fingerprint,
        )

    @staticmethod
    def _validate_series(
        observations: tuple[GovernedReasoningMethodOutcomeObservation, ...],
    ) -> None:
        if len({item.method_fingerprint for item in observations}) != 1:
            raise ValueError("method outcome observations do not share one method")
        if len({item.source_reference for item in observations}) != 1:
            raise ValueError("method outcome observations are not source-comparable")
        identity_groups = (
            ("observation", tuple(item.observation_id for item in observations)),
            (
                "method provenance",
                tuple(item.method_provenance_id for item in observations),
            ),
            ("quality", tuple(item.quality_assessment_id for item in observations)),
            (
                "sufficiency",
                tuple(item.sufficiency_assessment_id for item in observations),
            ),
        )
        for label, identities in identity_groups:
            if len(set(identities)) != len(identities):
                raise ValueError(f"method outcome association repeats {label} ids")

    @staticmethod
    def _derive_status(
        count: int,
        *,
        adequate: int,
        limited: int,
        review: int,
        sufficient: int,
        insufficient: int,
        indeterminate: int,
    ) -> tuple[GovernedReasoningMethodOutcomeAssociationStatus, tuple[str, ...]]:
        if count < 2:
            return (
                GovernedReasoningMethodOutcomeAssociationStatus.INSUFFICIENT_EVIDENCE,
                (
                    "method_outcome:insufficient_evidence",
                    "method_outcome:not_effectiveness_claim",
                ),
            )
        if adequate == count and sufficient == count:
            return (
                GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
                (
                    "method_outcome:consistently_adequate_observed",
                    "method_outcome:not_truth_or_correctness_claim",
                    "method_outcome:not_effectiveness_claim",
                ),
            )
        if limited == count and insufficient == count:
            return (
                GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
                (
                    "method_outcome:recurrent_limitation_observed",
                    "method_outcome:limitation_is_not_method_failure",
                    "method_outcome:not_causal_claim",
                ),
            )
        if review == count and indeterminate == count:
            return (
                (
                    GovernedReasoningMethodOutcomeAssociationStatus
                    .RECURRENT_REVIEW_REQUIRED
                ),
                (
                    "method_outcome:recurrent_review_required_observed",
                    "method_outcome:does_not_authorize_review",
                    "method_outcome:not_causal_claim",
                ),
            )
        return (
            GovernedReasoningMethodOutcomeAssociationStatus.MIXED,
            (
                "method_outcome:mixed_outcomes_observed",
                "method_outcome:no_majority_inference",
                "method_outcome:not_effectiveness_claim",
            ),
        )
