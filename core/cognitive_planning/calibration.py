from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum

from .executive_activation import (
    CognitiveExecutiveActivationAssessment,
    ExecutiveActivationDecision,
)
from .models import (
    CognitivePlan,
    CognitivePlanOutcomeAssessment,
    PlannedResponseDecision,
    ShadowAssessmentStatus,
)
from .policy_resolution import CognitivePolicyResolution


class CognitiveCalibrationStatus(StrEnum):
    ALIGNED = "aligned"
    PARTIAL = "partial"
    DIVERGED = "diverged"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True)
class CognitiveKernelCalibration:
    """Observed alignment between plan, policy, execution, and outcome."""

    schema_version: str
    status: CognitiveCalibrationStatus
    plan_policy_aligned: bool
    policy_execution_aligned: bool | None
    outcome_aligned: bool | None
    divergence_codes: tuple[str, ...]
    observation_codes: tuple[str, ...]
    score: float

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["divergence_codes"] = list(self.divergence_codes)
        payload["observation_codes"] = list(self.observation_codes)
        return payload


class CognitiveKernelCalibrationEngine:
    """Measure decision alignment without learning or changing behaviour."""

    def calibrate(
        self,
        plan: CognitivePlan,
        resolution: CognitivePolicyResolution,
        *,
        outcome: CognitivePlanOutcomeAssessment | None = None,
        activation: CognitiveExecutiveActivationAssessment | None = None,
    ) -> CognitiveKernelCalibration:
        divergences: list[str] = []
        observations: list[str] = []

        plan_policy_aligned = self._plan_policy_alignment(plan, resolution.policy)
        observations.append(f"plan_policy_aligned:{str(plan_policy_aligned).lower()}")
        if not plan_policy_aligned:
            divergences.append("plan_policy_divergence")

        policy_execution_aligned = self._policy_execution_alignment(
            resolution,
            activation,
        )
        if policy_execution_aligned is None:
            observations.append("execution:not_observed")
        else:
            observations.append(
                "policy_execution_aligned:"
                f"{str(policy_execution_aligned).lower()}"
            )
            if not policy_execution_aligned:
                divergences.append("policy_execution_divergence")

        outcome_aligned = self._outcome_alignment(resolution, outcome)
        if outcome_aligned is None:
            observations.append("outcome:not_observed")
        else:
            observations.append(f"outcome_aligned:{str(outcome_aligned).lower()}")
            if not outcome_aligned:
                divergences.append("outcome_divergence")

        score = self._score(
            plan_policy_aligned,
            policy_execution_aligned,
            outcome_aligned,
        )
        status = self._status(
            divergences=divergences,
            policy_execution_aligned=policy_execution_aligned,
            outcome_aligned=outcome_aligned,
        )
        observations.extend(
            (
                f"policy:{resolution.policy}",
                f"decisive_rule:{resolution.decisive_rule}",
            )
        )
        return CognitiveKernelCalibration(
            schema_version="rp22.03",
            status=status,
            plan_policy_aligned=plan_policy_aligned,
            policy_execution_aligned=policy_execution_aligned,
            outcome_aligned=outcome_aligned,
            divergence_codes=tuple(dict.fromkeys(divergences)),
            observation_codes=tuple(dict.fromkeys(observations)),
            score=score,
        )

    @staticmethod
    def _plan_policy_alignment(plan: CognitivePlan, policy: str) -> bool:
        if plan.response_decision is PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED:
            return policy in {
                "abstain_if_unverified",
                "respond_with_caution",
                "fallback",
            }
        return policy in {"respond", "respond_with_caution", "fallback"}

    @staticmethod
    def _policy_execution_alignment(
        resolution: CognitivePolicyResolution,
        activation: CognitiveExecutiveActivationAssessment | None,
    ) -> bool | None:
        if activation is None:
            return None
        if resolution.fallback_required:
            return activation.decision is ExecutiveActivationDecision.FALLBACK
        if resolution.policy == "abstain_if_unverified":
            return activation.decision is not ExecutiveActivationDecision.EXECUTE
        return activation.decision is not ExecutiveActivationDecision.FALLBACK

    @staticmethod
    def _outcome_alignment(
        resolution: CognitivePolicyResolution,
        outcome: CognitivePlanOutcomeAssessment | None,
    ) -> bool | None:
        if outcome is None:
            return None
        if resolution.policy == "abstain_if_unverified":
            return outcome.observed_abstention or outcome.evidence_satisfied
        if resolution.policy == "fallback":
            return outcome.status is not ShadowAssessmentStatus.UNSATISFIED
        if resolution.policy == "respond_with_caution":
            return outcome.status is not ShadowAssessmentStatus.UNSATISFIED
        return outcome.status in {
            ShadowAssessmentStatus.SATISFIED,
            ShadowAssessmentStatus.NOT_APPLICABLE,
        }

    @staticmethod
    def _score(
        plan_policy_aligned: bool,
        policy_execution_aligned: bool | None,
        outcome_aligned: bool | None,
    ) -> float:
        observed = [plan_policy_aligned]
        if policy_execution_aligned is not None:
            observed.append(policy_execution_aligned)
        if outcome_aligned is not None:
            observed.append(outcome_aligned)
        return round(sum(observed) / len(observed), 3)

    @staticmethod
    def _status(
        *,
        divergences: list[str],
        policy_execution_aligned: bool | None,
        outcome_aligned: bool | None,
    ) -> CognitiveCalibrationStatus:
        if divergences:
            if len(divergences) >= 2:
                return CognitiveCalibrationStatus.DIVERGED
            return CognitiveCalibrationStatus.PARTIAL
        if policy_execution_aligned is None or outcome_aligned is None:
            return CognitiveCalibrationStatus.INCOMPLETE
        return CognitiveCalibrationStatus.ALIGNED
