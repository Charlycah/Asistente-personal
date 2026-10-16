from __future__ import annotations

from dataclasses import dataclass

from core.capability_registry import CapabilityDescriptor, CapabilityKind

from .models import CognitivePlan, ToolRequirement


@dataclass(frozen=True)
class CognitiveCapabilitySelectionAssessment:
    """Advisory comparison between planned tools and a routed capability."""

    capability_name: str
    capability_kind: str
    matched_requirement: ToolRequirement | None
    compatible: bool
    governed: bool
    provider_agnostic: bool
    rationale_codes: tuple[str, ...]


class CognitiveCapabilitySelectionAssessor:
    """Evaluate a governed selection without authorizing or executing it."""

    _KIND_REQUIREMENTS = {
        CapabilityKind.WEATHER: ToolRequirement.WEATHER,
        CapabilityKind.CALENDAR: ToolRequirement.CALENDAR,
        CapabilityKind.WEB: ToolRequirement.CURRENT_AFFAIRS,
    }

    def assess(
        self,
        plan: CognitivePlan,
        descriptor: CapabilityDescriptor,
        *,
        origin: str,
    ) -> CognitiveCapabilitySelectionAssessment:
        matched = self._requirement_for(descriptor)
        required = set(plan.required_tools)
        compatible = (
            matched in required or ToolRequirement.CAPABILITY_ROUTER in required
        )
        rationale = ["governed_capability_selection_observed"]
        if compatible:
            rationale.append("planned_tool_requirement_matched")
        else:
            rationale.append("planned_tool_requirement_not_matched")
        if origin:
            rationale.append(f"selection_origin:{origin}")
        return CognitiveCapabilitySelectionAssessment(
            capability_name=descriptor.name,
            capability_kind=descriptor.normalized_kind.value,
            matched_requirement=matched,
            compatible=compatible,
            governed=True,
            provider_agnostic=True,
            rationale_codes=tuple(rationale),
        )

    def _requirement_for(
        self,
        descriptor: CapabilityDescriptor,
    ) -> ToolRequirement | None:
        direct = self._KIND_REQUIREMENTS.get(descriptor.normalized_kind)
        if direct is not None:
            return direct
        haystack = " ".join(
            (descriptor.name, descriptor.description, *descriptor.tags)
        ).casefold()
        if "memoria" in haystack or "memory" in haystack:
            return ToolRequirement.MEMORY
        if "actualidad" in haystack or "news" in haystack or "web" in haystack:
            return ToolRequirement.CURRENT_AFFAIRS
        return None
