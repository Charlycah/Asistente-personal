from __future__ import annotations

from datetime import datetime, timezone

from core.cross_context_continuity import CrossContextContinuityStatus

from .models import (
    InMemoryUnifiedPermissionConsentRepository,
    UnifiedPermissionConsentAction,
    UnifiedPermissionConsentConfig,
    UnifiedPermissionConsentRepository,
    UnifiedPermissionConsentRequest,
    UnifiedPermissionConsentResult,
    UnifiedPermissionConsentStatus,
)


class UnifiedPermissionConsent:
    """Evaluates explicit permission coverage for one M157 continuity result."""

    def __init__(self, *, repository=None, config=None) -> None:
        self.repository: UnifiedPermissionConsentRepository = (
            repository or InMemoryUnifiedPermissionConsentRepository()
        )
        self.config = config or UnifiedPermissionConsentConfig()

    def evaluate(self, request: UnifiedPermissionConsentRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "unified permission evaluation timestamp must be timezone-aware"
            )
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.evaluation_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "unified_permission_evaluation_not_requested",
                timestamp,
            )
        if (
            len(request.continuity_results) > self.config.maximum_continuity_results
            or len(request.requirements) > self.config.maximum_requirements
            or len(request.grants) > self.config.maximum_grants
        ):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "unified_permission_input_limit_exceeded",
                timestamp,
            )
        if not request.requirements:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_permission_requirements",
                timestamp,
            )
        continuities = {x.continuity_id: x for x in request.continuity_results}.values()
        owned = [
            x
            for x in continuities
            if x.request.owner.casefold() == request.owner.casefold()
        ]
        if request.continuity_results and not owned:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "continuity_owner_mismatch",
                timestamp,
            )
        valid = [
            x
            for x in owned
            if 0
            <= (timestamp - x.created_at).total_seconds()
            <= self.config.maximum_result_age.total_seconds()
            and x.confidence >= self.config.minimum_confidence
            and x.status
            in {
                CrossContextContinuityStatus.CONTINUOUS,
                CrossContextContinuityStatus.CONTINUOUS_PARTIAL,
            }
        ]
        if not valid:
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED if owned else self._status.NOT_APPLICABLE,
                self._action.HOLD if owned else self._action.NONE,
                "continuity_requires_review" if owned else "no_continuity_available",
                timestamp,
            )
        source = max(
            valid,
            key=lambda x: (
                x.status is CrossContextContinuityStatus.CONTINUOUS,
                x.confidence,
                x.created_at,
                x.continuity_id,
            ),
        )
        if (
            source.status is CrossContextContinuityStatus.CONTINUOUS_PARTIAL
            and not self.config.allow_partial_continuity
        ):
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "partial_continuity_requires_review",
                timestamp,
            )
        context_ids = {
            source.source_context.context_id,
            source.target_context.context_id,
        }
        duplicate_keys = [r.key for r in request.requirements]
        if len(set(duplicate_keys)) != len(duplicate_keys):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "duplicate_permission_requirement",
                timestamp,
            )
        if any(g.owner.casefold() != request.owner.casefold() for g in request.grants):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "consent_grant_owner_mismatch",
                timestamp,
            )
        satisfied, missing, denied, matched = [], [], [], []
        for requirement in request.requirements:
            required_contexts = set(requirement.context_ids) or context_ids
            if not required_contexts.issubset(context_ids):
                return self._inactive(
                    request,
                    self._status.BLOCKED,
                    self._action.WITHHOLD,
                    "permission_requirement_context_outside_continuity",
                    timestamp,
                )
            candidates = [
                g
                for g in request.grants
                if g.key == requirement.key
                and g.granted_at <= timestamp
                and (g.expires_at is None or timestamp <= g.expires_at)
                and required_contexts.issubset(set(g.context_ids))
            ]
            if any(g.denied for g in candidates):
                denied.append(requirement)
                continue
            active = [g for g in candidates if not g.revoked]
            if active:
                chosen = max(active, key=lambda g: (g.granted_at, g.grant_id))
                satisfied.append(requirement)
                matched.append(chosen.grant_id)
            elif requirement.explicit_consent_required:
                missing.append(requirement)
            else:
                satisfied.append(requirement)
        if denied:
            return self._active(
                request,
                source,
                self._status.DENIED,
                self._action.DECLARE_DENIAL,
                satisfied,
                missing,
                denied,
                matched,
                "explicit_consent_denied",
                timestamp,
            )
        if missing:
            return self._active(
                request,
                source,
                self._status.CONSENT_REQUIRED,
                self._action.REQUEST_EXPLICIT_CONSENT,
                satisfied,
                missing,
                denied,
                matched,
                "explicit_consent_required",
                timestamp,
            )
        partial = source.status is CrossContextContinuityStatus.CONTINUOUS_PARTIAL or (
            not self.config.require_all_contexts_covered
            and any(
                set(r.context_ids) != context_ids
                for r in request.requirements
                if r.context_ids
            )
        )
        return self._active(
            request,
            source,
            self._status.SATISFIED_PARTIAL if partial else self._status.SATISFIED,
            self._action.DECLARE_PARTIAL if partial else self._action.DECLARE_SATISFIED,
            satisfied,
            missing,
            denied,
            matched,
            "unified_permission_consent_satisfied_partially"
            if partial
            else "unified_permission_consent_satisfied",
            timestamp,
        )

    @property
    def _status(self):
        return UnifiedPermissionConsentStatus

    @property
    def _action(self):
        return UnifiedPermissionConsentAction

    @staticmethod
    def _forbidden():
        return {
            name: False
            for name in (
                "permission_grant_allowed",
                "consent_prompt_allowed",
                "conversation_start_allowed",
                "conversational_activation_allowed",
                "device_handoff_allowed",
                "context_transfer_allowed",
                "channel_selection_allowed",
                "scheduling_allowed",
                "prompt_generation_allowed",
                "response_realization_allowed",
                "provider_call_allowed",
                "automation_allowed",
                "platform_mutation_allowed",
            )
        }

    def _active(
        self,
        request,
        source,
        status,
        action,
        satisfied,
        missing,
        denied,
        matched,
        reason,
        timestamp,
    ):
        return UnifiedPermissionConsentResult(
            request=request,
            status=status,
            action=action,
            selected_continuity=source,
            selected_timing_evaluation=source.selected_timing_evaluation,
            selected_candidate=source.selected_candidate,
            selected_opportunity=source.selected_opportunity,
            satisfied_requirements=tuple(satisfied),
            missing_requirements=tuple(missing),
            denied_requirements=tuple(denied),
            matched_grant_ids=tuple(matched),
            confidence=source.confidence,
            consent_satisfied=status
            in {self._status.SATISFIED, self._status.SATISFIED_PARTIAL},
            partial_consent=status is self._status.SATISFIED_PARTIAL,
            explicit_consent_required=status is self._status.CONSENT_REQUIRED,
            consent_denied=status is self._status.DENIED,
            confirmation_required=status is self._status.CONSENT_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    def _inactive(self, request, status, action, reason, timestamp):
        return UnifiedPermissionConsentResult(
            request=request,
            status=status,
            action=action,
            selected_continuity=None,
            selected_timing_evaluation=None,
            selected_candidate=None,
            selected_opportunity=None,
            satisfied_requirements=(),
            missing_requirements=(),
            denied_requirements=(),
            matched_grant_ids=(),
            confidence=0.0,
            consent_satisfied=False,
            partial_consent=False,
            explicit_consent_required=False,
            consent_denied=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
