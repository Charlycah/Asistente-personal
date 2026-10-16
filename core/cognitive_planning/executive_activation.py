from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from core.capability_registry import CapabilityDescriptor, CapabilityRisk

from .capability_selection import CognitiveCapabilitySelectionAssessor
from .models import CognitivePlan, ToolRequirement


class ExecutiveActivationDecision(StrEnum):
    EXECUTE = "execute"
    SKIP = "skip"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class CognitiveExecutiveActivationAssessment:
    decision: ExecutiveActivationDecision
    capability_name: str
    plan_valid: bool
    plan_confident: bool
    capability_compatible: bool | None
    fallback_required: bool
    rationale_codes: tuple[str, ...]


class CognitiveExecutiveActivationPolicy:
    """Apply only narrow, reversible planner decisions at governed boundaries."""

    _CONFIDENT_RATIONALES = {
        "weather_information_detected",
        "current_information_detected",
        "calendar_information_detected",
        "memory_dependency_detected",
        "action_request_detected",
    }

    def __init__(
        self,
        capability_assessor: CognitiveCapabilitySelectionAssessor | None = None,
    ) -> None:
        self.capability_assessor = (
            capability_assessor or CognitiveCapabilitySelectionAssessor()
        )

    def assess_semantic_candidate(
        self,
        plan: CognitivePlan | None,
        descriptor: CapabilityDescriptor,
    ) -> CognitiveExecutiveActivationAssessment:
        if plan is None:
            return self._fallback(descriptor, "executive_plan_missing")
        if not self._valid(plan):
            return self._fallback(descriptor, "executive_plan_invalid")
        if not self._confident(plan):
            return self._fallback(descriptor, "executive_plan_not_confident")
        if not descriptor.enabled:
            return self._fallback(descriptor, "capability_disabled")
        if descriptor.requires_confirmation or descriptor.normalized_risk not in {
            CapabilityRisk.LOW,
            CapabilityRisk.MEDIUM,
        }:
            return self._fallback(descriptor, "capability_not_safe_for_auto_activation")

        selection = self.capability_assessor.assess(
            plan,
            descriptor,
            origin="executive_activation",
        )
        if selection.compatible:
            return CognitiveExecutiveActivationAssessment(
                decision=ExecutiveActivationDecision.EXECUTE,
                capability_name=descriptor.name,
                plan_valid=True,
                plan_confident=True,
                capability_compatible=True,
                fallback_required=False,
                rationale_codes=(
                    "controlled_executive_activation",
                    "planned_capability_compatible",
                ),
            )
        return CognitiveExecutiveActivationAssessment(
            decision=ExecutiveActivationDecision.SKIP,
            capability_name=descriptor.name,
            plan_valid=True,
            plan_confident=True,
            capability_compatible=False,
            fallback_required=False,
            rationale_codes=(
                "controlled_executive_activation",
                "incompatible_semantic_candidate_skipped",
            ),
        )

    @staticmethod
    def _valid(plan: CognitivePlan) -> bool:
        return bool(
            plan.required_context and plan.required_tools and plan.rationale_codes
        )

    def _confident(self, plan: CognitivePlan) -> bool:
        concrete_tools = {
            item for item in plan.required_tools if item is not ToolRequirement.NONE
        }
        return (
            len(concrete_tools) == 1
            and bool(set(plan.rationale_codes) & self._CONFIDENT_RATIONALES)
        )

    @staticmethod
    def _fallback(
        descriptor: CapabilityDescriptor,
        rationale: str,
    ) -> CognitiveExecutiveActivationAssessment:
        return CognitiveExecutiveActivationAssessment(
            decision=ExecutiveActivationDecision.FALLBACK,
            capability_name=descriptor.name,
            plan_valid=False,
            plan_confident=False,
            capability_compatible=None,
            fallback_required=True,
            rationale_codes=("legacy_execution_fallback", rationale),
        )
