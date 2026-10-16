from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeAssociation,
    GovernedReasoningMethodOutcomeAssociationStatus,
)


class GovernedComparativeReasoningMethodAwarenessStatus(StrEnum):
    INSUFFICIENT_COMPARATIVE_EVIDENCE = "insufficient_comparative_evidence"
    SAME_PATTERN = "same_pattern"
    DIFFERENT_PATTERN = "different_pattern"


@dataclass(frozen=True)
class GovernedComparativeReasoningMethodAwareness:
    awareness_id: str
    status: GovernedComparativeReasoningMethodAwarenessStatus
    source_reference: str
    association_ids: tuple[str, str]
    method_fingerprints: tuple[str, str]
    association_statuses: tuple[
        GovernedReasoningMethodOutcomeAssociationStatus,
        GovernedReasoningMethodOutcomeAssociationStatus,
    ]
    observation_counts: tuple[int, int]
    world_snapshot_ids: tuple[tuple[str, ...], tuple[str, ...]]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-comparative-reasoning-method-awareness-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    derivational: bool = True
    consultative: bool = True
    compares_methods: bool = True
    establishes_truth: bool = False
    establishes_falsity: bool = False
    establishes_causality: bool = False
    assigns_probability: bool = False
    evaluates_effectiveness: bool = False
    establishes_method_superiority: bool = False
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
            "comparative-reasoning-method-awareness-"
        ):
            raise ValueError("comparative method awareness identifier is invalid")
        if not self.source_reference.strip():
            raise ValueError("comparative method awareness requires source lineage")
        if len(set(self.association_ids)) != 2:
            raise ValueError("comparative method awareness requires two associations")
        if len(set(self.method_fingerprints)) != 2:
            raise ValueError("comparative method awareness requires distinct methods")
        if any(not item.strip() for item in self.method_fingerprints):
            raise ValueError(
                "comparative method awareness requires method fingerprints"
            )
        if any(count < 1 for count in self.observation_counts):
            raise ValueError("comparative method awareness requires observations")
        if not self.rationale_codes or not self.source_fingerprint.strip():
            raise ValueError("comparative method awareness requires provenance")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("comparative method awareness must preserve authority")
        if not self.read_only or not self.derivational or not self.consultative:
            raise ValueError("comparative method awareness must remain read-only")
        if not self.compares_methods:
            raise ValueError("comparative method awareness must compare methods")
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.establishes_causality,
                self.assigns_probability,
                self.evaluates_effectiveness,
                self.establishes_method_superiority,
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
            raise ValueError("comparative method awareness violates governed limits")


class GovernedComparativeReasoningMethodAwarenessFoundationV1:
    """Compare certified method/outcome patterns without evaluating methods."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def assess(
        self,
        associations: tuple[
            GovernedReasoningMethodOutcomeAssociation,
            GovernedReasoningMethodOutcomeAssociation,
        ],
    ) -> GovernedComparativeReasoningMethodAwareness:
        if len(associations) != 2:
            raise ValueError(
                "comparative method awareness requires exactly two associations"
            )
        ordered = tuple(
            sorted(
                associations,
                key=lambda item: (item.method_fingerprint, item.association_id),
            )
        )
        self._validate_associations(ordered)
        first, second = ordered
        status, rationale = self._derive_status(first.status, second.status)

        association_ids = (first.association_id, second.association_id)
        method_fingerprints = (first.method_fingerprint, second.method_fingerprint)
        association_statuses = (first.status, second.status)
        observation_counts = (first.observation_count, second.observation_count)
        world_snapshot_ids = (first.world_snapshot_ids, second.world_snapshot_ids)
        source_fingerprint = sha256(
            repr(
                (
                    first.source_fingerprint,
                    second.source_fingerprint,
                    status.value,
                    association_statuses[0].value,
                    association_statuses[1].value,
                    observation_counts,
                    world_snapshot_ids,
                )
            ).encode("utf-8")
        ).hexdigest()
        identity_fingerprint = sha256(
            repr(
                (
                    "post-m409.1-comparative-reasoning-method-awareness-v1",
                    first.source_reference,
                    association_ids,
                    method_fingerprints,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedComparativeReasoningMethodAwareness(
            awareness_id=(
                f"comparative-reasoning-method-awareness-"
                f"{identity_fingerprint[:24]}"
            ),
            status=status,
            source_reference=first.source_reference,
            association_ids=association_ids,
            method_fingerprints=method_fingerprints,
            association_statuses=association_statuses,
            observation_counts=observation_counts,
            world_snapshot_ids=world_snapshot_ids,
            rationale_codes=rationale,
            source_fingerprint=source_fingerprint,
        )

    @classmethod
    def _validate_associations(
        cls,
        associations: tuple[
            GovernedReasoningMethodOutcomeAssociation,
            GovernedReasoningMethodOutcomeAssociation,
        ],
    ) -> None:
        if any(
            item.canonical_authority != cls.CANONICAL_AUTHORITY
            for item in associations
        ):
            raise ValueError(
                "comparative method awareness requires reasoning authority"
            )
        if any(
            not item.read_only or not item.derivational or not item.consultative
            for item in associations
        ):
            raise ValueError(
                "comparative method awareness requires read-only associations"
            )
        if len({item.association_id for item in associations}) != 2:
            raise ValueError(
                "comparative method awareness requires distinct associations"
            )
        if len({item.method_fingerprint for item in associations}) != 2:
            raise ValueError("comparative method awareness requires distinct methods")
        if len({item.source_reference for item in associations}) != 1:
            raise ValueError(
                "comparative method awareness requires shared source reference"
            )

    @staticmethod
    def _derive_status(
        first: GovernedReasoningMethodOutcomeAssociationStatus,
        second: GovernedReasoningMethodOutcomeAssociationStatus,
    ) -> tuple[GovernedComparativeReasoningMethodAwarenessStatus, tuple[str, ...]]:
        insufficient = (
            GovernedReasoningMethodOutcomeAssociationStatus.INSUFFICIENT_EVIDENCE
        )
        if first is insufficient or second is insufficient:
            return (
                (
                    GovernedComparativeReasoningMethodAwarenessStatus
                    .INSUFFICIENT_COMPARATIVE_EVIDENCE
                ),
                (
                    "comparative_method:insufficient_comparative_evidence",
                    "comparative_method:no_difference_inference",
                    "comparative_method:not_effectiveness_claim",
                ),
            )
        if first is second:
            return (
                GovernedComparativeReasoningMethodAwarenessStatus.SAME_PATTERN,
                (
                    "comparative_method:same_categorical_pattern_observed",
                    "comparative_method:sameness_is_not_equivalence_claim",
                    "comparative_method:not_effectiveness_claim",
                ),
            )
        return (
            GovernedComparativeReasoningMethodAwarenessStatus.DIFFERENT_PATTERN,
            (
                "comparative_method:different_categorical_patterns_observed",
                "comparative_method:difference_is_not_causal_claim",
                "comparative_method:difference_is_not_superiority_claim",
            ),
        )
