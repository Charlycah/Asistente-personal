from __future__ import annotations

from dataclasses import dataclass

from .models import CognitivePlan, ContextRequirement, ShadowAssessmentStatus


@dataclass(frozen=True)
class CognitiveContextSelectionAssessment:
    """Advisory comparison between planned and actually selected context."""

    status: ShadowAssessmentStatus
    required_context: tuple[ContextRequirement, ...]
    available_conversation_turns: int
    selected_conversation_turns: int
    conversation_context_required: bool
    conversation_context_satisfied: bool
    personal_memory_required: bool
    context_applied: bool
    over_injection_observed: bool
    rationale_codes: tuple[str, ...]


class CognitiveContextSelectionAssessor:
    """Evaluate contextual selection without changing the selected prompt."""

    def assess(
        self,
        plan: CognitivePlan,
        *,
        available_conversation_turns: int,
        selected_conversation_turns: int,
    ) -> CognitiveContextSelectionAssessment:
        required = tuple(plan.required_context)
        conversation_required = ContextRequirement.CONVERSATION in required
        personal_memory_required = ContextRequirement.PERSONAL_MEMORY in required
        context_applied = selected_conversation_turns > 0
        conversation_satisfied = not conversation_required or context_applied
        over_injection = not conversation_required and context_applied

        rationale = ["context_selection_observed"]
        if conversation_required:
            rationale.append(
                "planned_conversation_context_observed"
                if conversation_satisfied
                else "planned_conversation_context_missing"
            )
        elif over_injection:
            rationale.append("unplanned_conversation_context_observed")
        else:
            rationale.append("conversation_context_not_required")
        if personal_memory_required:
            rationale.append("personal_memory_required_outside_context_gateway")

        applicable = (
            conversation_required or personal_memory_required or context_applied
        )
        if not applicable:
            status = ShadowAssessmentStatus.NOT_APPLICABLE
        elif conversation_satisfied and not over_injection:
            status = (
                ShadowAssessmentStatus.PARTIAL
                if personal_memory_required
                else ShadowAssessmentStatus.SATISFIED
            )
        elif conversation_satisfied:
            status = ShadowAssessmentStatus.PARTIAL
        else:
            status = ShadowAssessmentStatus.UNSATISFIED

        return CognitiveContextSelectionAssessment(
            status=status,
            required_context=required,
            available_conversation_turns=available_conversation_turns,
            selected_conversation_turns=selected_conversation_turns,
            conversation_context_required=conversation_required,
            conversation_context_satisfied=conversation_satisfied,
            personal_memory_required=personal_memory_required,
            context_applied=context_applied,
            over_injection_observed=over_injection,
            rationale_codes=tuple(rationale),
        )
