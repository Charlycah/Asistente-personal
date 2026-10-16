from __future__ import annotations

from dataclasses import dataclass

from .capability_selection import CognitiveCapabilitySelectionAssessment
from .context_selection import CognitiveContextSelectionAssessment
from .executive_activation import CognitiveExecutiveActivationAssessment
from .models import (
    CognitivePlan,
    CognitivePlanOutcomeAssessment,
    PlannedResponseDecision,
    ShadowAssessmentStatus,
)


@dataclass(frozen=True)
class CognitivePolicyResolution:
    """Deterministic, explainable resolution of competing cognitive policies."""

    policy: str
    decisive_rule: str
    conflict_codes: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    fallback_required: bool


class CognitivePolicyResolutionEngine:
    """Resolve policy conflicts without routing, executing, or rewriting output."""

    def resolve(
        self,
        plan: CognitivePlan,
        *,
        risk: str,
        confidence: str,
        outcome: CognitivePlanOutcomeAssessment | None = None,
        capability: CognitiveCapabilitySelectionAssessment | None = None,
        context: CognitiveContextSelectionAssessment | None = None,
        activation: CognitiveExecutiveActivationAssessment | None = None,
    ) -> CognitivePolicyResolution:
        conflicts = self._conflicts(
            outcome=outcome,
            capability=capability,
            context=context,
            activation=activation,
        )

        if plan.response_decision is PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED:
            if outcome is None or not outcome.evidence_satisfied:
                return self._result(
                    "abstain_if_unverified",
                    "required_evidence_not_satisfied",
                    conflicts,
                    fallback_required=False,
                )

        if confidence == "low":
            return self._result(
                "fallback",
                "low_confidence",
                conflicts,
                fallback_required=True,
            )

        if "context_unsatisfied" in conflicts:
            return self._result(
                "fallback",
                "required_context_unsatisfied",
                conflicts,
                fallback_required=True,
            )

        if "capability_mismatch" in conflicts:
            return self._result(
                "fallback",
                "required_capability_mismatch",
                conflicts,
                fallback_required=True,
            )

        if "contradictory_sources" in conflicts:
            return self._result(
                "respond_with_caution",
                "contradictory_sources",
                conflicts,
                fallback_required=False,
            )

        if activation is not None and activation.fallback_required:
            return self._result(
                "fallback",
                "executive_activation_fallback",
                conflicts,
                fallback_required=True,
            )

        if risk in {"moderate", "high"}:
            return self._result(
                "respond_with_caution",
                "elevated_risk",
                conflicts,
                fallback_required=False,
            )

        return self._result(
            "respond",
            "policies_satisfied",
            conflicts,
            fallback_required=False,
        )

    @staticmethod
    def _conflicts(
        *,
        outcome: CognitivePlanOutcomeAssessment | None,
        capability: CognitiveCapabilitySelectionAssessment | None,
        context: CognitiveContextSelectionAssessment | None,
        activation: CognitiveExecutiveActivationAssessment | None,
    ) -> tuple[str, ...]:
        conflicts: list[str] = []
        if outcome is not None and outcome.observed_conflicting_sources:
            conflicts.append("contradictory_sources")
        if outcome is not None and outcome.status is ShadowAssessmentStatus.UNSATISFIED:
            conflicts.append("outcome_unsatisfied")
        if context is not None and context.status is ShadowAssessmentStatus.UNSATISFIED:
            conflicts.append("context_unsatisfied")
        if capability is not None and not capability.compatible:
            conflicts.append("capability_mismatch")
        if activation is not None and activation.fallback_required:
            conflicts.append("activation_fallback")
        return tuple(dict.fromkeys(conflicts))

    @staticmethod
    def _result(
        policy: str,
        decisive_rule: str,
        conflicts: tuple[str, ...],
        *,
        fallback_required: bool,
    ) -> CognitivePolicyResolution:
        rationale = [
            f"policy_resolution:{policy}",
            f"policy_rule:{decisive_rule}",
        ]
        rationale.extend(f"policy_conflict:{code}" for code in conflicts)
        return CognitivePolicyResolution(
            policy=policy,
            decisive_rule=decisive_rule,
            conflict_codes=conflicts,
            rationale_codes=tuple(rationale),
            fallback_required=fallback_required,
        )
