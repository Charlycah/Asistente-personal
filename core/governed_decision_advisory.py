from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.causal_prediction import (
    CausalAssessmentKind,
    CausalPredictionStatus,
    GovernedCausalPredictionReport,
    PredictiveOutcomeKind,
)
from core.governed_reasoning.scenario_simulation import (
    GovernedScenarioSimulationReport,
    ScenarioOutcomeKind,
    ScenarioSimulationStatus,
)
from core.intelligent_personal_organization import (
    IntelligentPersonalOrganizationReport,
    OrganizationRecommendationKind,
)
from core.mental_model_decision_evidence import MentalModelDecisionEvidence


class DecisionAdvisoryStatus(StrEnum):
    COMPLETE = "complete"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


class DecisionOptionDisposition(StrEnum):
    RECOMMEND = "recommend"
    DEFER = "defer"
    BLOCKED = "blocked"
    REVIEW = "review"


@dataclass(frozen=True)
class GovernedDecisionOption:
    option_id: str
    title: str
    organization_item_id: str | None = None
    scenario_hypothesis_id: str | None = None
    causal_relation_id: str | None = None
    explicit_preference: float = 0.0

    def __post_init__(self) -> None:
        if not self.option_id.strip():
            raise ValueError("decision option id must not be blank")
        if not self.title.strip():
            raise ValueError("decision option title must not be blank")
        for value, label in (
            (self.organization_item_id, "organization item"),
            (self.scenario_hypothesis_id, "scenario hypothesis"),
            (self.causal_relation_id, "causal relation"),
        ):
            if value is not None and not value.strip():
                raise ValueError(f"decision option {label} must not be blank")
        if not 0.0 <= float(self.explicit_preference) <= 1.0:
            raise ValueError("explicit preference must be between 0 and 1")


@dataclass(frozen=True)
class GovernedDecisionOptionAssessment:
    option_id: str
    disposition: DecisionOptionDisposition
    priority_score: float | None
    explicit_preference: float
    reason_codes: tuple[str, ...]
    organization_kind: str | None = None
    scenario_kind: str | None = None
    causal_kind: str | None = None
    prediction_kind: str | None = None
    action_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.option_id.strip():
            raise ValueError("decision assessment option id must not be blank")
        if self.priority_score is not None and not 0.0 <= self.priority_score <= 1.0:
            raise ValueError("decision priority score must be between 0 and 1")
        if not 0.0 <= self.explicit_preference <= 1.0:
            raise ValueError("decision preference must be between 0 and 1")
        if not self.reason_codes or any(not code.strip() for code in self.reason_codes):
            raise ValueError("decision assessment requires reason codes")
        if self.action_authorized:
            raise ValueError("decision advisory cannot authorize action")


@dataclass(frozen=True)
class GovernedDecisionAdvisoryReport:
    report_id: str
    status: DecisionAdvisoryStatus
    assessments: tuple[GovernedDecisionOptionAssessment, ...]
    recommended_option_id: str | None
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m391.6"
    canonical_authority: str = "unified_cognitive_coordination"
    canonical_facade: str = "CanonicalDecisionFacade"
    read_only: bool = True
    advisory_only: bool = True
    human_decision_preserved: bool = True
    creates_facts: bool = False
    creates_plans: bool = False
    creates_tasks: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    modifies_organization: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("decision-advisory-"):
            raise ValueError("decision advisory report id is invalid")
        if self.canonical_authority != "unified_cognitive_coordination":
            raise ValueError("canonical decision authority must be preserved")
        if self.canonical_facade != "CanonicalDecisionFacade":
            raise ValueError("canonical decision facade must be preserved")
        option_ids = tuple(item.option_id for item in self.assessments)
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("decision assessment option ids must be unique")
        if self.recommended_option_id is not None:
            if self.recommended_option_id not in option_ids:
                raise ValueError("recommended option must exist in assessments")
            selected = next(
                item
                for item in self.assessments
                if item.option_id == self.recommended_option_id
            )
            if selected.disposition is not DecisionOptionDisposition.RECOMMEND:
                raise ValueError("recommended option must be recommendable")
        if any(
            (
                not self.read_only,
                not self.advisory_only,
                not self.human_decision_preserved,
                self.creates_facts,
                self.creates_plans,
                self.creates_tasks,
                self.persists_results,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_planning,
                self.modifies_organization,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("decision advisory violates governed limits")


class GovernedDecisionAdvisor:
    """Pure advisory support subordinate to canonical decision authority."""

    CANONICAL_AUTHORITY = "unified_cognitive_coordination"
    CANONICAL_FACADE = "CanonicalDecisionFacade"

    def assess(
        self,
        options: tuple[GovernedDecisionOption, ...],
        *,
        organization: IntelligentPersonalOrganizationReport | None = None,
        scenarios: GovernedScenarioSimulationReport | None = None,
        causal: GovernedCausalPredictionReport | None = None,
        mental_model_evidence: tuple[MentalModelDecisionEvidence, ...] = (),
    ) -> GovernedDecisionAdvisoryReport:
        self._validate_unique_options(options)
        assessments = tuple(
            self._assess_option(
                option, organization, scenarios, causal, mental_model_evidence
            )
            for option in sorted(options, key=lambda item: item.option_id)
        )
        recommended = self._recommend(assessments)
        status = self._status(assessments, organization, scenarios, causal)
        evidence_codes = self._evidence_codes(
            organization, scenarios, causal, mental_model_evidence
        )
        risk_codes = self._risk_codes(assessments, organization, scenarios, causal)
        fingerprint = self._fingerprint(
            options,
            assessments,
            recommended,
            evidence_codes,
            risk_codes,
        )
        return GovernedDecisionAdvisoryReport(
            report_id=f"decision-advisory-{fingerprint[:16]}",
            status=status,
            assessments=assessments,
            recommended_option_id=recommended,
            evidence_codes=evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    def assess_safely(
        self,
        options: tuple[GovernedDecisionOption, ...],
        *,
        organization: IntelligentPersonalOrganizationReport | None = None,
        scenarios: GovernedScenarioSimulationReport | None = None,
        causal: GovernedCausalPredictionReport | None = None,
        mental_model_evidence: tuple[MentalModelDecisionEvidence, ...] = (),
    ) -> GovernedDecisionAdvisoryReport:
        try:
            return self.assess(
                options,
                organization=organization,
                scenarios=scenarios,
                causal=causal,
                mental_model_evidence=mental_model_evidence,
            )
        except Exception:
            fingerprint = sha256(repr(options).encode("utf-8")).hexdigest()
            return GovernedDecisionAdvisoryReport(
                report_id=f"decision-advisory-{fingerprint[:16]}",
                status=DecisionAdvisoryStatus.DEGRADED,
                assessments=(),
                recommended_option_id=None,
                evidence_codes=(),
                risk_codes=("decision_advisory_failure",),
                source_fingerprint=fingerprint,
            )

    @staticmethod
    def _validate_unique_options(options: tuple[GovernedDecisionOption, ...]) -> None:
        ids = tuple(item.option_id for item in options)
        if len(ids) != len(set(ids)):
            raise ValueError("decision option ids must be unique")

    @classmethod
    def _assess_option(
        cls,
        option: GovernedDecisionOption,
        organization: IntelligentPersonalOrganizationReport | None,
        scenarios: GovernedScenarioSimulationReport | None,
        causal: GovernedCausalPredictionReport | None,
        mental_model_evidence: tuple[MentalModelDecisionEvidence, ...],
    ) -> GovernedDecisionOptionAssessment:
        reasons: list[str] = []
        priority_score: float | None = None
        organization_kind: str | None = None
        scenario_kind: str | None = None
        causal_kind: str | None = None
        prediction_kind: str | None = None
        positive_signal = False
        blocked = False
        review = False
        deferred = False

        if option.organization_item_id is not None:
            item = cls._organization_item(organization, option.organization_item_id)
            if item is None:
                review = True
                reasons.append("decision:organization_evidence_missing")
            else:
                organization_kind = item.kind.value
                priority_score = item.score
                reasons.extend(f"organization:{code}" for code in item.reason_codes)
                if item.kind is OrganizationRecommendationKind.BLOCKED:
                    blocked = True
                elif item.kind is OrganizationRecommendationKind.REVIEW:
                    review = True
                elif item.kind is OrganizationRecommendationKind.DEFER:
                    deferred = True
                elif item.kind is OrganizationRecommendationKind.PRIORITIZE:
                    positive_signal = True

        if option.scenario_hypothesis_id is not None:
            outcome = cls._scenario_outcome(scenarios, option.scenario_hypothesis_id)
            if outcome is None:
                review = True
                reasons.append("decision:scenario_evidence_missing")
            else:
                scenario_kind = outcome.kind.value
                reasons.extend(outcome.rationale_codes)
                if outcome.kind is ScenarioOutcomeKind.CONTRADICTED:
                    blocked = True
                elif outcome.kind is ScenarioOutcomeKind.UNRESOLVED:
                    review = True
                elif outcome.kind is ScenarioOutcomeKind.CONSISTENT:
                    positive_signal = True

        if option.causal_relation_id is not None:
            assessment, prediction = cls._causal_evidence(
                causal,
                option.causal_relation_id,
            )
            if assessment is None or prediction is None:
                review = True
                reasons.append("decision:causal_evidence_missing")
            else:
                causal_kind = assessment.kind.value
                prediction_kind = prediction.kind.value
                reasons.extend(assessment.rationale_codes)
                reasons.extend(prediction.rationale_codes)
                if assessment.kind in {
                    CausalAssessmentKind.CAUSE_CONTRADICTED,
                    CausalAssessmentKind.EFFECT_CONTRADICTED,
                }:
                    blocked = True
                elif assessment.kind is CausalAssessmentKind.UNRESOLVED:
                    review = True
                if prediction.kind is PredictiveOutcomeKind.CURRENTLY_CONTRADICTED:
                    blocked = True
                elif prediction.kind is PredictiveOutcomeKind.UNRESOLVED:
                    review = True
                elif prediction.kind is PredictiveOutcomeKind.CONDITIONALLY_EXPECTED:
                    positive_signal = True

        matched_mental_model = tuple(
            item for item in mental_model_evidence if item.option_id == option.option_id
        )
        if matched_mental_model:
            reasons.extend(
                f"mental_model:{item.evidence_id}" for item in matched_mental_model
            )
            positive_signal = True

        if option.explicit_preference > 0.0:
            reasons.append("decision:explicit_preference")
            positive_signal = True

        if blocked:
            disposition = DecisionOptionDisposition.BLOCKED
        elif review:
            disposition = DecisionOptionDisposition.REVIEW
        elif deferred:
            disposition = DecisionOptionDisposition.DEFER
        elif positive_signal:
            disposition = DecisionOptionDisposition.RECOMMEND
        else:
            disposition = DecisionOptionDisposition.REVIEW
            reasons.append("decision:insufficient_explicit_evidence")

        return GovernedDecisionOptionAssessment(
            option_id=option.option_id,
            disposition=disposition,
            priority_score=priority_score,
            explicit_preference=option.explicit_preference,
            reason_codes=tuple(dict.fromkeys(reasons)),
            organization_kind=organization_kind,
            scenario_kind=scenario_kind,
            causal_kind=causal_kind,
            prediction_kind=prediction_kind,
        )

    @staticmethod
    def _organization_item(
        report: IntelligentPersonalOrganizationReport | None,
        item_id: str,
    ):
        if report is None:
            return None
        return next(
            (item for item in report.recommendations if item.item_id == item_id),
            None,
        )

    @staticmethod
    def _scenario_outcome(
        report: GovernedScenarioSimulationReport | None,
        hypothesis_id: str,
    ):
        if report is None:
            return None
        return next(
            (item for item in report.outcomes if item.hypothesis_id == hypothesis_id),
            None,
        )

    @staticmethod
    def _causal_evidence(
        report: GovernedCausalPredictionReport | None,
        relation_id: str,
    ):
        if report is None:
            return None, None
        assessment = next(
            (item for item in report.assessments if item.relation_id == relation_id),
            None,
        )
        prediction = next(
            (item for item in report.predictions if item.relation_id == relation_id),
            None,
        )
        return assessment, prediction

    @staticmethod
    def _recommend(
        assessments: tuple[GovernedDecisionOptionAssessment, ...],
    ) -> str | None:
        eligible = tuple(
            item
            for item in assessments
            if item.disposition is DecisionOptionDisposition.RECOMMEND
        )
        if not eligible:
            return None
        ordered = sorted(
            eligible,
            key=lambda item: (
                -(item.priority_score if item.priority_score is not None else 0.0),
                -item.explicit_preference,
                item.option_id,
            ),
        )
        return ordered[0].option_id

    @staticmethod
    def _status(
        assessments: tuple[GovernedDecisionOptionAssessment, ...],
        organization: IntelligentPersonalOrganizationReport | None,
        scenarios: GovernedScenarioSimulationReport | None,
        causal: GovernedCausalPredictionReport | None,
    ) -> DecisionAdvisoryStatus:
        if (
            scenarios is not None
            and scenarios.status is ScenarioSimulationStatus.DEGRADED
        ):
            return DecisionAdvisoryStatus.DEGRADED
        if causal is not None and causal.status is CausalPredictionStatus.DEGRADED:
            return DecisionAdvisoryStatus.DEGRADED
        if not assessments:
            return DecisionAdvisoryStatus.INSUFFICIENT_EVIDENCE
        if any(
            item.disposition is DecisionOptionDisposition.REVIEW for item in assessments
        ):
            return DecisionAdvisoryStatus.REVIEW_REQUIRED
        if any(
            item.disposition is DecisionOptionDisposition.RECOMMEND
            for item in assessments
        ):
            return DecisionAdvisoryStatus.COMPLETE
        if organization is None and scenarios is None and causal is None:
            return DecisionAdvisoryStatus.INSUFFICIENT_EVIDENCE
        return DecisionAdvisoryStatus.COMPLETE

    @staticmethod
    def _evidence_codes(
        organization: IntelligentPersonalOrganizationReport | None,
        scenarios: GovernedScenarioSimulationReport | None,
        causal: GovernedCausalPredictionReport | None,
        mental_model_evidence: tuple[MentalModelDecisionEvidence, ...],
    ) -> tuple[str, ...]:
        codes: list[str] = []
        if organization is not None:
            codes.append(f"organization_report:{organization.report_id}")
        if scenarios is not None:
            codes.append(f"scenario_report:{scenarios.simulation_id}")
            codes.extend(scenarios.evidence_codes)
        if causal is not None:
            codes.append(f"causal_report:{causal.analysis_id}")
            codes.extend(causal.evidence_codes)
        codes.extend(
            f"mental_model_evidence:{item.evidence_id}"
            for item in mental_model_evidence
        )
        return tuple(dict.fromkeys(codes))

    @staticmethod
    def _risk_codes(
        assessments: tuple[GovernedDecisionOptionAssessment, ...],
        organization: IntelligentPersonalOrganizationReport | None,
        scenarios: GovernedScenarioSimulationReport | None,
        causal: GovernedCausalPredictionReport | None,
    ) -> tuple[str, ...]:
        del organization
        codes: list[str] = ["decision_advisory_not_action_authority"]
        if scenarios is not None:
            codes.extend(scenarios.risk_codes)
        if causal is not None:
            codes.extend(causal.risk_codes)
        if any(
            item.disposition is DecisionOptionDisposition.REVIEW for item in assessments
        ):
            codes.append("decision_human_review_required")
        if any(
            item.disposition is DecisionOptionDisposition.BLOCKED
            for item in assessments
        ):
            codes.append("decision_option_blocked")
        return tuple(dict.fromkeys(codes))

    @staticmethod
    def _fingerprint(*parts: object) -> str:
        return sha256(repr(parts).encode("utf-8")).hexdigest()
