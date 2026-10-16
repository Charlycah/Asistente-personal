from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.reasoning_method_effectiveness_awareness import (
    GovernedReasoningMethodEffectivenessAwareness,
    GovernedReasoningMethodEffectivenessAwarenessStatus,
)


class GovernedHistoricalReasoningMethodAdvisoryStatus(StrEnum):
    NO_APPLICABLE_HISTORY = "no_applicable_history"
    ONE_METHOD_SUPPORTED = "one_method_supported"
    METHOD_PREFERENCE_OBSERVED = "method_preference_observed"
    AMBIGUOUS = "ambiguous"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedHistoricalReasoningMethodAdvisory:
    advisory_id: str
    status: GovernedHistoricalReasoningMethodAdvisoryStatus
    evaluation_scope: str
    candidate_method_fingerprints: tuple[str, ...]
    recommended_method_fingerprint: str | None
    source_awareness_ids: tuple[str, ...]
    source_association_ids: tuple[str, ...]
    world_snapshot_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "cci-05-historical-reasoning-method-advisory-v1"
    canonical_authority: str = "governed_reasoning"
    consultative: bool = True
    recommends_method: bool = True
    application_authorized: bool = False
    selects_method: bool = False
    modifies_reasoning: bool = False
    reruns_reasoning: bool = False
    changes_reasoning_method: bool = False
    establishes_causality: bool = False
    establishes_method_superiority: bool = False
    establishes_global_effectiveness: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.advisory_id.startswith("historical-reasoning-method-advisory-"):
            raise ValueError("historical method advisory identifier is invalid")
        if not self.evaluation_scope.strip():
            raise ValueError("historical method advisory requires scope")
        if not self.rationale_codes or not self.source_fingerprint.strip():
            raise ValueError("historical method advisory requires provenance")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("historical method advisory must preserve authority")
        if not self.consultative or not self.recommends_method:
            raise ValueError("historical method advisory must remain consultative")
        if any(
            (
                self.application_authorized,
                self.selects_method,
                self.modifies_reasoning,
                self.reruns_reasoning,
                self.changes_reasoning_method,
                self.establishes_causality,
                self.establishes_method_superiority,
                self.establishes_global_effectiveness,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("historical method advisory violates governed limits")
        if (
            self.status
            in {
                AdvisoryStatus.ONE_METHOD_SUPPORTED,
                AdvisoryStatus.METHOD_PREFERENCE_OBSERVED,
            }
            and self.recommended_method_fingerprint is None
        ):
            raise ValueError("supportive advisory requires a recommendation")


AdvisoryStatus = GovernedHistoricalReasoningMethodAdvisoryStatus
AwarenessStatus = GovernedReasoningMethodEffectivenessAwarenessStatus


class GovernedHistoricalReasoningMethodAdvisoryV1:
    """Recommend, but never select, a method from compatible certified history."""

    CANONICAL_AUTHORITY = "governed_reasoning"
    MIN_OBSERVATIONS = 2

    def advise(
        self,
        awareness: tuple[GovernedReasoningMethodEffectivenessAwareness, ...],
        *,
        evaluation_scope: str,
        candidate_method_fingerprints: tuple[str, ...],
    ) -> GovernedHistoricalReasoningMethodAdvisory:
        scope = evaluation_scope.strip()
        candidates = tuple(sorted(set(candidate_method_fingerprints)))
        if not scope or not candidates or any(not item.strip() for item in candidates):
            raise ValueError("historical method advisory requires scope and candidates")

        applicable = tuple(
            item
            for item in awareness
            if item.evaluation_scope == scope
            and item.method_fingerprint in candidates
            and item.observation_count >= self.MIN_OBSERVATIONS
        )
        status, recommendation, rationale = self._derive(applicable)
        source_awareness_ids = tuple(item.awareness_id for item in applicable)
        source_association_ids = tuple(
            item.source_association_id for item in applicable
        )
        world_snapshot_ids = tuple(
            sorted({snap for item in applicable for snap in item.world_snapshot_ids})
        )
        source_fingerprint = sha256(
            repr(
                (
                    scope,
                    candidates,
                    tuple(item.source_fingerprint for item in applicable),
                    status.value,
                    recommendation,
                )
            ).encode("utf-8")
        ).hexdigest()
        identity = sha256(
            repr((scope, candidates, source_awareness_ids, source_fingerprint)).encode(
                "utf-8"
            )
        ).hexdigest()
        return GovernedHistoricalReasoningMethodAdvisory(
            advisory_id=f"historical-reasoning-method-advisory-{identity[:24]}",
            status=status,
            evaluation_scope=scope,
            candidate_method_fingerprints=candidates,
            recommended_method_fingerprint=recommendation,
            source_awareness_ids=source_awareness_ids,
            source_association_ids=source_association_ids,
            world_snapshot_ids=world_snapshot_ids,
            rationale_codes=rationale,
            source_fingerprint=source_fingerprint,
        )

    @staticmethod
    def _derive(
        applicable: tuple[GovernedReasoningMethodEffectivenessAwareness, ...],
    ) -> tuple[
        GovernedHistoricalReasoningMethodAdvisoryStatus,
        str | None,
        tuple[str, ...],
    ]:
        if not applicable:
            return (
                AdvisoryStatus.NO_APPLICABLE_HISTORY,
                None,
                ("historical_advisory:no_compatible_sufficient_history",),
            )
        if any(
            item.status
            is AwarenessStatus.REVIEW_REQUIRED_OBSERVED_RECORD
            for item in applicable
        ):
            return (
                AdvisoryStatus.REVIEW_REQUIRED,
                None,
                ("historical_advisory:review_required_history_present",),
            )
        supportive = tuple(
            item
            for item in applicable
            if item.status
            is AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD
        )
        if len(applicable) == 1 and len(supportive) == 1:
            return (
                AdvisoryStatus.ONE_METHOD_SUPPORTED,
                supportive[0].method_fingerprint,
                ("historical_advisory:one_supported_method_observed",),
            )
        if len(supportive) == 1:
            return (
                AdvisoryStatus.METHOD_PREFERENCE_OBSERVED,
                supportive[0].method_fingerprint,
                ("historical_advisory:bounded_preference_observed",),
            )
        return (
            AdvisoryStatus.AMBIGUOUS,
            None,
            ("historical_advisory:no_unique_supported_method",),
        )
