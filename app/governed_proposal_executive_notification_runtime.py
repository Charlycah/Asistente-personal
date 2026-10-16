from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from app.governed_presented_proposal_review_transport import (
    GovernedPresentedProposalReviewTransport,
)
from core.executive_event_model import (
    DeliveryRequirement,
    EventPriority,
    EventSource,
    GenericTextEvent,
)
from core.executive_notification_broker import BrokeredEvent
from domain.governed_proposal import GovernedProposal, ProposalPriority, ProposalState


class GovernedProposalGateway(Protocol):
    def next_presentable_governed_proposal(self, context=None, *, observed_at=None): ...

    def offer_governed_proposal(self, proposal_id: str, *, observed_at=None): ...


class ExecutiveRuntimePort(Protocol):
    broker: object

    def publish(self, event: GenericTextEvent): ...


@dataclass(frozen=True)
class GovernedProposalExecutiveNotificationPolicy:
    poll_interval: timedelta = timedelta(seconds=2)

    def __post_init__(self) -> None:
        if self.poll_interval.total_seconds() <= 0:
            raise ValueError("proposal notification poll interval must be positive")


@dataclass(frozen=True)
class GovernedProposalExecutiveNotificationSnapshot:
    running: bool
    cycles: int
    submitted: int
    offered: int
    failures: int
    inflight: int


class GovernedProposalExecutiveNotificationRuntime:
    """Productive adapter from governed proposals to the existing executive spine.

    This runtime owns no proposal, initiative, presentation, notification, or execution
    authority. It asks the canonical proposal presentation policy for one eligible
    proposal, publishes that proposal as an executive event, and moves the proposal to
    OFFERED only after the existing ExecutiveNotificationBroker actually dispatches it.
    """

    _CORRELATION_PREFIX = "governed-proposal:"

    def __init__(
        self,
        *,
        gateway: GovernedProposalGateway,
        executive_runtime: ExecutiveRuntimePort,
        policy: GovernedProposalExecutiveNotificationPolicy | None = None,
        proposal_review_transport: (
            GovernedPresentedProposalReviewTransport | None
        ) = None,
    ) -> None:
        self.gateway = gateway
        self.executive_runtime = executive_runtime
        self.policy = policy or GovernedProposalExecutiveNotificationPolicy()
        self._proposal_review_transport = proposal_review_transport
        self._running = False
        self._cycles = 0
        self._submitted = 0
        self._offered = 0
        self._failures = 0
        self._inflight: set[str] = set()
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def snapshot(self) -> GovernedProposalExecutiveNotificationSnapshot:
        with self._lock:
            return GovernedProposalExecutiveNotificationSnapshot(
                running=self._running,
                cycles=self._cycles,
                submitted=self._submitted,
                offered=self._offered,
                failures=self._failures,
                inflight=len(self._inflight),
            )

    def start(self) -> None:
        if self._running:
            return
        self._stop.clear()
        self.executive_runtime.broker.subscribe(self._on_broker_dispatch)
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            name="roby-governed-proposal-notification-runtime",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if not self._running:
            return
        self._stop.set()
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=max(1.0, self.policy.poll_interval.total_seconds() * 2))
        self.executive_runtime.broker.unsubscribe(self._on_broker_dispatch)
        self._thread = None
        self._running = False

    def tick(self, *, now: datetime | None = None) -> str | None:
        observed_at = now or datetime.now(timezone.utc)
        if observed_at.tzinfo is None:
            raise ValueError("proposal notification time must be timezone-aware")
        with self._lock:
            self._cycles += 1
        try:
            decision = self.gateway.next_presentable_governed_proposal(
                observed_at=observed_at
            )
            if decision is None:
                return None
            proposal = decision.proposal
            if proposal.state is not ProposalState.PENDING:
                return None
            with self._lock:
                if proposal.proposal_id in self._inflight:
                    return None
            result = self.executive_runtime.publish(
                self._event_for(proposal, decision.effective_priority)
            )
            if not bool(getattr(result, "accepted", False)):
                return None
            with self._lock:
                self._inflight.add(proposal.proposal_id)
                self._submitted += 1
            return proposal.proposal_id
        except Exception:
            with self._lock:
                self._failures += 1
            return None

    def _on_broker_dispatch(self, brokered: BrokeredEvent) -> None:
        correlation_id = brokered.event.correlation_id
        if correlation_id is None or not correlation_id.startswith(
            self._CORRELATION_PREFIX
        ):
            return
        proposal_id = correlation_id[len(self._CORRELATION_PREFIX) :]
        with self._lock:
            if proposal_id not in self._inflight:
                return
        observed_at = brokered.selected_at or datetime.now(timezone.utc)
        try:
            self.gateway.offer_governed_proposal(
                proposal_id,
                observed_at=observed_at,
            )
        except Exception:
            with self._lock:
                self._failures += 1
            raise
        if self._proposal_review_transport is not None:
            self._proposal_review_transport.retain_presented_proposal_reference(
                proposal_id
            )
        with self._lock:
            self._inflight.discard(proposal_id)
            self._offered += 1

    def _run(self) -> None:
        interval = self.policy.poll_interval.total_seconds()
        while not self._stop.is_set():
            self.tick(now=datetime.now(timezone.utc))
            self._stop.wait(interval)

    @classmethod
    def _event_for(
        cls,
        proposal: GovernedProposal,
        effective_priority: ProposalPriority,
    ) -> GenericTextEvent:
        return GenericTextEvent(
            text=cls._render(proposal),
            source=EventSource.SYSTEM,
            priority=cls._executive_priority(effective_priority),
            delivery_requirement=DeliveryRequirement.PRESENTATION_REQUIRED,
            occurred_at=proposal.created_at,
            expires_at=proposal.expires_at,
            correlation_id=f"{cls._CORRELATION_PREFIX}{proposal.proposal_id}",
            payload={
                "proposal_id": proposal.proposal_id,
                "proposal_category": proposal.category,
                "proposal_source": proposal.source_id,
            },
        )

    @staticmethod
    def _render(proposal: GovernedProposal) -> str:
        title = proposal.title.strip()
        summary = proposal.summary.strip()
        if summary.casefold().startswith(title.casefold()):
            return summary
        return f"{title}: {summary}"

    @staticmethod
    def _executive_priority(priority: ProposalPriority) -> EventPriority:
        return {
            ProposalPriority.LOW: EventPriority.LOW,
            ProposalPriority.NORMAL: EventPriority.NORMAL,
            ProposalPriority.HIGH: EventPriority.HIGH,
            ProposalPriority.CRITICAL: EventPriority.CRITICAL,
        }[priority]
