from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from .models import (
    DeviceTrustLevel,
    InMemorySessionContinuityRepository,
    SessionContinuityAction,
    SessionContinuityDecision,
    SessionContinuityPolicy,
    SessionContinuityRepository,
    SessionContinuityRequest,
    SessionContinuityStatus,
)


class DeviceSessionContinuityEngine:
    """Evaluates cross-device session continuity without executing a handoff."""

    def __init__(
        self,
        *,
        repository: SessionContinuityRepository | None = None,
        policy: SessionContinuityPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemorySessionContinuityRepository()
        self.policy = policy or SessionContinuityPolicy()

    @property
    def last_decision(self) -> SessionContinuityDecision | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def evaluate(
        self,
        request: SessionContinuityRequest,
        *,
        now: datetime | None = None,
        required_capabilities: tuple[str, ...] = (),
    ) -> SessionContinuityDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("continuity evaluation timestamp must be aware")
        required = tuple(item.strip().casefold() for item in required_capabilities)
        if any(not item for item in required) or len(required) != len(set(required)):
            raise ValueError("required capabilities must be non-blank and unique")
        self._validate_ownership(request)
        status, action, rationale = self._assess(request, timestamp, required)
        cursor = (
            self._cursor(request) if status is SessionContinuityStatus.READY else None
        )
        result = SessionContinuityDecision(
            request=request,
            status=status,
            action=action,
            eligible_for_handoff=status is SessionContinuityStatus.READY,
            resume_cursor=cursor,
            required_capabilities=required,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(result)
        return result

    def _validate_ownership(self, request: SessionContinuityRequest) -> None:
        owners = (
            request.session.owner,
            request.source.device.owner,
            request.target.device.owner,
        )
        if any(owner.casefold() != request.owner.casefold() for owner in owners):
            raise ValueError("device continuity owner mismatch")
        if request.session.active_device_id != request.source.device.device_id:
            raise ValueError("source device must be the active session device")

    def _assess(
        self,
        request: SessionContinuityRequest,
        now: datetime,
        required: tuple[str, ...],
    ):
        source, target = request.source, request.target
        if source.device.device_id == target.device.device_id:
            if not self.policy.allow_same_device_resume:
                return (
                    SessionContinuityStatus.NOT_APPLICABLE,
                    SessionContinuityAction.NONE,
                    ("source_and_target_are_the_same_device",),
                )
        if not source.available:
            return (
                SessionContinuityStatus.BLOCKED,
                SessionContinuityAction.STAY,
                ("source_device_is_unavailable",),
            )
        if not target.available:
            return (
                SessionContinuityStatus.BLOCKED,
                SessionContinuityAction.STAY,
                ("target_device_is_unavailable",),
            )
        if self.policy.require_authenticated_endpoints and (
            not source.authenticated or not target.authenticated
        ):
            return (
                SessionContinuityStatus.BLOCKED,
                SessionContinuityAction.STAY,
                ("endpoint_authentication_is_required",),
            )
        ages = (
            (now - source.observed_at).total_seconds(),
            (now - target.observed_at).total_seconds(),
        )
        if any(age < 0 for age in ages):
            return (
                SessionContinuityStatus.REVIEW_REQUIRED,
                SessionContinuityAction.CONFIRM,
                ("endpoint_observation_is_in_the_future",),
            )
        if any(age > self.policy.max_observation_age_seconds for age in ages):
            return (
                SessionContinuityStatus.REVIEW_REQUIRED,
                SessionContinuityAction.CONFIRM,
                ("endpoint_observation_is_stale",),
            )
        if target.device.trust_level is DeviceTrustLevel.UNTRUSTED:
            return (
                SessionContinuityStatus.BLOCKED,
                SessionContinuityAction.STAY,
                ("target_device_is_untrusted",),
            )
        if self.policy.require_trusted_target and (
            target.device.trust_level is not DeviceTrustLevel.TRUSTED
        ):
            return (
                SessionContinuityStatus.REVIEW_REQUIRED,
                SessionContinuityAction.CONFIRM,
                ("target_device_requires_confirmation",),
            )
        missing = tuple(
            item for item in required if item not in target.device.capabilities
        )
        if missing:
            return (
                SessionContinuityStatus.BLOCKED,
                SessionContinuityAction.STAY,
                ("target_device_lacks_required_capabilities", *missing),
            )
        return (
            SessionContinuityStatus.READY,
            SessionContinuityAction.RESUME,
            ("device_identity_verified", "session_continuity_is_eligible"),
        )

    @staticmethod
    def _cursor(request: SessionContinuityRequest) -> str:
        return sha256(
            "|".join(
                (
                    request.session.session_id,
                    str(request.session.revision),
                    request.session.conversation_reference_id,
                    request.source.device.device_id,
                    request.target.device.device_id,
                )
            ).encode("utf-8")
        ).hexdigest()
