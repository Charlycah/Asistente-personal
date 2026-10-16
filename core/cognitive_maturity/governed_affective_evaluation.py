from __future__ import annotations

from .functional_psychology import (
    FunctionalPsychologyReport,
    FunctionalPsychologyStatus,
)
from .pending_matters import PendingMattersReport, PendingMattersStatus
from .simulated_inner_state import (
    SimulatedActivationLevel,
    SimulatedAffectiveTone,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedInnerStateSignal,
    SimulatedRelationalOpenness,
    SimulatedStabilityLevel,
)
from .unified_epistemic_evidence import (
    UnifiedEpistemicCategory,
    UnifiedEpistemicReport,
    UnifiedEpistemicStatus,
)


class GovernedAffectiveEvaluator:
    """Pure adapter from certified M389 reports to M390 simulated-state signals.

    This component is deliberately not an authority. It cannot construct or persist
    an inner-state snapshot; only ``SimulatedInnerStateAuthority`` may do that.
    """

    evaluator_id = "governed_affective_evaluation"

    def evaluate(
        self,
        psychology: FunctionalPsychologyReport | None,
        pending_matters: PendingMattersReport | None,
        epistemic: UnifiedEpistemicReport | None,
    ) -> tuple[SimulatedInnerStateSignal, ...]:
        signals: list[SimulatedInnerStateSignal] = []
        if psychology is not None:
            signals.append(self._from_psychology(psychology))
        if pending_matters is not None:
            signals.append(self._from_pending_matters(pending_matters))
        if epistemic is not None:
            signals.append(self._from_epistemic(epistemic))
        return tuple(
            sorted(
                signals,
                key=lambda item: (item.source_authority, item.source_reference),
            )
        )

    def evaluate_safely(
        self,
        psychology: FunctionalPsychologyReport | None,
        pending_matters: PendingMattersReport | None,
        epistemic: UnifiedEpistemicReport | None,
    ) -> tuple[SimulatedInnerStateSignal, ...]:
        try:
            return self.evaluate(psychology, pending_matters, epistemic)
        except Exception:
            return (
                SimulatedInnerStateSignal(
                    source_authority=self.evaluator_id,
                    source_reference="safe-degradation",
                    epistemic_category=(
                        UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION
                    ),
                    affective_tone=SimulatedAffectiveTone.UNKNOWN,
                    activation_level=SimulatedActivationLevel.UNKNOWN,
                    stability_level=SimulatedStabilityLevel.UNKNOWN,
                    concern_level=SimulatedConcernLevel.UNKNOWN,
                    relational_openness=SimulatedRelationalOpenness.UNKNOWN,
                    dominant_state=SimulatedDominantState.UNCERTAIN,
                    evidence_codes=("safe_degradation_without_side_effects",),
                    risk_codes=("governed_affective_evaluation_failure",),
                ),
            )

    @staticmethod
    def _from_psychology(
        report: FunctionalPsychologyReport,
    ) -> SimulatedInnerStateSignal:
        if report.status is FunctionalPsychologyStatus.DEGRADED:
            return GovernedAffectiveEvaluator._unknown_signal(
                source_authority="functional_psychology",
                source_reference=report.report_id,
                evidence_codes=("functional_psychology_degraded",),
                risk_codes=report.caution_codes,
            )
        if report.status is FunctionalPsychologyStatus.INSUFFICIENT_EVIDENCE:
            return GovernedAffectiveEvaluator._unknown_signal(
                source_authority="functional_psychology",
                source_reference=report.report_id,
                evidence_codes=("functional_psychology_insufficient",),
                risk_codes=report.caution_codes,
            )

        indicator_codes = {
            item.code
            for item in (
                report.cognitive_style_indicators
                + report.conversational_function_indicators
                + report.stability_indicators
            )
        }
        risk_attention = any("risk_attention" in code for code in indicator_codes)
        exploratory = "exploratory_hypothesis_processing" in indicator_codes
        stable = bool(report.stability_indicators)
        cautious = bool(report.caution_codes) or risk_attention

        dominant_state = SimulatedDominantState.ATTENTIVE
        if cautious:
            dominant_state = SimulatedDominantState.CAUTIOUS
        elif exploratory:
            dominant_state = SimulatedDominantState.CURIOUS

        concern = (
            SimulatedConcernLevel.MODERATE
            if risk_attention
            else SimulatedConcernLevel.LOW
            if report.caution_codes
            else SimulatedConcernLevel.NONE
        )
        return SimulatedInnerStateSignal(
            source_authority="functional_psychology",
            source_reference=report.report_id,
            epistemic_category=UnifiedEpistemicCategory.INFERRED,
            affective_tone=SimulatedAffectiveTone.NEUTRAL,
            activation_level=SimulatedActivationLevel.MODERATE,
            stability_level=(
                SimulatedStabilityLevel.STABLE
                if stable
                else SimulatedStabilityLevel.UNKNOWN
            ),
            concern_level=concern,
            relational_openness=SimulatedRelationalOpenness.BALANCED,
            dominant_state=dominant_state,
            evidence_codes=tuple(
                sorted(
                    {
                        "affective_signal_from_functional_psychology",
                        *(f"psychology_indicator:{code}" for code in indicator_codes),
                    }
                )
            ),
            risk_codes=tuple(sorted(set(report.caution_codes))),
        )

    @staticmethod
    def _from_pending_matters(
        report: PendingMattersReport,
    ) -> SimulatedInnerStateSignal:
        if report.status is PendingMattersStatus.DEGRADED:
            return GovernedAffectiveEvaluator._unknown_signal(
                source_authority="pending_matters",
                source_reference=report.report_id,
                evidence_codes=("pending_matters_degraded",),
                risk_codes=report.risk_codes,
            )
        if report.status is PendingMattersStatus.INSUFFICIENT_EVIDENCE:
            return GovernedAffectiveEvaluator._unknown_signal(
                source_authority="pending_matters",
                source_reference=report.report_id,
                evidence_codes=("pending_matters_insufficient",),
                risk_codes=report.risk_codes,
            )

        unresolved = (
            report.statistics.open_count
            + report.statistics.partial_count
            + report.statistics.unknown_count
        )
        if unresolved == 0:
            activation = SimulatedActivationLevel.LOW
            stability = SimulatedStabilityLevel.STABLE
            concern = SimulatedConcernLevel.NONE
            dominant_state = SimulatedDominantState.CALM
        else:
            activation = (
                SimulatedActivationLevel.HIGH
                if unresolved >= 4
                else SimulatedActivationLevel.MODERATE
            )
            stability = SimulatedStabilityLevel.VARIABLE
            concern = (
                SimulatedConcernLevel.HIGH
                if unresolved >= 4
                else SimulatedConcernLevel.MODERATE
            )
            dominant_state = SimulatedDominantState.CONCERNED

        return SimulatedInnerStateSignal(
            source_authority="pending_matters",
            source_reference=report.report_id,
            epistemic_category=UnifiedEpistemicCategory.INFERRED,
            affective_tone=SimulatedAffectiveTone.NEUTRAL,
            activation_level=activation,
            stability_level=stability,
            concern_level=concern,
            relational_openness=SimulatedRelationalOpenness.BALANCED,
            dominant_state=dominant_state,
            evidence_codes=tuple(
                sorted(
                    {
                        "affective_signal_from_pending_matters",
                        f"pending_total:{report.statistics.total}",
                        f"pending_unresolved:{unresolved}",
                        *report.evidence_codes,
                    }
                )
            ),
            risk_codes=tuple(sorted(set(report.risk_codes))),
        )

    @staticmethod
    def _from_epistemic(report: UnifiedEpistemicReport) -> SimulatedInnerStateSignal:
        if report.status is UnifiedEpistemicStatus.DEGRADED:
            return GovernedAffectiveEvaluator._unknown_signal(
                source_authority="unified_epistemic_evidence",
                source_reference=report.report_id,
                evidence_codes=("unified_epistemic_evidence_degraded",),
                risk_codes=report.risk_codes,
            )
        if report.status is UnifiedEpistemicStatus.INSUFFICIENT_EVIDENCE:
            return GovernedAffectiveEvaluator._unknown_signal(
                source_authority="unified_epistemic_evidence",
                source_reference=report.report_id,
                evidence_codes=("unified_epistemic_evidence_insufficient",),
                risk_codes=report.risk_codes,
            )
        if report.status is UnifiedEpistemicStatus.CONFLICT_REVIEW_REQUIRED:
            return SimulatedInnerStateSignal(
                source_authority="unified_epistemic_evidence",
                source_reference=report.report_id,
                epistemic_category=UnifiedEpistemicCategory.POSSIBLE,
                affective_tone=SimulatedAffectiveTone.MIXED,
                activation_level=SimulatedActivationLevel.MODERATE,
                stability_level=SimulatedStabilityLevel.VARIABLE,
                concern_level=SimulatedConcernLevel.MODERATE,
                relational_openness=SimulatedRelationalOpenness.RESERVED,
                dominant_state=SimulatedDominantState.CONFLICTED,
                evidence_codes=tuple(
                    sorted(
                        {
                            "affective_signal_from_epistemic_conflict",
                            *report.evidence_codes,
                            *report.conflict_codes,
                        }
                    )
                ),
                risk_codes=tuple(sorted(set(report.risk_codes))),
            )

        categories = {item.category for item in report.records}
        if UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION in categories:
            category = UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION
            dominant_state = SimulatedDominantState.UNCERTAIN
            concern = SimulatedConcernLevel.LOW
        elif UnifiedEpistemicCategory.POSSIBLE in categories:
            category = UnifiedEpistemicCategory.POSSIBLE
            dominant_state = SimulatedDominantState.CAUTIOUS
            concern = SimulatedConcernLevel.LOW
        elif UnifiedEpistemicCategory.INFERRED in categories:
            category = UnifiedEpistemicCategory.INFERRED
            dominant_state = SimulatedDominantState.ATTENTIVE
            concern = SimulatedConcernLevel.NONE
        else:
            category = UnifiedEpistemicCategory.OBSERVED
            dominant_state = SimulatedDominantState.ATTENTIVE
            concern = SimulatedConcernLevel.NONE

        return SimulatedInnerStateSignal(
            source_authority="unified_epistemic_evidence",
            source_reference=report.report_id,
            epistemic_category=category,
            affective_tone=SimulatedAffectiveTone.NEUTRAL,
            activation_level=SimulatedActivationLevel.MODERATE,
            stability_level=SimulatedStabilityLevel.STABLE,
            concern_level=concern,
            relational_openness=SimulatedRelationalOpenness.BALANCED,
            dominant_state=dominant_state,
            evidence_codes=tuple(
                sorted(
                    {
                        "affective_signal_from_unified_epistemic_evidence",
                        *report.evidence_codes,
                    }
                )
            ),
            risk_codes=tuple(sorted(set(report.risk_codes))),
        )

    @staticmethod
    def _unknown_signal(
        *,
        source_authority: str,
        source_reference: str,
        evidence_codes: tuple[str, ...],
        risk_codes: tuple[str, ...],
    ) -> SimulatedInnerStateSignal:
        return SimulatedInnerStateSignal(
            source_authority=source_authority,
            source_reference=source_reference,
            epistemic_category=UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION,
            affective_tone=SimulatedAffectiveTone.UNKNOWN,
            activation_level=SimulatedActivationLevel.UNKNOWN,
            stability_level=SimulatedStabilityLevel.UNKNOWN,
            concern_level=SimulatedConcernLevel.UNKNOWN,
            relational_openness=SimulatedRelationalOpenness.UNKNOWN,
            dominant_state=SimulatedDominantState.UNCERTAIN,
            evidence_codes=tuple(sorted(set(evidence_codes))),
            risk_codes=tuple(sorted(set(risk_codes))),
        )
