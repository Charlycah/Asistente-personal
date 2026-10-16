from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityStatus,
)


class GovernedLongitudinalReasoningStatus(StrEnum):
    INSUFFICIENT_HISTORY = "insufficient_history"
    CONSISTENTLY_ADEQUATE = "consistently_adequate"
    RECURRENT_LIMITATION = "recurrent_limitation"
    RECURRENT_REVIEW_REQUIRED = "recurrent_review_required"
    MIXED = "mixed"


@dataclass(frozen=True)
class GovernedReasoningAssessmentObservation:
    """Neutral admitted episode view used by longitudinal reasoning."""

    quality_assessment_id: str
    quality_status: GovernedReasoningQualityStatus
    sufficiency_assessment_id: str
    sufficiency_status: EpistemicSufficiencyStatus
    source_reference: str
    world_snapshot_id: str
    quality_source_fingerprint: str
    sufficiency_source_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True

    def __post_init__(self) -> None:
        if not self.quality_assessment_id.startswith("reasoning-quality-"):
            raise ValueError("longitudinal observation quality identifier is invalid")
        if not self.sufficiency_assessment_id.startswith("epistemic-sufficiency-"):
            raise ValueError(
                "longitudinal observation sufficiency identifier is invalid"
            )
        if not isinstance(self.quality_status, GovernedReasoningQualityStatus):
            raise ValueError("longitudinal observation quality status is invalid")
        if not isinstance(self.sufficiency_status, EpistemicSufficiencyStatus):
            raise ValueError("longitudinal observation sufficiency status is invalid")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("longitudinal observation requires source lineage")
        if not self.quality_source_fingerprint.strip():
            raise ValueError("longitudinal observation requires quality fingerprint")
        if not self.sufficiency_source_fingerprint.strip():
            raise ValueError(
                "longitudinal observation requires sufficiency fingerprint"
            )
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "longitudinal observation must preserve reasoning authority"
            )
        if not self.read_only or not self.consultative:
            raise ValueError("longitudinal observation must remain read-only")

    @classmethod
    def from_assessments(
        cls,
        quality: GovernedReasoningQualityAssessment,
        sufficiency: GovernedEpistemicSufficiencyAssessment,
    ) -> GovernedReasoningAssessmentObservation:
        cls._validate_assessment_pair(quality, sufficiency)
        return cls(
            quality_assessment_id=quality.assessment_id,
            quality_status=quality.status,
            sufficiency_assessment_id=sufficiency.assessment_id,
            sufficiency_status=sufficiency.status,
            source_reference=quality.source_reference,
            world_snapshot_id=quality.world_snapshot_id,
            quality_source_fingerprint=quality.source_fingerprint,
            sufficiency_source_fingerprint=sufficiency.source_fingerprint,
        )

    @staticmethod
    def _validate_assessment_pair(
        quality: GovernedReasoningQualityAssessment,
        sufficiency: GovernedEpistemicSufficiencyAssessment,
    ) -> None:
        if quality.canonical_authority != "governed_reasoning":
            raise ValueError("longitudinal reasoning requires governed quality")
        if sufficiency.canonical_authority != "governed_reasoning":
            raise ValueError("longitudinal reasoning requires governed sufficiency")
        if not quality.read_only or not quality.consultative:
            raise ValueError("longitudinal reasoning requires read-only quality")
        if not sufficiency.read_only or not sufficiency.consultative:
            raise ValueError("longitudinal reasoning requires read-only sufficiency")
        if (
            quality.source_epistemic_sufficiency_assessment_id
            != sufficiency.assessment_id
        ):
            raise ValueError(
                "longitudinal reasoning quality/sufficiency lineage mismatch"
            )
        if quality.source_reference != sufficiency.source_reference:
            raise ValueError("longitudinal reasoning source lineage mismatch")
        if quality.world_snapshot_id != sufficiency.world_snapshot_id:
            raise ValueError("longitudinal reasoning snapshot lineage mismatch")
        if not quality.source_fingerprint.strip():
            raise ValueError("longitudinal reasoning requires quality fingerprint")
        if not sufficiency.source_fingerprint.strip():
            raise ValueError("longitudinal reasoning requires sufficiency fingerprint")


@dataclass(frozen=True)
class GovernedLongitudinalReasoningAssessment:
    assessment_id: str
    status: GovernedLongitudinalReasoningStatus
    source_reference: str
    source_reasoning_quality_assessment_ids: tuple[str, ...]
    source_epistemic_sufficiency_assessment_ids: tuple[str, ...]
    world_snapshot_ids: tuple[str, ...]
    adequate_count: int
    limited_count: int
    review_required_count: int
    sufficient_count: int
    insufficient_count: int
    indeterminate_count: int
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-longitudinal-reasoning-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    derivational: bool = True
    longitudinal: bool = True
    establishes_truth: bool = False
    establishes_falsity: bool = False
    assigns_probability: bool = False
    changes_reasoning: bool = False
    reruns_reasoning: bool = False
    authorizes_review: bool = False
    authorizes_stopping: bool = False
    invokes_reflection: bool = False
    invokes_learning: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_hypotheses: bool = False
    modifies_world_model: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id.startswith("longitudinal-reasoning-"):
            raise ValueError("longitudinal reasoning identifier is invalid")
        if not self.source_reference.strip():
            raise ValueError("longitudinal reasoning requires source reference")
        if not self.source_reasoning_quality_assessment_ids:
            raise ValueError("longitudinal reasoning requires quality lineage")
        if not self.source_epistemic_sufficiency_assessment_ids:
            raise ValueError("longitudinal reasoning requires sufficiency lineage")
        if not self.world_snapshot_ids:
            raise ValueError("longitudinal reasoning requires snapshot lineage")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("longitudinal reasoning requires rationale codes")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("longitudinal reasoning must preserve reasoning authority")
        if not self.read_only or not self.consultative or not self.derivational:
            raise ValueError("longitudinal reasoning must remain derived and read-only")
        if not self.longitudinal:
            raise ValueError("longitudinal reasoning must remain cross-episode")
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.assigns_probability,
                self.changes_reasoning,
                self.reruns_reasoning,
                self.authorizes_review,
                self.authorizes_stopping,
                self.invokes_reflection,
                self.invokes_learning,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_hypotheses,
                self.modifies_world_model,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("longitudinal reasoning violates governed limits")


class GovernedLongitudinalReasoningAssessmentFoundationV1:
    """Assess recurrence across an explicitly supplied comparable episode series."""

    CANONICAL_AUTHORITY = "governed_reasoning"
    MINIMUM_PATTERN_EPISODES = 2

    def assess(
        self,
        observations: tuple[GovernedReasoningAssessmentObservation, ...],
    ) -> GovernedLongitudinalReasoningAssessment:
        if not observations:
            raise ValueError("longitudinal reasoning requires explicit observations")

        for observation in observations:
            self._validate_observation(observation)
        self._validate_series(observations)

        ordered = tuple(
            sorted(
                observations,
                key=lambda item: (
                    item.quality_assessment_id,
                    item.sufficiency_assessment_id,
                ),
            )
        )
        counts = self._counts(ordered)
        status, rationale = self._derive_status(len(ordered), counts)
        return self._report(ordered, status=status, counts=counts, rationale=rationale)

    @staticmethod
    def _validate_observation(
        observation: GovernedReasoningAssessmentObservation,
    ) -> None:
        if observation.canonical_authority != "governed_reasoning":
            raise ValueError("longitudinal reasoning requires governed observation")
        if not observation.read_only or not observation.consultative:
            raise ValueError("longitudinal reasoning requires read-only observation")

    @staticmethod
    def _validate_series(
        observations: tuple[GovernedReasoningAssessmentObservation, ...],
    ) -> None:
        references = {item.source_reference for item in observations}
        if len(references) != 1:
            raise ValueError("longitudinal reasoning series is not comparable")

        quality_ids = [item.quality_assessment_id for item in observations]
        if len(set(quality_ids)) != len(quality_ids):
            raise ValueError("longitudinal reasoning repeats quality assessments")
        sufficiency_ids = [item.sufficiency_assessment_id for item in observations]
        if len(set(sufficiency_ids)) != len(sufficiency_ids):
            raise ValueError("longitudinal reasoning repeats sufficiency assessments")

    @staticmethod
    def _counts(
        observations: tuple[GovernedReasoningAssessmentObservation, ...],
    ) -> tuple[int, int, int, int, int, int]:
        quality_statuses = tuple(item.quality_status for item in observations)
        sufficiency_statuses = tuple(item.sufficiency_status for item in observations)
        return (
            quality_statuses.count(GovernedReasoningQualityStatus.ADEQUATE),
            quality_statuses.count(GovernedReasoningQualityStatus.LIMITED),
            quality_statuses.count(GovernedReasoningQualityStatus.REVIEW_REQUIRED),
            sufficiency_statuses.count(EpistemicSufficiencyStatus.SUFFICIENT),
            sufficiency_statuses.count(EpistemicSufficiencyStatus.INSUFFICIENT),
            sufficiency_statuses.count(EpistemicSufficiencyStatus.INDETERMINATE),
        )

    @classmethod
    def _derive_status(
        cls,
        episode_count: int,
        counts: tuple[int, int, int, int, int, int],
    ) -> tuple[GovernedLongitudinalReasoningStatus, tuple[str, ...]]:
        adequate, limited, review, _sufficient, _insufficient, _indeterminate = counts
        base = (
            "longitudinal:observed_assessment_pattern_only",
            "longitudinal:not_truth_promotion",
            "longitudinal:not_correctness_claim",
            "longitudinal:not_temporal_trend",
        )
        if episode_count < cls.MINIMUM_PATTERN_EPISODES:
            return (
                GovernedLongitudinalReasoningStatus.INSUFFICIENT_HISTORY,
                ("longitudinal:insufficient_episode_history",) + base,
            )
        if review >= cls.MINIMUM_PATTERN_EPISODES:
            return (
                GovernedLongitudinalReasoningStatus.RECURRENT_REVIEW_REQUIRED,
                ("longitudinal:recurrent_review_required_observed",) + base,
            )
        if limited >= cls.MINIMUM_PATTERN_EPISODES:
            return (
                GovernedLongitudinalReasoningStatus.RECURRENT_LIMITATION,
                (
                    "longitudinal:recurrent_limitation_observed",
                    "longitudinal:limitation_is_not_reasoning_failure",
                )
                + base,
            )
        if adequate == episode_count:
            return (
                GovernedLongitudinalReasoningStatus.CONSISTENTLY_ADEQUATE,
                ("longitudinal:all_supplied_episodes_adequate",) + base,
            )
        return (
            GovernedLongitudinalReasoningStatus.MIXED,
            ("longitudinal:mixed_assessment_history",) + base,
        )

    @staticmethod
    def _report(
        observations: tuple[GovernedReasoningAssessmentObservation, ...],
        *,
        status: GovernedLongitudinalReasoningStatus,
        counts: tuple[int, int, int, int, int, int],
        rationale: tuple[str, ...],
    ) -> GovernedLongitudinalReasoningAssessment:
        quality_ids = tuple(item.quality_assessment_id for item in observations)
        sufficiency_ids = tuple(item.sufficiency_assessment_id for item in observations)
        snapshot_ids = tuple(item.world_snapshot_id for item in observations)
        adequate, limited, review, sufficient, insufficient, indeterminate = counts
        source_reference = observations[0].source_reference
        fingerprint = sha256(
            repr(
                (
                    source_reference,
                    quality_ids,
                    sufficiency_ids,
                    snapshot_ids,
                    status.value,
                    counts,
                    rationale,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedLongitudinalReasoningAssessment(
            assessment_id=f"longitudinal-reasoning-{fingerprint[:24]}",
            status=status,
            source_reference=source_reference,
            source_reasoning_quality_assessment_ids=quality_ids,
            source_epistemic_sufficiency_assessment_ids=sufficiency_ids,
            world_snapshot_ids=snapshot_ids,
            adequate_count=adequate,
            limited_count=limited,
            review_required_count=review,
            sufficient_count=sufficient,
            insufficient_count=insufficient,
            indeterminate_count=indeterminate,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
        )
