from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.causal_prediction import (
    CausalPredictionStatus,
    GovernedCausalPredictionReport,
    PredictiveOutcomeKind,
)


class GovernedPredictionStatus(StrEnum):
    COMPLETE = "complete"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


class GovernedPredictionDisposition(StrEnum):
    CONDITIONALLY_SUPPORTED = "conditionally_supported"
    CURRENTLY_CONTRADICTED = "currently_contradicted"
    UNRESOLVED = "unresolved"
    REVIEW = "review"


@dataclass(frozen=True)
class GovernedPredictionRequest:
    prediction_id: str
    relation_id: str
    horizon_code: str
    condition_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, label in (
            (self.prediction_id, "prediction id"),
            (self.relation_id, "relation id"),
            (self.horizon_code, "horizon code"),
        ):
            if not value.strip():
                raise ValueError(f"governed prediction {label} must not be blank")
        if any(not code.strip() for code in self.condition_codes):
            raise ValueError("prediction condition codes must not be blank")


@dataclass(frozen=True)
class GovernedPredictionAssessment:
    prediction_id: str
    relation_id: str
    horizon_code: str
    disposition: GovernedPredictionDisposition
    predicted_domain: str | None
    predicted_key: str | None
    predicted_value: str | None
    condition_codes: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    epistemic_level: EpistemicLevel = EpistemicLevel.INFERENCE
    is_future_fact: bool = False
    probability_calibrated: bool = False
    outcome_verified: bool = False

    def __post_init__(self) -> None:
        if not self.prediction_id.strip() or not self.relation_id.strip():
            raise ValueError("prediction assessment identifiers must not be blank")
        if not self.horizon_code.strip():
            raise ValueError("prediction assessment horizon must not be blank")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("prediction assessment requires rationale codes")
        if self.epistemic_level is not EpistemicLevel.INFERENCE:
            raise ValueError("governed predictions must remain inferences")
        if self.is_future_fact:
            raise ValueError("governed predictions cannot become future facts")
        if self.probability_calibrated:
            raise ValueError("M391.7 does not calibrate probability")
        if self.outcome_verified:
            raise ValueError("M391.7 does not verify future outcomes")


@dataclass(frozen=True)
class GovernedPredictionReport:
    report_id: str
    status: GovernedPredictionStatus
    source_analysis_id: str
    assessments: tuple[GovernedPredictionAssessment, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m391.7"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    creates_facts: bool = False
    calibrates_probability: bool = False
    verifies_outcomes: bool = False
    persists_results: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    modifies_decision: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("governed-prediction-"):
            raise ValueError("governed prediction report id is invalid")
        if not self.source_analysis_id.strip():
            raise ValueError("prediction source analysis is required")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("governed reasoning authority must be preserved")
        ids = tuple(item.prediction_id for item in self.assessments)
        if len(ids) != len(set(ids)):
            raise ValueError("prediction assessment ids must be unique")
        if any(
            (
                not self.read_only,
                self.creates_facts,
                self.calibrates_probability,
                self.verifies_outcomes,
                self.persists_results,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_planning,
                self.modifies_decision,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("governed prediction violates governed limits")


class GovernedPredictionEvaluator:
    """Pure prediction evaluation subordinate to governed reasoning authority."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def evaluate(
        self,
        source: GovernedCausalPredictionReport,
        requests: tuple[GovernedPredictionRequest, ...],
    ) -> GovernedPredictionReport:
        self._validate_unique_requests(requests)
        ordered = tuple(sorted(requests, key=lambda item: item.prediction_id))
        assessments = tuple(self._assess(source, item) for item in ordered)
        status = self._status(source, assessments)
        evidence_codes = tuple(
            dict.fromkeys(
                (
                    f"causal_prediction:{source.analysis_id}",
                    *source.evidence_codes,
                    *(code for item in ordered for code in item.condition_codes),
                    *(
                        code
                        for item in assessments
                        for code in item.rationale_codes
                    ),
                )
            )
        )
        risk_codes = tuple(
            dict.fromkeys(
                (
                    *source.risk_codes,
                    "prediction_not_fact",
                    "probability_not_calibrated",
                    *(
                        "prediction_review_required"
                        for item in assessments
                        if item.disposition is GovernedPredictionDisposition.REVIEW
                    ),
                    *(
                        "prediction_evidence_insufficient"
                        for item in assessments
                        if item.disposition
                        is GovernedPredictionDisposition.UNRESOLVED
                    ),
                )
            )
        )
        fingerprint = self._fingerprint(source, ordered, assessments)
        return GovernedPredictionReport(
            report_id=f"governed-prediction-{fingerprint[:16]}",
            status=status,
            source_analysis_id=source.analysis_id,
            assessments=assessments,
            evidence_codes=evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    def evaluate_safely(
        self,
        source: GovernedCausalPredictionReport,
        requests: tuple[GovernedPredictionRequest, ...],
    ) -> GovernedPredictionReport:
        try:
            return self.evaluate(source, requests)
        except Exception:
            fingerprint = sha256(source.analysis_id.encode("utf-8")).hexdigest()
            return GovernedPredictionReport(
                report_id=f"governed-prediction-{fingerprint[:16]}",
                status=GovernedPredictionStatus.DEGRADED,
                source_analysis_id=source.analysis_id,
                assessments=(),
                evidence_codes=(f"causal_prediction:{source.analysis_id}",),
                risk_codes=("governed_prediction_failure",),
                source_fingerprint=fingerprint,
            )

    @staticmethod
    def _validate_unique_requests(
        requests: tuple[GovernedPredictionRequest, ...],
    ) -> None:
        ids = tuple(item.prediction_id for item in requests)
        if len(ids) != len(set(ids)):
            raise ValueError("prediction request ids must be unique")

    @staticmethod
    def _assess(
        source: GovernedCausalPredictionReport,
        request: GovernedPredictionRequest,
    ) -> GovernedPredictionAssessment:
        prediction = next(
            (
                item
                for item in source.predictions
                if item.relation_id == request.relation_id
            ),
            None,
        )
        if prediction is None:
            return GovernedPredictionAssessment(
                prediction_id=request.prediction_id,
                relation_id=request.relation_id,
                horizon_code=request.horizon_code,
                disposition=GovernedPredictionDisposition.REVIEW,
                predicted_domain=None,
                predicted_key=None,
                predicted_value=None,
                condition_codes=request.condition_codes,
                rationale_codes=("prediction:source_relation_missing",),
            )

        if prediction.kind is PredictiveOutcomeKind.CONDITIONALLY_EXPECTED:
            disposition = GovernedPredictionDisposition.CONDITIONALLY_SUPPORTED
            rationale = (
                "prediction:conditionally_supported_by_m391_4",
                "prediction:horizon_is_explicit_not_inferred",
                "prediction:not_a_future_fact",
            )
        elif prediction.kind is PredictiveOutcomeKind.CURRENTLY_CONTRADICTED:
            disposition = GovernedPredictionDisposition.CURRENTLY_CONTRADICTED
            rationale = ("prediction:current_evidence_contradicts_source",)
        else:
            disposition = GovernedPredictionDisposition.UNRESOLVED
            rationale = ("prediction:source_evidence_unresolved",)
        return GovernedPredictionAssessment(
            prediction_id=request.prediction_id,
            relation_id=request.relation_id,
            horizon_code=request.horizon_code,
            disposition=disposition,
            predicted_domain=prediction.predicted_domain,
            predicted_key=prediction.predicted_key,
            predicted_value=prediction.predicted_value,
            condition_codes=request.condition_codes,
            rationale_codes=rationale,
        )

    @staticmethod
    def _status(
        source: GovernedCausalPredictionReport,
        assessments: tuple[GovernedPredictionAssessment, ...],
    ) -> GovernedPredictionStatus:
        if source.status is CausalPredictionStatus.DEGRADED:
            return GovernedPredictionStatus.DEGRADED
        if source.status is CausalPredictionStatus.WORLD_CONFLICT_REVIEW_REQUIRED:
            return GovernedPredictionStatus.REVIEW_REQUIRED
        if any(
            item.disposition is GovernedPredictionDisposition.REVIEW
            for item in assessments
        ):
            return GovernedPredictionStatus.REVIEW_REQUIRED
        if not assessments or all(
            item.disposition is GovernedPredictionDisposition.UNRESOLVED
            for item in assessments
        ):
            return GovernedPredictionStatus.INSUFFICIENT_EVIDENCE
        return GovernedPredictionStatus.COMPLETE

    @staticmethod
    def _fingerprint(
        source: GovernedCausalPredictionReport,
        requests: tuple[GovernedPredictionRequest, ...],
        assessments: tuple[GovernedPredictionAssessment, ...],
    ) -> str:
        payload = "\n".join(
            (
                source.source_fingerprint,
                *(
                    "|".join(
                        (
                            item.prediction_id,
                            item.relation_id,
                            item.horizon_code,
                            ",".join(item.condition_codes),
                        )
                    )
                    for item in requests
                ),
                *(
                    "|".join(
                        (
                            item.prediction_id,
                            item.relation_id,
                            item.horizon_code,
                            item.disposition.value,
                            item.predicted_domain or "",
                            item.predicted_key or "",
                            item.predicted_value or "",
                            ",".join(item.rationale_codes),
                        )
                    )
                    for item in assessments
                ),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()
