from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock

from core.executive_event_model import (
    DeliveryRequirement,
    EventPriority,
    ExecutiveEvent,
)

from .models import (
    AttentionDecision,
    AttentionDisposition,
    AttentionReason,
    AttentionState,
    PresenceAttentionContext,
    PresenceAttentionSnapshot,
    PresenceState,
)


class PresenceAttentionManager:
    """Evaluates whether an executive event should interrupt the user.

    M325.4 keeps policy deterministic and in memory. It does not infer presence,
    persist observations, operate sensors, or replace the presentation layer.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._context = PresenceAttentionContext()
        self._update_count = 0
        self._decision_count = 0
        self._delivered_count = 0
        self._deferred_count = 0
        self._silenced_count = 0
        self._last_decision_at: datetime | None = None

    @property
    def context(self) -> PresenceAttentionContext:
        with self._lock:
            return self._context

    @property
    def snapshot(self) -> PresenceAttentionSnapshot:
        with self._lock:
            return PresenceAttentionSnapshot(
                context=self._context,
                update_count=self._update_count,
                decision_count=self._decision_count,
                delivered_count=self._delivered_count,
                deferred_count=self._deferred_count,
                silenced_count=self._silenced_count,
                last_decision_at=self._last_decision_at,
            )

    def update(
        self,
        *,
        presence: PresenceState | str | None = None,
        attention: AttentionState | str | None = None,
        observed_at: datetime | None = None,
    ) -> PresenceAttentionContext:
        timestamp = self._timestamp(observed_at)
        with self._lock:
            self._context = PresenceAttentionContext(
                presence=presence or self._context.presence,
                attention=attention or self._context.attention,
                observed_at=timestamp,
            )
            self._update_count += 1
            return self._context

    def assess(
        self,
        event: ExecutiveEvent,
        *,
        evaluated_at: datetime | None = None,
    ) -> AttentionDecision:
        if not isinstance(event, ExecutiveEvent):
            raise TypeError("attention manager accepts ExecutiveEvent instances only")
        timestamp = self._timestamp(evaluated_at)
        with self._lock:
            context = self._context
            disposition, reason = self._evaluate(event, context)
            self._decision_count += 1
            self._last_decision_at = timestamp
            if disposition is AttentionDisposition.DELIVER:
                self._delivered_count += 1
            elif disposition is AttentionDisposition.DEFER:
                self._deferred_count += 1
            else:
                self._silenced_count += 1
            return AttentionDecision(
                event=event,
                disposition=disposition,
                reason=reason,
                evaluated_at=timestamp,
                context=context,
            )

    def broker_decider(
        self,
        event: ExecutiveEvent,
        evaluated_at: datetime,
    ) -> AttentionDecision:
        return self.assess(event, evaluated_at=evaluated_at)

    @staticmethod
    def _evaluate(
        event: ExecutiveEvent,
        context: PresenceAttentionContext,
    ) -> tuple[AttentionDisposition, AttentionReason]:
        if event.priority is EventPriority.CRITICAL:
            return (
                AttentionDisposition.DELIVER,
                AttentionReason.CRITICAL_OVERRIDE,
            )
        if context.attention is AttentionState.DO_NOT_DISTURB:
            return (
                AttentionDisposition.SILENCE,
                AttentionReason.DO_NOT_DISTURB,
            )
        if context.presence is PresenceState.AWAY:
            if event.delivery_requirement is DeliveryRequirement.BEST_EFFORT:
                return (
                    AttentionDisposition.SILENCE,
                    AttentionReason.BEST_EFFORT_WHILE_AWAY,
                )
            return AttentionDisposition.DEFER, AttentionReason.USER_AWAY
        if context.attention in {
            AttentionState.USER_SPEAKING,
            AttentionState.USER_TYPING,
        }:
            return AttentionDisposition.DEFER, AttentionReason.USER_BUSY
        if context.attention is AttentionState.ROBY_RESPONDING:
            return AttentionDisposition.DEFER, AttentionReason.ROBY_BUSY
        return AttentionDisposition.DELIVER, AttentionReason.AVAILABLE

    @staticmethod
    def _timestamp(value: datetime | None) -> datetime:
        timestamp = value or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("attention time must be timezone-aware")
        return timestamp
