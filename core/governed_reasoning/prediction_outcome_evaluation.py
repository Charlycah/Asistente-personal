from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.governed_prediction import (
    GovernedPredictionAssessment,
    GovernedPredictionDisposition,
)


class PredictionOutcomeDisposition(StrEnum):
    MATCH = "match"
    MISMATCH = "mismatch"
    UNRESOLVED = "unresolved"
    REVIEW = "review"


@dataclass(frozen=True)
class ObservedPredictionOutcome:
    observation_id: str
    domain: str
    key: str
    value: str
    horizon_code: str
    condition_codes: tuple[str, ...] = ()
    evidence_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, label in (
            (self.observation_id, "observation id"),
            (self.domain, "domain"),
            (self.key, "key"),
            (self.value, "value"),
            (self.horizon_code, "horizon code"),
        ):
            if not value.strip():
                raise ValueError(f"prediction outcome {label} must not be blank")
        if any(not code.strip() for code in self.condition_codes):
            raise ValueError("prediction outcome conditions must not be blank")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("prediction outcome evidence must not be blank")


@dataclass(frozen=True)
class PredictionErrorLearningCandidate:
    evaluation_id: str
    prediction_id: str
    observation_id: str
    disposition: str = "review_required"
    accepted_as_knowledge: bool = False
    persistence_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.evaluation_id.strip():
            raise ValueError("prediction learning evaluation id must not be blank")
        if not self.prediction_id.strip() or not self.observation_id.strip():
            raise ValueError("prediction learning lineage must not be blank")
        if self.disposition != "review_required":
            raise ValueError("prediction learning candidate must remain review-only")
        if self.accepted_as_knowledge or self.persistence_authorized:
            raise ValueError("prediction error cannot auto-accept or persist learning")


@dataclass(frozen=True)
class PredictionOutcomeEvaluation:
    evaluation_id: str
    prediction_id: str
    observation_id: str | None
    disposition: PredictionOutcomeDisposition | str
    predicted_value: str | None
    observed_value: str | None
    evidence_codes: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    learning_candidate: PredictionErrorLearningCandidate | None = None
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    establishes_truth: bool = False
    proves_causality: bool = False
    calibrates_probability: bool = False
    modifies_prediction: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    persists_results: bool = False
    executes_actions: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "disposition",
            PredictionOutcomeDisposition(self.disposition),
        )
        if not self.evaluation_id.startswith("prediction-outcome-"):
            raise ValueError("prediction outcome evaluation id is invalid")
        if not self.prediction_id.strip():
            raise ValueError("prediction outcome prediction id must not be blank")
        if not self.rationale_codes:
            raise ValueError("prediction outcome evaluation requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("prediction outcome must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                self.establishes_truth,
                self.proves_causality,
                self.calibrates_probability,
                self.modifies_prediction,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.persists_results,
                self.executes_actions,
            )
        ):
            raise ValueError("prediction outcome evaluation violates governed limits")
        if (
            self.learning_candidate is not None
            and self.disposition is not PredictionOutcomeDisposition.MISMATCH
        ):
            raise ValueError("only a mismatch may propose review-only learning")


class GovernedPredictionOutcomeEvaluator:
    """Compare one governed prediction with one later governed observation."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def evaluate(
        self,
        prediction: GovernedPredictionAssessment,
        observation: ObservedPredictionOutcome | None,
    ) -> PredictionOutcomeEvaluation:
        disposition, rationale = self._compare(prediction, observation)
        observation_id = observation.observation_id if observation else None
        observed_value = observation.value if observation else None
        evidence = tuple(
            dict.fromkeys(
                (
                    f"prediction:{prediction.prediction_id}",
                    *prediction.rationale_codes,
                    *(() if observation is None else observation.evidence_codes),
                    *(
                        ()
                        if observation is None
                        else (f"observation:{observation.observation_id}",)
                    ),
                )
            )
        )
        fingerprint = sha256(
            "|".join(
                (
                    prediction.prediction_id,
                    prediction.relation_id,
                    prediction.horizon_code,
                    prediction.predicted_domain or "",
                    prediction.predicted_key or "",
                    prediction.predicted_value or "",
                    ",".join(prediction.condition_codes),
                    observation_id or "none",
                    observed_value or "none",
                    disposition.value,
                    *rationale,
                )
            ).encode("utf-8")
        ).hexdigest()
        evaluation_id = f"prediction-outcome-{fingerprint[:16]}"
        candidate = None
        if disposition is PredictionOutcomeDisposition.MISMATCH:
            candidate = PredictionErrorLearningCandidate(
                evaluation_id=evaluation_id,
                prediction_id=prediction.prediction_id,
                observation_id=observation_id or "",
            )
        return PredictionOutcomeEvaluation(
            evaluation_id=evaluation_id,
            prediction_id=prediction.prediction_id,
            observation_id=observation_id,
            disposition=disposition,
            predicted_value=prediction.predicted_value,
            observed_value=observed_value,
            evidence_codes=evidence,
            rationale_codes=rationale,
            learning_candidate=candidate,
        )

    @staticmethod
    def _compare(
        prediction: GovernedPredictionAssessment,
        observation: ObservedPredictionOutcome | None,
    ) -> tuple[PredictionOutcomeDisposition, tuple[str, ...]]:
        if (
            prediction.disposition
            is not GovernedPredictionDisposition.CONDITIONALLY_SUPPORTED
        ):
            return (
                PredictionOutcomeDisposition.UNRESOLVED,
                ("prediction_outcome:source_prediction_not_supported",),
            )
        if observation is None:
            return (
                PredictionOutcomeDisposition.UNRESOLVED,
                ("prediction_outcome:observation_missing",),
            )
        if observation.horizon_code != prediction.horizon_code:
            return (
                PredictionOutcomeDisposition.REVIEW,
                ("prediction_outcome:horizon_mismatch",),
            )
        if tuple(observation.condition_codes) != tuple(prediction.condition_codes):
            return (
                PredictionOutcomeDisposition.REVIEW,
                ("prediction_outcome:condition_mismatch",),
            )
        if (
            observation.domain.casefold()
            != (prediction.predicted_domain or "").casefold()
            or observation.key.casefold()
            != (prediction.predicted_key or "").casefold()
        ):
            return (
                PredictionOutcomeDisposition.REVIEW,
                ("prediction_outcome:observation_lineage_mismatch",),
            )
        if (
            observation.value.casefold()
            == (prediction.predicted_value or "").casefold()
        ):
            return (
                PredictionOutcomeDisposition.MATCH,
                ("prediction_outcome:observed_value_matches_prediction",),
            )
        return (
            PredictionOutcomeDisposition.MISMATCH,
            ("prediction_outcome:observed_value_differs_from_prediction",),
        )
