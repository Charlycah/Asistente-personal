from __future__ import annotations

from dataclasses import dataclass

from .capability_selection import CognitiveCapabilitySelectionAssessment
from .context_selection import CognitiveContextSelectionAssessment
from .executive_activation import CognitiveExecutiveActivationAssessment
from .models import CognitivePlan, CognitivePlanOutcomeAssessment
from .policy_resolution import CognitivePolicyResolution


@dataclass(frozen=True)
class CognitiveDecisionExplanation:
    """Stable, serializable explanation of one kernel decision."""

    schema_version: str
    decision: str
    decisive_rule: str
    evaluated_rules: tuple[str, ...]
    conflict_codes: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    narrative: str
    fallback_required: bool

    def as_dict(self) -> dict[str, object]:
        """Return a deterministic transport representation."""

        return {
            "schema_version": self.schema_version,
            "decision": self.decision,
            "decisive_rule": self.decisive_rule,
            "evaluated_rules": list(self.evaluated_rules),
            "conflict_codes": list(self.conflict_codes),
            "evidence_codes": list(self.evidence_codes),
            "narrative": self.narrative,
            "fallback_required": self.fallback_required,
        }


class CognitiveDecisionExplainer:
    """Explain kernel output without changing resolution or execution."""

    SCHEMA_VERSION = "rp22.02"

    def explain(
        self,
        plan: CognitivePlan,
        resolution: CognitivePolicyResolution,
        *,
        risk: str,
        confidence: str,
        outcome: CognitivePlanOutcomeAssessment | None = None,
        capability: CognitiveCapabilitySelectionAssessment | None = None,
        context: CognitiveContextSelectionAssessment | None = None,
        activation: CognitiveExecutiveActivationAssessment | None = None,
    ) -> CognitiveDecisionExplanation:
        evaluated_rules = self._evaluated_rules(
            plan=plan,
            outcome=outcome,
            capability=capability,
            context=context,
            activation=activation,
            risk=risk,
            confidence=confidence,
        )
        evidence_codes = self._evidence_codes(
            plan=plan,
            outcome=outcome,
            capability=capability,
            context=context,
            activation=activation,
            risk=risk,
            confidence=confidence,
        )
        narrative = self._narrative(
            resolution=resolution,
            risk=risk,
            confidence=confidence,
        )
        return CognitiveDecisionExplanation(
            schema_version=self.SCHEMA_VERSION,
            decision=resolution.policy,
            decisive_rule=resolution.decisive_rule,
            evaluated_rules=evaluated_rules,
            conflict_codes=resolution.conflict_codes,
            evidence_codes=evidence_codes,
            narrative=narrative,
            fallback_required=resolution.fallback_required,
        )

    @staticmethod
    def _evaluated_rules(
        *,
        plan: CognitivePlan,
        outcome: CognitivePlanOutcomeAssessment | None,
        capability: CognitiveCapabilitySelectionAssessment | None,
        context: CognitiveContextSelectionAssessment | None,
        activation: CognitiveExecutiveActivationAssessment | None,
        risk: str,
        confidence: str,
    ) -> tuple[str, ...]:
        rules = [
            f"planned_response:{plan.response_decision.value}",
            f"risk:{risk}",
            f"confidence:{confidence}",
        ]
        if outcome is not None:
            rules.append(f"outcome:{outcome.status.value}")
            rules.append(f"evidence_satisfied:{str(outcome.evidence_satisfied).lower()}")
        if context is not None:
            rules.append(f"context:{context.status.value}")
        if capability is not None:
            rules.append(f"capability_compatible:{str(capability.compatible).lower()}")
        if activation is not None:
            rules.append(
                f"activation_fallback:{str(activation.fallback_required).lower()}"
            )
        return tuple(dict.fromkeys(rules))

    @staticmethod
    def _evidence_codes(
        *,
        plan: CognitivePlan,
        outcome: CognitivePlanOutcomeAssessment | None,
        capability: CognitiveCapabilitySelectionAssessment | None,
        context: CognitiveContextSelectionAssessment | None,
        activation: CognitiveExecutiveActivationAssessment | None,
        risk: str,
        confidence: str,
    ) -> tuple[str, ...]:
        codes = list(plan.rationale_codes)
        for assessment in (outcome, capability, context, activation):
            if assessment is not None:
                codes.extend(assessment.rationale_codes)
        codes.extend((f"kernel_risk:{risk}", f"kernel_confidence:{confidence}"))
        return tuple(dict.fromkeys(codes))

    @staticmethod
    def _narrative(
        *,
        resolution: CognitivePolicyResolution,
        risk: str,
        confidence: str,
    ) -> str:
        conflicts = ", ".join(resolution.conflict_codes) or "none"
        return (
            f"Decision '{resolution.policy}' selected by rule "
            f"'{resolution.decisive_rule}' with risk '{risk}', confidence "
            f"'{confidence}', and conflicts '{conflicts}'."
        )
