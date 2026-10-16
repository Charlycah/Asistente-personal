from __future__ import annotations

from datetime import datetime, timezone

from core.companion_reliability_model import CompanionReliabilityStatus
from core.cross_context_continuity import CrossContextContinuityStatus
from core.living_conversation_conversation_timing_evaluation import (
    LivingConversationConversationTimingEvaluationStatus,
)
from core.long_term_experience_evaluation import LongTermExperienceStatus
from core.unified_permission_consent import UnifiedPermissionConsentStatus

from .models import (
    InMemoryUnifiedCompanionIntegrationRepository,
    UnifiedCompanionIntegrationAction,
    UnifiedCompanionIntegrationConfig,
    UnifiedCompanionIntegrationRepository,
    UnifiedCompanionIntegrationRequest,
    UnifiedCompanionIntegrationResult,
    UnifiedCompanionIntegrationStatus,
)


class UnifiedCompanionIntegration:
    """Closes the governed companion pipeline without activating or executing it."""

    def __init__(
        self,
        *,
        config: UnifiedCompanionIntegrationConfig | None = None,
        repository: UnifiedCompanionIntegrationRepository | None = None,
    ) -> None:
        self.config = config or UnifiedCompanionIntegrationConfig()
        self.repository = repository or InMemoryUnifiedCompanionIntegrationRepository()

    @property
    def last_integration(self) -> UnifiedCompanionIntegrationResult | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def integrate(
        self,
        request: UnifiedCompanionIntegrationRequest,
        *,
        now: datetime | None = None,
    ) -> UnifiedCompanionIntegrationResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("integration timestamp must be timezone-aware")
        experience = request.experience_result
        if not request.integration_requested:
            result = self._inactive(
                request,
                UnifiedCompanionIntegrationStatus.NOT_APPLICABLE,
                UnifiedCompanionIntegrationAction.NONE,
                "unified_companion_integration_not_requested",
                timestamp,
            )
        elif experience.status is LongTermExperienceStatus.NOT_APPLICABLE:
            result = self._inactive(
                request,
                UnifiedCompanionIntegrationStatus.NOT_APPLICABLE,
                UnifiedCompanionIntegrationAction.NONE,
                "experience_not_applicable",
                timestamp,
            )
        elif experience.status is LongTermExperienceStatus.BLOCKED:
            result = self._inactive(
                request,
                UnifiedCompanionIntegrationStatus.BLOCKED,
                UnifiedCompanionIntegrationAction.WITHHOLD,
                "experience_blocked",
                timestamp,
            )
        elif experience.status in {
            LongTermExperienceStatus.INSUFFICIENT,
            LongTermExperienceStatus.REVIEW_REQUIRED,
        }:
            result = self._inactive(
                request,
                UnifiedCompanionIntegrationStatus.BLOCKED,
                UnifiedCompanionIntegrationAction.WITHHOLD,
                "experience_lineage_unavailable",
                timestamp,
            )
        else:
            result = self._integrate_active(request, timestamp)
        self.repository.add(result)
        return result

    def _integrate_active(self, request, timestamp):
        experience = request.experience_result
        reliability = experience.selected_reliability_result
        permission = experience.selected_permission_result
        continuity = experience.selected_continuity
        timing = experience.selected_timing_evaluation
        candidate = experience.selected_candidate
        opportunity = experience.selected_opportunity
        assert (
            reliability
            and permission
            and continuity
            and timing
            and candidate
            and opportunity
        )
        confidence = round(
            min(
                experience.confidence,
                reliability.confidence,
                permission.confidence,
                continuity.confidence,
                timing.confidence,
                candidate.confidence,
                opportunity.confidence,
            ),
            6,
        )
        if confidence < self.config.minimum_confidence:
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.HOLD,
                UnifiedCompanionIntegrationAction.HOLD,
                "unified_companion_confidence_below_threshold",
            )
        elif permission.status not in {
            UnifiedPermissionConsentStatus.SATISFIED,
            UnifiedPermissionConsentStatus.SATISFIED_PARTIAL,
        }:
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.HOLD,
                UnifiedCompanionIntegrationAction.HOLD,
                "permission_or_consent_not_satisfied",
            )
        elif continuity.status not in {
            CrossContextContinuityStatus.CONTINUOUS,
            CrossContextContinuityStatus.CONTINUOUS_PARTIAL,
        }:
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.HOLD,
                UnifiedCompanionIntegrationAction.HOLD,
                "cross_context_continuity_not_available",
            )
        elif timing.status not in {
            LivingConversationConversationTimingEvaluationStatus.TIMELY,
            LivingConversationConversationTimingEvaluationStatus.TIMELY_PARTIAL,
        }:
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.HOLD,
                UnifiedCompanionIntegrationAction.HOLD,
                "conversation_timing_not_timely",
            )
        elif reliability.status is CompanionReliabilityStatus.UNAVAILABLE:
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.HOLD,
                UnifiedCompanionIntegrationAction.HOLD,
                "companion_path_unavailable",
            )
        elif experience.status is LongTermExperienceStatus.NEGATIVE:
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.HOLD,
                UnifiedCompanionIntegrationAction.HOLD,
                "long_term_experience_negative",
            )
        elif (
            experience.status is LongTermExperienceStatus.MIXED
            and not self.config.allow_mixed_experience
        ):
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.HOLD,
                UnifiedCompanionIntegrationAction.HOLD,
                "mixed_experience_requires_hold",
            )
        elif (
            experience.status is LongTermExperienceStatus.MIXED
            or reliability.status is CompanionReliabilityStatus.DEGRADED
            or permission.status is UnifiedPermissionConsentStatus.SATISFIED_PARTIAL
            or continuity.status is CrossContextContinuityStatus.CONTINUOUS_PARTIAL
            or timing.status
            is LivingConversationConversationTimingEvaluationStatus.TIMELY_PARTIAL
        ):
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.DEGRADED,
                UnifiedCompanionIntegrationAction.DECLARE_DEGRADED,
                "unified_companion_available_with_degradation",
            )
        else:
            status, action, reason = (
                UnifiedCompanionIntegrationStatus.READY,
                UnifiedCompanionIntegrationAction.DECLARE_READY,
                "unified_companion_ready",
            )
        refs = (
            experience.evaluation_id,
            reliability.reliability_id,
            permission.evaluation_id,
            continuity.continuity_id,
            timing.timing_evaluation_id,
            candidate.candidate_id,
            opportunity.opportunity_id,
        )
        return UnifiedCompanionIntegrationResult(
            request=request,
            status=status,
            action=action,
            selected_experience_result=experience,
            selected_reliability_result=reliability,
            selected_permission_result=permission,
            selected_continuity=continuity,
            selected_timing_evaluation=timing,
            selected_candidate=candidate,
            selected_opportunity=opportunity,
            stage_reference_ids=refs,
            confidence=confidence,
            ready=status is UnifiedCompanionIntegrationStatus.READY,
            degraded=status is UnifiedCompanionIntegrationStatus.DEGRADED,
            hold=status is UnifiedCompanionIntegrationStatus.HOLD,
            confirmation_required=status is UnifiedCompanionIntegrationStatus.HOLD,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    @staticmethod
    def _forbidden():
        return {
            name: False
            for name in (
                "activation_allowed",
                "conversation_start_allowed",
                "device_selection_allowed",
                "channel_selection_allowed",
                "context_transfer_allowed",
                "scheduling_allowed",
                "prompt_generation_allowed",
                "response_realization_allowed",
                "provider_call_allowed",
                "automation_allowed",
                "platform_mutation_allowed",
            )
        }

    def _inactive(self, request, status, action, reason, timestamp):
        return UnifiedCompanionIntegrationResult(
            request=request,
            status=status,
            action=action,
            selected_experience_result=None,
            selected_reliability_result=None,
            selected_permission_result=None,
            selected_continuity=None,
            selected_timing_evaluation=None,
            selected_candidate=None,
            selected_opportunity=None,
            stage_reference_ids=(),
            confidence=0,
            ready=False,
            degraded=False,
            hold=False,
            confirmation_required=status is UnifiedCompanionIntegrationStatus.BLOCKED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
