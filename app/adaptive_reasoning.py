from __future__ import annotations

from core.adaptive_reasoning import (
    AdaptiveLearningEvidence,
    AdaptiveReasoningContext,
    AdaptiveReasoningDisposition,
    AdaptiveReasoningResult,
    AdaptiveReasoningSnapshot,
)


class AdaptiveReasoning:
    """Governed advisory evaluator for explicit reviewed learning."""

    SCHEMA_VERSION = "m369.5"
    CANONICAL_AUTHORITY = "adaptive_reasoning"
    PARENT_AUTHORITY = "pattern_recognition"

    @property
    def snapshot(self) -> AdaptiveReasoningSnapshot:
        return AdaptiveReasoningSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_authority=self.PARENT_AUTHORITY,
            read_only=True,
            explicit_options_required=True,
            reviewed_patterns_required=True,
            automatic_application=False,
            goal_modification_authorized=False,
            policy_modification_authorized=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def evaluate(
        self,
        *,
        context: AdaptiveReasoningContext,
        evidence: tuple[AdaptiveLearningEvidence, ...],
    ) -> AdaptiveReasoningResult:
        pattern_ids = tuple(item.pattern_id for item in evidence)
        if len(pattern_ids) != len(set(pattern_ids)):
            raise ValueError("adaptive reasoning evidence must be unique")

        applicable = tuple(
            item
            for item in evidence
            if item.subject == context.subject
            and item.suggested_value in context.available_options
        )
        if not applicable:
            return AdaptiveReasoningResult(
                context_id=context.context_id,
                subject=context.subject,
                default_option=context.default_option,
                suggested_option=None,
                pattern_ids=(),
                confidence=0.0,
                disposition=AdaptiveReasoningDisposition.NO_APPLICABLE_LEARNING,
                explanation_codes=("no_applicable_reviewed_pattern",),
                application_authorized=False,
                persistence_authorized=False,
            )

        values = {item.suggested_value for item in applicable}
        if len(values) != 1:
            raise ValueError("adaptive reasoning evidence must support one option")
        ordered = tuple(sorted(applicable, key=lambda item: item.pattern_id))
        confidence = round(
            sum(item.confidence for item in ordered) / len(ordered),
            6,
        )
        return AdaptiveReasoningResult(
            context_id=context.context_id,
            subject=context.subject,
            default_option=context.default_option,
            suggested_option=next(iter(values)),
            pattern_ids=tuple(item.pattern_id for item in ordered),
            confidence=confidence,
            disposition=AdaptiveReasoningDisposition.REVIEW_REQUIRED,
            explanation_codes=(
                "reviewed_pattern_matches_subject",
                "suggestion_is_advisory_only",
            ),
            application_authorized=False,
            persistence_authorized=False,
        )
