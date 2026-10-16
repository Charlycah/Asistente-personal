from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from .prediction_outcome_evaluation import (
    PredictionOutcomeDisposition,
    PredictionOutcomeEvaluation,
)


class HistoricalPredictionReliabilityDisposition(StrEnum):
    SUPPORTED = "supported"
    MIXED = "mixed"
    LIMITED = "limited"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class HistoricalPredictionReliabilityAssessment:
    assessment_id: str
    scope: str
    disposition: HistoricalPredictionReliabilityDisposition | str
    total_count: int
    unique_count: int
    duplicate_count: int
    evaluable_count: int
    match_count: int
    mismatch_count: int
    unresolved_count: int
    review_count: int
    coverage: float
    match_ratio: float | None
    source_evaluation_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    match_ratio_is_descriptive: bool = True
    future_probability: float | None = None
    response_confidence_update: object | None = None
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    establishes_truth: bool = False
    calibrates_probability: bool = False
    modifies_response_confidence: bool = False
    modifies_prediction: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    persists_results: bool = False
    executes_actions: bool = False

    def __post_init__(self) -> None:
        scope = self.scope.strip()
        disposition = HistoricalPredictionReliabilityDisposition(self.disposition)
        if not scope:
            raise ValueError(
                "historical prediction reliability scope must not be blank"
            )
        if not self.assessment_id.startswith("historical-reliability-"):
            raise ValueError("historical reliability assessment id is invalid")
        counts = (
            self.total_count,
            self.unique_count,
            self.duplicate_count,
            self.evaluable_count,
            self.match_count,
            self.mismatch_count,
            self.unresolved_count,
            self.review_count,
        )
        if any(value < 0 for value in counts):
            raise ValueError("historical reliability counts must not be negative")
        if self.unique_count + self.duplicate_count != self.total_count:
            raise ValueError("historical reliability duplicate accounting is invalid")
        if self.match_count + self.mismatch_count != self.evaluable_count:
            raise ValueError("historical reliability evaluable accounting is invalid")
        if not 0.0 <= self.coverage <= 1.0:
            raise ValueError("historical reliability coverage must be bounded")
        if self.match_ratio is not None and not 0.0 <= self.match_ratio <= 1.0:
            raise ValueError("historical reliability match ratio must be bounded")
        if len(set(self.source_evaluation_ids)) != len(self.source_evaluation_ids):
            raise ValueError("historical reliability source ids must be unique")
        if not self.rationale_codes:
            raise ValueError("historical reliability requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("historical reliability must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                self.establishes_truth,
                self.calibrates_probability,
                self.modifies_response_confidence,
                self.modifies_prediction,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.persists_results,
                self.executes_actions,
            )
        ):
            raise ValueError("historical reliability violates governed limits")
        if not self.match_ratio_is_descriptive:
            raise ValueError("historical match ratio must remain descriptive")
        if self.future_probability is not None:
            raise ValueError("historical reliability cannot assert future probability")
        if self.response_confidence_update is not None:
            raise ValueError("historical reliability cannot update response confidence")
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "disposition", disposition)


class GovernedHistoricalPredictionReliabilityEvaluator:
    """Aggregate already-governed outcomes as read-only historical evidence."""

    CANONICAL_AUTHORITY = "governed_reasoning"
    MIN_EVALUABLE_SAMPLE = 5
    MIN_SUPPORTED_COVERAGE = 0.5
    SUPPORTED_MATCH_RATIO = 0.75

    def evaluate(
        self,
        *,
        scope: str,
        outcomes: tuple[PredictionOutcomeEvaluation, ...],
    ) -> HistoricalPredictionReliabilityAssessment:
        normalized_scope = scope.strip()
        if not normalized_scope:
            raise ValueError(
                "historical prediction reliability scope must not be blank"
            )

        unique, duplicate_count = self._deduplicate(outcomes)
        foreign_count = sum(
            not self._belongs_to_scope(item, normalized_scope) for item in unique
        )
        scoped = tuple(
            item for item in unique if self._belongs_to_scope(item, normalized_scope)
        )

        match_count = self._count(scoped, PredictionOutcomeDisposition.MATCH)
        mismatch_count = self._count(scoped, PredictionOutcomeDisposition.MISMATCH)
        unresolved_count = self._count(
            scoped,
            PredictionOutcomeDisposition.UNRESOLVED,
        )
        explicit_review_count = self._count(
            scoped,
            PredictionOutcomeDisposition.REVIEW,
        )
        review_count = explicit_review_count + foreign_count
        evaluable_count = match_count + mismatch_count
        unique_count = len(unique)
        coverage = evaluable_count / unique_count if unique_count else 0.0
        match_ratio = (
            match_count / evaluable_count if evaluable_count else None
        )

        disposition, rationale = self._classify(
            evaluable_count=evaluable_count,
            match_ratio=match_ratio,
            coverage=coverage,
            review_count=review_count,
            duplicate_count=duplicate_count,
        )

        source_ids = tuple(item.evaluation_id for item in unique)
        fingerprint = sha256(
            "|".join(
                (
                    normalized_scope,
                    disposition.value,
                    str(len(outcomes)),
                    str(unique_count),
                    str(duplicate_count),
                    str(evaluable_count),
                    str(match_count),
                    str(mismatch_count),
                    str(unresolved_count),
                    str(review_count),
                    f"{coverage:.6f}",
                    "none" if match_ratio is None else f"{match_ratio:.6f}",
                    *source_ids,
                    *rationale,
                )
            ).encode("utf-8")
        ).hexdigest()

        return HistoricalPredictionReliabilityAssessment(
            assessment_id=f"historical-reliability-{fingerprint[:16]}",
            scope=normalized_scope,
            disposition=disposition,
            total_count=len(outcomes),
            unique_count=unique_count,
            duplicate_count=duplicate_count,
            evaluable_count=evaluable_count,
            match_count=match_count,
            mismatch_count=mismatch_count,
            unresolved_count=unresolved_count,
            review_count=review_count,
            coverage=coverage,
            match_ratio=match_ratio,
            source_evaluation_ids=source_ids,
            rationale_codes=rationale,
        )

    @staticmethod
    def _deduplicate(
        outcomes: tuple[PredictionOutcomeEvaluation, ...],
    ) -> tuple[tuple[PredictionOutcomeEvaluation, ...], int]:
        by_id: dict[str, PredictionOutcomeEvaluation] = {}
        for item in outcomes:
            by_id.setdefault(item.evaluation_id, item)
        unique = tuple(by_id.values())
        return unique, len(outcomes) - len(unique)

    @staticmethod
    def _belongs_to_scope(
        item: PredictionOutcomeEvaluation,
        scope: str,
    ) -> bool:
        marker = f"prediction-{scope}-".casefold()
        return item.prediction_id.casefold().startswith(marker)

    @staticmethod
    def _count(
        outcomes: tuple[PredictionOutcomeEvaluation, ...],
        disposition: PredictionOutcomeDisposition,
    ) -> int:
        return sum(item.disposition is disposition for item in outcomes)

    def _classify(
        self,
        *,
        evaluable_count: int,
        match_ratio: float | None,
        coverage: float,
        review_count: int,
        duplicate_count: int,
    ) -> tuple[
        HistoricalPredictionReliabilityDisposition,
        tuple[str, ...],
    ]:
        if review_count:
            return (
                HistoricalPredictionReliabilityDisposition.REVIEW_REQUIRED,
                ("historical_reliability:review_or_scope_mismatch_present",),
            )
        if evaluable_count == 0:
            return (
                HistoricalPredictionReliabilityDisposition.INSUFFICIENT_EVIDENCE,
                ("historical_reliability:no_evaluable_outcomes",),
            )
        if evaluable_count < self.MIN_EVALUABLE_SAMPLE:
            return (
                HistoricalPredictionReliabilityDisposition.LIMITED,
                ("historical_reliability:evaluable_sample_too_small",),
            )
        if coverage < self.MIN_SUPPORTED_COVERAGE:
            return (
                HistoricalPredictionReliabilityDisposition.LIMITED,
                ("historical_reliability:evaluable_coverage_limited",),
            )
        if duplicate_count:
            return (
                HistoricalPredictionReliabilityDisposition.MIXED,
                ("historical_reliability:duplicates_excluded_from_evidence",),
            )
        if (
            match_ratio is not None
            and match_ratio >= self.SUPPORTED_MATCH_RATIO
        ):
            return (
                HistoricalPredictionReliabilityDisposition.SUPPORTED,
                (
                    "historical_reliability:observed_history_supported",
                    "historical_reliability:ratio_is_descriptive_not_probability",
                ),
            )
        return (
            HistoricalPredictionReliabilityDisposition.MIXED,
            ("historical_reliability:observed_history_is_mixed",),
        )
