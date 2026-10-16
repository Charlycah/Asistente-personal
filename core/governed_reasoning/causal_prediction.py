from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.persistent_world_model import PersistentWorldSnapshot


class CausalPredictionStatus(StrEnum):
    COMPLETE = "complete"
    WORLD_CONFLICT_REVIEW_REQUIRED = "world_conflict_review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


class CausalAssessmentKind(StrEnum):
    ASSOCIATION_COMPATIBLE = "association_compatible"
    EFFECT_CONTRADICTED = "effect_contradicted"
    CAUSE_CONTRADICTED = "cause_contradicted"
    UNRESOLVED = "unresolved"


class PredictiveOutcomeKind(StrEnum):
    CONDITIONALLY_EXPECTED = "conditionally_expected"
    CURRENTLY_CONTRADICTED = "currently_contradicted"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class CausalHypothesis:
    relation_id: str
    proposition: str
    cause_domain: str
    cause_key: str
    cause_value: str
    effect_domain: str
    effect_key: str
    effect_value: str
    evidence_codes: tuple[str, ...] = ()
    epistemic_level: EpistemicLevel = EpistemicLevel.HYPOTHESIS
    temporal_scope: str = "current"

    def __post_init__(self) -> None:
        for value, label in (
            (self.relation_id, "relation id"),
            (self.proposition, "proposition"),
            (self.cause_domain, "cause domain"),
            (self.cause_key, "cause key"),
            (self.cause_value, "cause value"),
            (self.effect_domain, "effect domain"),
            (self.effect_key, "effect key"),
            (self.effect_value, "effect value"),
        ):
            if not value.strip():
                raise ValueError(f"causal hypothesis {label} must not be blank")
        if self.epistemic_level is not EpistemicLevel.HYPOTHESIS:
            raise ValueError("causal relations must remain hypotheses")
        if self.temporal_scope not in {"current", "future"}:
            raise ValueError("causal temporal scope must be current or future")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("causal evidence codes must not be blank")


@dataclass(frozen=True)
class CausalAssessment:
    relation_id: str
    kind: CausalAssessmentKind
    cause_fact_ids: tuple[str, ...]
    effect_fact_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    epistemic_level: EpistemicLevel = EpistemicLevel.HYPOTHESIS
    establishes_causality: bool = False

    def __post_init__(self) -> None:
        if not self.relation_id.strip():
            raise ValueError("causal assessment relation id must not be blank")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("causal assessment requires rationale codes")
        if self.epistemic_level is not EpistemicLevel.HYPOTHESIS:
            raise ValueError("causal assessments must remain hypotheses")
        if self.establishes_causality:
            raise ValueError("M391.4 cannot establish causality automatically")


@dataclass(frozen=True)
class PredictiveOutcome:
    relation_id: str
    kind: PredictiveOutcomeKind
    predicted_domain: str
    predicted_key: str
    predicted_value: str
    rationale_codes: tuple[str, ...]
    epistemic_level: EpistemicLevel = EpistemicLevel.INFERENCE
    is_future_fact: bool = False

    def __post_init__(self) -> None:
        for value, label in (
            (self.relation_id, "relation id"),
            (self.predicted_domain, "predicted domain"),
            (self.predicted_key, "predicted key"),
            (self.predicted_value, "predicted value"),
        ):
            if not value.strip():
                raise ValueError(f"predictive outcome {label} must not be blank")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("predictive outcome requires rationale codes")
        if self.epistemic_level is not EpistemicLevel.INFERENCE:
            raise ValueError("predictions must remain inferences")
        if self.is_future_fact:
            raise ValueError("predictions cannot be future facts")


@dataclass(frozen=True)
class GovernedCausalPredictionReport:
    analysis_id: str
    status: CausalPredictionStatus
    world_snapshot_id: str
    hypotheses: tuple[CausalHypothesis, ...]
    assessments: tuple[CausalAssessment, ...]
    predictions: tuple[PredictiveOutcome, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m391.4"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    creates_facts: bool = False
    proves_causality: bool = False
    calibrates_probability: bool = False
    persists_results: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.analysis_id.startswith("causal-prediction-"):
            raise ValueError("causal prediction identifier is invalid")
        if not self.world_snapshot_id.strip():
            raise ValueError("causal prediction world snapshot is required")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("causal prediction must preserve reasoning authority")
        ids = tuple(item.relation_id for item in self.hypotheses)
        if len(ids) != len(set(ids)):
            raise ValueError("causal relation identifiers must be unique")
        if tuple(item.relation_id for item in self.assessments) != ids:
            raise ValueError("causal assessments must preserve relation ordering")
        if tuple(item.relation_id for item in self.predictions) != ids:
            raise ValueError("predictions must preserve relation ordering")
        if any(
            (
                not self.read_only,
                self.creates_facts,
                self.proves_causality,
                self.calibrates_probability,
                self.persists_results,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_planning,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("causal prediction violates governed limits")


class GovernedCausalPredictiveReasoner:
    """Pure causal/predictive analysis under governed reasoning authority."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def analyze(
        self,
        world: PersistentWorldSnapshot,
        hypotheses: tuple[CausalHypothesis, ...],
    ) -> GovernedCausalPredictionReport:
        ordered = tuple(sorted(hypotheses, key=lambda item: item.relation_id))
        assessments = tuple(self._assess(world, item) for item in ordered)
        predictions = tuple(
            self._predict(item, assessment)
            for item, assessment in zip(ordered, assessments, strict=True)
        )
        status = self._status(world, assessments)
        evidence_codes = tuple(
            dict.fromkeys(
                (
                    f"world_snapshot:{world.snapshot_id}",
                    *world.evidence_codes,
                    *(code for item in ordered for code in item.evidence_codes),
                    *(
                        code
                        for assessment in assessments
                        for code in assessment.rationale_codes
                    ),
                    *(
                        code
                        for prediction in predictions
                        for code in prediction.rationale_codes
                    ),
                )
            )
        )
        risk_codes = tuple(
            dict.fromkeys(
                (
                    *world.risk_codes,
                    "causality_not_established",
                    "prediction_not_fact",
                    *(
                        "causal_evidence_insufficient"
                        for assessment in assessments
                        if assessment.kind is CausalAssessmentKind.UNRESOLVED
                    ),
                    *(
                        "causal_hypothesis_contradicted"
                        for assessment in assessments
                        if assessment.kind
                        in {
                            CausalAssessmentKind.CAUSE_CONTRADICTED,
                            CausalAssessmentKind.EFFECT_CONTRADICTED,
                        }
                    ),
                )
            )
        )
        fingerprint = self._fingerprint(
            world,
            ordered,
            assessments,
            predictions,
        )
        return GovernedCausalPredictionReport(
            analysis_id=f"causal-prediction-{fingerprint[:16]}",
            status=status,
            world_snapshot_id=world.snapshot_id,
            hypotheses=ordered,
            assessments=assessments,
            predictions=predictions,
            evidence_codes=evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    def analyze_safely(
        self,
        world: PersistentWorldSnapshot,
        hypotheses: tuple[CausalHypothesis, ...],
    ) -> GovernedCausalPredictionReport:
        try:
            return self.analyze(world, hypotheses)
        except Exception:
            fingerprint = sha256(world.snapshot_id.encode("utf-8")).hexdigest()
            return GovernedCausalPredictionReport(
                analysis_id=f"causal-prediction-{fingerprint[:16]}",
                status=CausalPredictionStatus.DEGRADED,
                world_snapshot_id=world.snapshot_id,
                hypotheses=(),
                assessments=(),
                predictions=(),
                evidence_codes=(f"world_snapshot:{world.snapshot_id}",),
                risk_codes=("causal_prediction_failure",),
                source_fingerprint=fingerprint,
            )

    @staticmethod
    def _facts_for(
        world: PersistentWorldSnapshot,
        domain: str,
        key: str,
    ) -> tuple[object, ...]:
        return tuple(
            fact
            for fact in world.facts
            if fact.active
            and fact.domain.value == domain
            and fact.fact_key.casefold() == key.casefold()
            and fact.epistemic_level is EpistemicLevel.FACT
        )

    @classmethod
    def _assess(
        cls,
        world: PersistentWorldSnapshot,
        hypothesis: CausalHypothesis,
    ) -> CausalAssessment:
        causes = cls._facts_for(world, hypothesis.cause_domain, hypothesis.cause_key)
        effects = cls._facts_for(
            world,
            hypothesis.effect_domain,
            hypothesis.effect_key,
        )
        cause_values = {fact.value.strip().casefold() for fact in causes}
        effect_values = {fact.value.strip().casefold() for fact in effects}
        cause_match = hypothesis.cause_value.strip().casefold() in cause_values
        effect_match = hypothesis.effect_value.strip().casefold() in effect_values

        if causes and not cause_match:
            kind = CausalAssessmentKind.CAUSE_CONTRADICTED
            rationale = ("causal:cause_contradicted_by_persistent_fact",)
        elif cause_match and effects and not effect_match:
            kind = CausalAssessmentKind.EFFECT_CONTRADICTED
            rationale = ("causal:effect_contradicted_by_persistent_fact",)
        elif cause_match and effect_match:
            kind = CausalAssessmentKind.ASSOCIATION_COMPATIBLE
            rationale = (
                "causal:association_compatible",
                "causal:cooccurrence_does_not_prove_causality",
            )
        elif (
            hypothesis.temporal_scope == "future"
            and cause_match
            and not effects
        ):
            kind = CausalAssessmentKind.ASSOCIATION_COMPATIBLE
            rationale = (
                "causal:future_cause_condition_supported",
                "causal:future_effect_not_yet_observed",
                "causal:causality_not_established",
            )
        else:
            kind = CausalAssessmentKind.UNRESOLVED
            rationale = ("causal:insufficient_explicit_evidence",)
        return CausalAssessment(
            relation_id=hypothesis.relation_id,
            kind=kind,
            cause_fact_ids=tuple(fact.fact_id for fact in causes),
            effect_fact_ids=tuple(fact.fact_id for fact in effects),
            rationale_codes=rationale,
        )

    @staticmethod
    def _predict(
        hypothesis: CausalHypothesis,
        assessment: CausalAssessment,
    ) -> PredictiveOutcome:
        if assessment.kind is CausalAssessmentKind.ASSOCIATION_COMPATIBLE:
            kind = PredictiveOutcomeKind.CONDITIONALLY_EXPECTED
            rationale = (
                "prediction:conditional_on_explicit_causal_hypothesis",
                "prediction:not_a_future_fact",
            )
        elif assessment.kind in {
            CausalAssessmentKind.CAUSE_CONTRADICTED,
            CausalAssessmentKind.EFFECT_CONTRADICTED,
        }:
            kind = PredictiveOutcomeKind.CURRENTLY_CONTRADICTED
            rationale = ("prediction:current_world_contradicts_hypothesis",)
        else:
            kind = PredictiveOutcomeKind.UNRESOLVED
            rationale = ("prediction:insufficient_explicit_evidence",)
        return PredictiveOutcome(
            relation_id=hypothesis.relation_id,
            kind=kind,
            predicted_domain=hypothesis.effect_domain,
            predicted_key=hypothesis.effect_key,
            predicted_value=hypothesis.effect_value,
            rationale_codes=rationale,
        )

    @staticmethod
    def _status(
        world: PersistentWorldSnapshot,
        assessments: tuple[CausalAssessment, ...],
    ) -> CausalPredictionStatus:
        if world.conflict_keys:
            return CausalPredictionStatus.WORLD_CONFLICT_REVIEW_REQUIRED
        if not assessments or all(
            item.kind is CausalAssessmentKind.UNRESOLVED for item in assessments
        ):
            return CausalPredictionStatus.INSUFFICIENT_EVIDENCE
        return CausalPredictionStatus.COMPLETE

    @staticmethod
    def _fingerprint(
        world: PersistentWorldSnapshot,
        hypotheses: tuple[CausalHypothesis, ...],
        assessments: tuple[CausalAssessment, ...],
        predictions: tuple[PredictiveOutcome, ...],
    ) -> str:
        payload = "\n".join(
            (
                world.source_fingerprint,
                *(
                    "|".join(
                        (
                            item.relation_id,
                            item.proposition,
                            item.cause_domain,
                            item.cause_key,
                            item.cause_value,
                            item.effect_domain,
                            item.effect_key,
                            item.effect_value,
                            item.temporal_scope,
                            ",".join(item.evidence_codes),
                        )
                    )
                    for item in hypotheses
                ),
                *(
                    "|".join(
                        (
                            item.relation_id,
                            item.kind.value,
                            ",".join(item.cause_fact_ids),
                            ",".join(item.effect_fact_ids),
                            ",".join(item.rationale_codes),
                        )
                    )
                    for item in assessments
                ),
                *(
                    "|".join(
                        (
                            item.relation_id,
                            item.kind.value,
                            item.predicted_domain,
                            item.predicted_key,
                            item.predicted_value,
                            ",".join(item.rationale_codes),
                        )
                    )
                    for item in predictions
                ),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()
