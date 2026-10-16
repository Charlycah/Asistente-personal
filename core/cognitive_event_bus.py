from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from threading import RLock

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.global_cognitive_state import (
    GlobalCognitiveState,
    GlobalCognitiveStateEngine,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class CognitiveEventType(str, Enum):
    STATE_CHANGED = "state_changed"
    SIGNAL_PUBLISHED = "signal_published"
    CONSTRAINT_RAISED = "constraint_raised"
    HEALTH_CHANGED = "health_changed"


class CognitiveEventDeliveryStatus(str, Enum):
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass(frozen=True)
class CognitiveEvent:
    owner: str
    session_id: str
    event_type: CognitiveEventType | str
    source_domain: CognitiveBlackboardDomain | str
    topic: str
    value: str
    confidence: float = 1.0
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        event_type = CognitiveEventType(self.event_type)
        source_domain = CognitiveBlackboardDomain(self.source_domain)
        topic = self.topic.strip()
        value = self.value.strip()
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("cognitive event identity must be complete")
        if not topic or not value:
            raise ValueError("cognitive event topic and value must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("cognitive event time must be timezone-aware")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("cognitive event confidence must be between zero and one")
        if len(set(references)) != len(references):
            raise ValueError("cognitive event references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    event_type.value,
                    source_domain.value,
                    topic,
                    value,
                    f"{self.confidence:.3f}",
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.event_id and self.event_id != expected:
            raise ValueError("cognitive event id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "source_domain", source_domain)
        object.__setattr__(self, "topic", topic)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "event_id", expected)


@dataclass(frozen=True)
class CognitiveEventSubscription:
    owner: str
    session_id: str
    event_types: tuple[CognitiveEventType | str, ...] = ()
    topics: tuple[str, ...] = ()
    source_domains: tuple[CognitiveBlackboardDomain | str, ...] = ()
    subscription_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        event_types = tuple(CognitiveEventType(item) for item in self.event_types)
        topics = tuple(item.strip() for item in self.topics if item.strip())
        domains = tuple(CognitiveBlackboardDomain(item) for item in self.source_domains)
        if not owner or not session_id:
            raise ValueError("cognitive event subscription identity must be complete")
        if len(set(event_types)) != len(event_types):
            raise ValueError("subscription event types must be unique")
        if len({item.casefold() for item in topics}) != len(topics):
            raise ValueError("subscription topics must be unique")
        if len(set(domains)) != len(domains):
            raise ValueError("subscription source domains must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    *(item.value for item in event_types),
                    *(item.casefold() for item in topics),
                    *(item.value for item in domains),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.subscription_id and self.subscription_id != expected:
            raise ValueError("cognitive event subscription id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "event_types", event_types)
        object.__setattr__(self, "topics", topics)
        object.__setattr__(self, "source_domains", domains)
        object.__setattr__(self, "subscription_id", expected)

    def matches(self, event: CognitiveEvent) -> bool:
        if self.owner.casefold() != event.owner.casefold():
            return False
        if self.session_id != event.session_id:
            return False
        if self.event_types and event.event_type not in self.event_types:
            return False
        if self.topics and event.topic.casefold() not in {
            item.casefold() for item in self.topics
        }:
            return False
        return not self.source_domains or event.source_domain in self.source_domains


@dataclass(frozen=True)
class CognitiveEventDelivery:
    event_id: str
    subscription_id: str
    status: CognitiveEventDeliveryStatus | str
    error: str = ""

    def __post_init__(self) -> None:
        event_id = self.event_id.strip()
        subscription_id = self.subscription_id.strip()
        status = CognitiveEventDeliveryStatus(self.status)
        error = self.error.strip()
        if not event_id or not subscription_id:
            raise ValueError("cognitive event delivery identity must be complete")
        if status is CognitiveEventDeliveryStatus.DELIVERED and error:
            raise ValueError("successful delivery cannot contain an error")
        object.__setattr__(self, "event_id", event_id)
        object.__setattr__(self, "subscription_id", subscription_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "error", error)


CognitiveEventHandler = Callable[[CognitiveEvent], None]


class CognitiveEventBus:
    """Dispatch bounded cognitive events without granting execution authority."""

    def __init__(self, *, maximum_events_per_session: int = 256) -> None:
        if maximum_events_per_session < 1:
            raise ValueError("event bus maximum events must be positive")
        self.maximum_events_per_session = maximum_events_per_session
        self._events: dict[tuple[str, str], list[CognitiveEvent]] = {}
        self._subscriptions: dict[
            str, tuple[CognitiveEventSubscription, CognitiveEventHandler]
        ] = {}
        self._lock = RLock()
        self.last_event: CognitiveEvent | None = None
        self.last_deliveries: tuple[CognitiveEventDelivery, ...] = ()

    def subscribe(
        self,
        subscription: CognitiveEventSubscription,
        handler: CognitiveEventHandler,
    ) -> CognitiveEventSubscription:
        if not callable(handler):
            raise TypeError("cognitive event handler must be callable")
        with self._lock:
            self._subscriptions[subscription.subscription_id] = (
                subscription,
                handler,
            )
        return subscription

    def unsubscribe(self, subscription_id: str) -> bool:
        with self._lock:
            return self._subscriptions.pop(subscription_id.strip(), None) is not None

    def publish(self, event: CognitiveEvent) -> tuple[CognitiveEventDelivery, ...]:
        identity = (event.owner.casefold(), event.session_id)
        with self._lock:
            bucket = self._events.setdefault(identity, [])
            is_new = not any(item.event_id == event.event_id for item in bucket)
            if is_new:
                bucket.append(event)
                overflow = len(bucket) - self.maximum_events_per_session
                if overflow > 0:
                    del bucket[:overflow]
            subscriptions = tuple(self._subscriptions.values())
        if not is_new:
            self.last_event = event
            self.last_deliveries = ()
            return ()
        deliveries: list[CognitiveEventDelivery] = []
        for subscription, handler in subscriptions:
            if not subscription.matches(event):
                continue
            try:
                handler(event)
            except Exception as exc:  # consumer failure must remain contained
                deliveries.append(
                    CognitiveEventDelivery(
                        event_id=event.event_id,
                        subscription_id=subscription.subscription_id,
                        status=CognitiveEventDeliveryStatus.FAILED,
                        error=type(exc).__name__,
                    )
                )
            else:
                deliveries.append(
                    CognitiveEventDelivery(
                        event_id=event.event_id,
                        subscription_id=subscription.subscription_id,
                        status=CognitiveEventDeliveryStatus.DELIVERED,
                    )
                )
        self.last_event = event
        self.last_deliveries = tuple(deliveries)
        return self.last_deliveries

    def events(
        self,
        *,
        owner: str,
        session_id: str,
        event_types: tuple[CognitiveEventType | str, ...] = (),
        topics: tuple[str, ...] = (),
    ) -> tuple[CognitiveEvent, ...]:
        identity = (owner.strip().casefold(), session_id.strip())
        normalized_types = {CognitiveEventType(item) for item in event_types}
        normalized_topics = {item.strip().casefold() for item in topics if item.strip()}
        with self._lock:
            events = tuple(self._events.get(identity, ()))
        if normalized_types:
            events = tuple(
                item for item in events if item.event_type in normalized_types
            )
        if normalized_topics:
            events = tuple(
                item for item in events if item.topic.casefold() in normalized_topics
            )
        return events

    def clear_session(self, *, owner: str, session_id: str) -> int:
        identity = (owner.strip().casefold(), session_id.strip())
        with self._lock:
            events = self._events.pop(identity, [])
        return len(events)


@dataclass(frozen=True)
class CognitiveEventBusRuntimeContributor:
    bus: CognitiveEventBus
    state_engine: GlobalCognitiveStateEngine
    blackboard: UnifiedCognitiveBlackboard
    name: str = "cognitive_event_bus"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del text, request
        state = self._resolve_state(owner=owner, session_id=session_id, now=now)
        event_type = (
            CognitiveEventType.CONSTRAINT_RAISED
            if state.constraints
            else CognitiveEventType.STATE_CHANGED
        )
        event = CognitiveEvent(
            owner=owner,
            session_id=session_id,
            event_type=event_type,
            source_domain=CognitiveBlackboardDomain.SYSTEM,
            topic="global_cognitive_state",
            value=state.readiness.value,
            confidence=state.average_confidence,
            source_reference_ids=(state.state_id, *state.source_reference_ids),
            created_at=now,
        )
        deliveries = self.bus.publish(event)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.SIGNAL,
                key="cognitive_event_bus_last_event",
                value=event.event_type.value,
                confidence=event.confidence,
                source_reference_ids=(event.event_id, *event.source_reference_ids),
                created_at=now,
            )
        )
        failed = sum(
            item.status is CognitiveEventDeliveryStatus.FAILED for item in deliveries
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Bus de eventos cognitivos: "
                f"{event.event_type.value}; tema {event.topic}; "
                f"entregas {len(deliveries)}; fallos contenidos {failed}.",
            ),
            reference_ids=(entry.entry_id, event.event_id, *event.source_reference_ids),
            rationale=(
                "m202_global_state_eventized",
                "cognitive_event_dispatched",
                "consumer_failures_contained",
            ),
        )

    def _resolve_state(
        self, *, owner: str, session_id: str, now: datetime
    ) -> GlobalCognitiveState:
        state = self.state_engine.last_state
        if (
            state is None
            or state.owner != owner.strip()
            or state.session_id != session_id.strip()
        ):
            self.state_engine.bind_blackboard(self.blackboard)
            state = self.state_engine.assess(
                owner=owner,
                session_id=session_id,
                now=now,
            )
        return state
