from __future__ import annotations

from collections import deque
from datetime import datetime, timezone

from .models import (
    VisionCapability,
    VisionEvent,
    VisionEventType,
    VisionMode,
    VisionObservation,
    VisionPolicy,
    VisionSnapshot,
)


class IntelligentVisionService:
    """Governed visual control plane; it never opens a camera or stores media."""

    def __init__(self, policy: VisionPolicy | None = None) -> None:
        self.policy = policy or VisionPolicy()
        self._active = False
        self._activated_at: datetime | None = None
        self._expires_at: datetime | None = None
        self._queue: deque[VisionObservation] = deque(maxlen=self.policy.queue_limit)
        self._events: list[VisionEvent] = []

    @property
    def snapshot(self) -> VisionSnapshot:
        return VisionSnapshot(
            active=self._active,
            activated_at=self._activated_at,
            expires_at=self._expires_at,
            queued_observation_refs=tuple(item.observation_ref for item in self._queue),
            events=tuple(self._events),
        )

    def process(
        self,
        observation: VisionObservation,
        *,
        now: datetime | None = None,
    ) -> VisionEvent:
        timestamp = now or observation.observed_at
        if timestamp.tzinfo is None:
            raise ValueError("vision processing time must be timezone-aware")
        self._expire_if_needed(timestamp)
        rejection = self._rejection_reasons(observation, timestamp)
        if rejection:
            return self._record(VisionEventType.REJECTED, observation, rejection)
        if self.policy.mode is VisionMode.DISABLED:
            return self._record(
                VisionEventType.REJECTED,
                observation,
                ("vision is disabled by policy",),
            )
        if self.policy.mode is VisionMode.ON_DEMAND and not observation.user_requested:
            return self._record(
                VisionEventType.IGNORED,
                observation,
                ("observation was not explicitly requested",),
            )
        if self.policy.mode is VisionMode.AUTHORIZED_SESSION and not self._active:
            if not observation.user_requested:
                return self._record(
                    VisionEventType.IGNORED,
                    observation,
                    ("authorized vision session is not active",),
                )
            self._active = True
            self._activated_at = timestamp
            self._expires_at = timestamp + self.policy.session_timeout
        elif self._active:
            self._expires_at = timestamp + self.policy.session_timeout

        accepted = tuple(
            item
            for item in observation.requested_capabilities
            if item in self.policy.allowed_capabilities
        )
        if not accepted:
            return self._record(
                VisionEventType.REJECTED,
                observation,
                ("requested visual capabilities are not authorized",),
            )
        self._queue.append(observation)
        rationale = ["visual observation accepted by policy"]
        if observation.raw_media_present and not self.policy.retain_raw_media:
            rationale.append("raw visual media must not be retained")
        if self._active and self._activated_at == timestamp:
            rationale.append("authorized vision session started")
        return self._record(
            VisionEventType.ACCEPTED,
            observation,
            tuple(rationale),
            accepted_capabilities=accepted,
        )

    def pop_observation(self) -> VisionObservation | None:
        return self._queue.popleft() if self._queue else None

    def deactivate(self, *, now: datetime | None = None) -> VisionEvent:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("vision deactivation time must be timezone-aware")
        self._active = False
        self._activated_at = None
        self._expires_at = None
        placeholder = VisionObservation(
            observation_ref="vision-session",
            observed_at=timestamp,
            privacy_level="public",
            requested_capabilities=(VisionCapability.SCENE_DESCRIPTION,),
        )
        return self._record(
            VisionEventType.SESSION_EXPIRED,
            placeholder,
            ("vision session was deactivated",),
        )

    def _rejection_reasons(
        self, observation: VisionObservation, now: datetime
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if self.policy.require_camera_permission and not observation.camera_permission:
            reasons.append("camera permission is missing")
        if (
            self.policy.require_explicit_consent
            and not observation.explicit_user_consent
        ):
            reasons.append("explicit visual consent is missing")
        if observation.confidence < self.policy.minimum_confidence:
            reasons.append("visual confidence is below policy threshold")
        age = now - observation.observed_at
        if age.total_seconds() < 0:
            reasons.append("visual observation timestamp is in the future")
        elif age > self.policy.maximum_observation_age:
            reasons.append("visual observation is stale")
        if observation.privacy_level not in self.policy.allowed_privacy_levels:
            reasons.append("visual privacy level is not authorized")
        if (
            VisionCapability.BIOMETRIC_IDENTIFICATION
            in observation.requested_capabilities
        ):
            reasons.append("biometric identification is prohibited")
        return tuple(reasons)

    def _expire_if_needed(self, now: datetime) -> None:
        if self._expires_at is None or now <= self._expires_at:
            return
        self._active = False
        self._activated_at = None
        self._expires_at = None
        placeholder = VisionObservation(
            observation_ref="vision-session",
            observed_at=now,
            privacy_level="public",
            requested_capabilities=(VisionCapability.SCENE_DESCRIPTION,),
        )
        self._record(
            VisionEventType.SESSION_EXPIRED,
            placeholder,
            ("vision session expired after inactivity",),
        )

    def _record(
        self,
        event_type: VisionEventType,
        observation: VisionObservation,
        rationale: tuple[str, ...],
        *,
        accepted_capabilities: tuple[VisionCapability, ...] = (),
    ) -> VisionEvent:
        event = VisionEvent(
            event_type=event_type,
            observed_at=observation.observed_at,
            observation_ref=observation.observation_ref,
            rationale=rationale,
            accepted_capabilities=accepted_capabilities,
            summary=observation.summary,
        )
        self._events.append(event)
        return event
