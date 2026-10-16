from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.governed_initiative_engine import GovernedInitiativeCandidate
from app.governed_proposal_executive_notification_runtime import (
    GovernedProposalExecutiveNotificationPolicy,
    GovernedProposalExecutiveNotificationRuntime,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic
from app.relevance_evaluator import RelevanceCandidate
from core.executive_runtime_integration import RuntimeExecutiveIntegration
from domain.governed_proposal import ProposalState


class Runtime:
    pass


def _candidate(now: datetime) -> GovernedInitiativeCandidate:
    return GovernedInitiativeCandidate(
        source_id="nasa",
        summary="NASA publicó una novedad espacial relevante para Carlos y Cristina.",
        category="space",
        relevance_candidate=RelevanceCandidate(
            title="Nueva observación espacial",
            topics=frozenset({InterestTopic.SPACE_EXPLORATION}),
            importance=15,
            source_confidence=99,
            verification="confirmed",
            information_kind="discovery",
        ),
        expires_at=now + timedelta(days=1),
        metadata={"origin": "governed_source"},
    )


def _executive_runtime(tmp_path: Path) -> RuntimeExecutiveIntegration:
    return RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl",
    )


def test_governed_proposal_reaches_existing_executive_notification_spine(tmp_path):
    now = datetime.now(timezone.utc)
    gateway = OfficialConversationGateway(Runtime())
    generated = gateway.generate_governed_initiative(_candidate(now), observed_at=now)
    assert generated.proposal is not None
    assert generated.proposal.state is ProposalState.PENDING

    executive = _executive_runtime(tmp_path)
    executive.start()
    bridge = GovernedProposalExecutiveNotificationRuntime(
        gateway=gateway,
        executive_runtime=executive,
        policy=GovernedProposalExecutiveNotificationPolicy(
            poll_interval=timedelta(hours=1)
        ),
    )
    bridge.start()
    try:
        submitted_id = bridge.tick(now=now + timedelta(seconds=1))
        if submitted_id is None:
            # The resident thread may have won the race and submitted it already.
            assert bridge.snapshot.submitted == 1
        else:
            assert submitted_id == generated.proposal.proposal_id

        notifications = executive.drain_notifications()
        assert len(notifications) == 1
        assert "Nueva observación espacial" in notifications[0]
        assert "NASA publicó" in notifications[0]

        stored = gateway.find_governed_proposal(generated.proposal.proposal_id)
        assert stored is not None
        assert stored.state is ProposalState.OFFERED
        assert bridge.snapshot.offered == 1
        assert bridge.snapshot.inflight == 0
    finally:
        bridge.stop()
        executive.stop()


def test_bridge_preserves_existing_authorities_and_uses_correlation_identity(tmp_path):
    now = datetime.now(timezone.utc)
    gateway = OfficialConversationGateway(Runtime())
    generated = gateway.generate_governed_initiative(_candidate(now), observed_at=now)
    assert generated.proposal is not None

    executive = _executive_runtime(tmp_path)
    executive.start()
    bridge = GovernedProposalExecutiveNotificationRuntime(
        gateway=gateway,
        executive_runtime=executive,
        policy=GovernedProposalExecutiveNotificationPolicy(
            poll_interval=timedelta(hours=1)
        ),
    )
    bridge.start()
    try:
        bridge.tick(now=now + timedelta(seconds=1))
        pending = executive.coordinator.snapshot.pending_count
        assert pending == 1
        executive.coordinator.dispatch_pending()
        brokered = executive.broker.pending_events()
        assert len(brokered) == 1
        assert brokered[0].event.correlation_id == (
            f"governed-proposal:{generated.proposal.proposal_id}"
        )
        assert gateway.find_governed_proposal(
            generated.proposal.proposal_id
        ).state is ProposalState.PENDING

        executive.broker.dispatch_pending()
        assert gateway.find_governed_proposal(
            generated.proposal.proposal_id
        ).state is ProposalState.OFFERED
    finally:
        bridge.stop()
        executive.stop()


def test_desktop_wires_bridge_without_second_notification_authority():
    source = Path("app/desktop_bootstrap.py").read_text(encoding="utf-8")
    bridge_source = Path(
        "app/governed_proposal_executive_notification_runtime.py"
    ).read_text(encoding="utf-8")

    assert "GovernedProposalExecutiveNotificationRuntime" in source
    assert "gateway=runtime" in source
    assert "executive_runtime=executive_runtime" in source
    assert "governed_proposal_notification_runtime" in source
    assert "executive_runtime.publish(" in bridge_source
    assert "gateway.next_presentable_governed_proposal" in bridge_source
    assert "gateway.offer_governed_proposal" in bridge_source
    assert "ExecutiveNotificationBroker(" not in bridge_source
    assert "GovernedProposalInbox(" not in bridge_source
