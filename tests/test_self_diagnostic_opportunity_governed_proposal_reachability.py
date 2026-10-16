from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from app.official_conversation_gateway import OfficialConversationGateway
from app.self_diagnostic_opportunity_governed_proposal_reachability import (
    SelfDiagnosticOpportunity,
    SelfDiagnosticOpportunityGovernedProposalReachability,
)
from app.self_improvement_governed_proposal_reachability import (
    SelfImprovementGovernedProposalReachability,
)
from app.self_improvement_proposal_generation import (
    DiagnosticProjectEvidence,
    DiagnosticProjectFileEvidence,
)
from core.self_diagnostics import (
    DiagnosticHypothesis,
    DiagnosticObservation,
    DiagnosticThreshold,
    GovernedSelfDiagnostics,
)
from domain.governed_proposal import ProposalState


class Runtime:
    pass


def _file_evidence(path, root, rationale):
    relative = path.relative_to(root).as_posix()
    return DiagnosticProjectFileEvidence(
        relative_path=relative,
        content_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        rationale=rationale,
    )


def _opportunity(tmp_path):
    app_dir = tmp_path / "app"
    tests_dir = tmp_path / "tests"
    app_dir.mkdir()
    tests_dir.mkdir()
    target = app_dir / "example.py"
    validation = tests_dir / "test_example.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    validation.write_text("def test_value(): assert True\n", encoding="utf-8")

    now = datetime.now(timezone.utc)
    observations = tuple(
        DiagnosticObservation(
            observation_id=f"obs-{index}",
            source_authority="runtime_readiness",
            metric="failed_residents",
            value=1.0,
            observed_at=now + timedelta(seconds=index),
            evidence_codes=(f"resident-failure-{index}",),
        )
        for index in range(1, 4)
    )
    return SelfDiagnosticOpportunity(
        observations=observations,
        threshold=DiagnosticThreshold(
            metric="failed_residents",
            limit=0.0,
            direction="above",
            minimum_consecutive_samples=2,
        ),
        hypothesis=DiagnosticHypothesis(
            "hyp-1",
            "candidate runtime readiness regression",
            ("obs-1", "obs-2"),
        ),
        project_evidence=DiagnosticProjectEvidence(
            affected_files=(
                _file_evidence(target, tmp_path, "explicit candidate target"),
            ),
            validation_tests=(
                _file_evidence(validation, tmp_path, "existing validation"),
            ),
        ),
        project_root=tmp_path,
        proof_id="proof-1",
        proposal_id="proposal-1",
    )


def _reachability():
    gateway = OfficialConversationGateway(Runtime())
    proposal_reachability = SelfImprovementGovernedProposalReachability(
        gateway=gateway
    )
    return (
        gateway,
        SelfDiagnosticOpportunityGovernedProposalReachability(
            diagnostics=GovernedSelfDiagnostics(),
            proposal_reachability=proposal_reachability,
        ),
    )


def test_explicit_opportunity_reaches_existing_governed_proposal(tmp_path):
    gateway, reachability = _reachability()
    result = reachability.submit(
        _opportunity(tmp_path),
        observed_at=datetime.now(timezone.utc),
    )

    assert result.diagnostic_proposal.proposal_id == "proposal-1"
    assert result.governed_proposal.proposal_id == "self-improvement-proposal-1"
    assert result.governed_proposal.state is ProposalState.PENDING
    assert gateway.governed_proposal_inbox.pending_proposals == 1


def test_opportunity_reuses_self_diagnostics_and_adds_no_autonomy():
    _, reachability = _reachability()
    snapshot = reachability.snapshot

    assert snapshot.diagnostic_authority == "self_diagnostics"
    assert snapshot.autonomous_hypothesis_generation_enabled is False
    assert snapshot.background_monitoring_enabled is False
    assert snapshot.autonomous_execution_enabled is False
    assert snapshot.code_mutation_enabled is False


def test_opportunity_adapter_does_not_own_diagnostic_or_proposal_authorities():
    source = (
        "app/self_diagnostic_opportunity_governed_proposal_reachability.py"
    )
    text = __import__("pathlib").Path(source).read_text(encoding="utf-8")

    assert "GovernedSelfDiagnostics()" not in text
    assert "GovernedProposalModel()" not in text
    assert "GovernedProposalInbox()" not in text
    assert "subprocess" not in text
    assert "write_text(" not in text
