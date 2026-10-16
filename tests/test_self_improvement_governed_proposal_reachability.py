from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.governed_proposal_executive_notification_runtime import (
    GovernedProposalExecutiveNotificationPolicy,
    GovernedProposalExecutiveNotificationRuntime,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.self_improvement_governed_proposal_reachability import (
    SelfImprovementGovernedProposalReachability,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration
from core.self_diagnostics import DiagnosticProposal, DiagnosticProposalStatus
from domain.governed_proposal import ProposalPriority, ProposalState


class Runtime:
    pass


def _diagnostic_proposal() -> DiagnosticProposal:
    return DiagnosticProposal(
        proposal_id="diag-001",
        status=DiagnosticProposalStatus.DRAFT,
        proof_id="proof-001",
        hypothesis_id="hyp-001",
        source_authority="governed_reasoning",
        metric="reasoning_quality",
        evidence_digest="a" * 64,
        title="Review reproduced reasoning_quality diagnostic behavior",
        change_intent="Minimally adjust app/example.py under existing authority.",
        affected_files=("app/example.py",),
        validation_tests=("tests/test_example.py",),
        risk_notes=("human review required",),
        review_path=".roby/review/proposals/diag-001/proposal.json",
        rationale=("proposal_does_not_authorize_application",),
    )


def _reachability(gateway: OfficialConversationGateway):
    return SelfImprovementGovernedProposalReachability(gateway=gateway)


def test_self_improvement_reuses_canonical_governed_proposal_inbox():
    now = datetime.now(timezone.utc)
    gateway = OfficialConversationGateway(Runtime())
    proposal = _reachability(gateway).enqueue(
        _diagnostic_proposal(),
        observed_at=now,
    )

    assert proposal.state is ProposalState.PENDING
    assert proposal.source_id == "self_diagnostics"
    assert proposal.category == "self_improvement_review"
    assert proposal.priority is ProposalPriority.HIGH
    assert proposal.metadata["recipient"] == "both"
    assert proposal.metadata["human_review_required"] == "true"
    assert proposal.metadata["autonomous_execution"] == "false"
    assert gateway.governed_proposal_inbox.pending_proposals == 1


def test_self_improvement_reaches_existing_executive_notification_spine(tmp_path):
    now = datetime.now(timezone.utc)
    gateway = OfficialConversationGateway(Runtime())
    proposal = _reachability(gateway).enqueue(
        _diagnostic_proposal(),
        observed_at=now,
    )
    executive = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl"
    )
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
        submitted = bridge.tick(now=now + timedelta(seconds=1))
        if submitted is None:
            assert bridge.snapshot.submitted == 1
        else:
            assert submitted == proposal.proposal_id
        notifications = executive.drain_notifications()
        assert len(notifications) == 1
        assert "posible mejora" in notifications[0]
        assert "requiere revisión humana" in notifications[0]
        stored = gateway.find_governed_proposal(proposal.proposal_id)
        assert stored is not None
        assert stored.state is ProposalState.OFFERED
    finally:
        bridge.stop()
        executive.stop()


def test_self_improvement_adds_no_execution_or_code_mutation_authority():
    gateway = OfficialConversationGateway(Runtime())
    snapshot = _reachability(gateway).snapshot
    assert snapshot.diagnostic_authority == (
        "core.self_diagnostics:GovernedSelfDiagnostics"
    )
    assert snapshot.proposal_authority == (
        "domain.governed_proposal:GovernedProposalModel"
    )
    assert snapshot.inbox_authority == (
        "domain.governed_proposal_inbox:GovernedProposalInbox"
    )
    assert snapshot.autonomous_execution_enabled is False
    assert snapshot.code_mutation_enabled is False

    source = Path(
        "app/self_improvement_governed_proposal_reachability.py"
    ).read_text(encoding="utf-8")
    assert "GovernedProposalModel()" not in source
    assert "GovernedProposalInbox()" not in source
    assert "write_text(" not in source
    assert "subprocess" not in source
