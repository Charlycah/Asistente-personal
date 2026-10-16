from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.self_diagnostics import (
    DiagnosticHypothesis,
    DiagnosticObservation,
    DiagnosticProofStatus,
    DiagnosticProposalRequest,
    DiagnosticProposalStatus,
    DiagnosticThreshold,
    GovernedSelfDiagnostics,
)

NOW = datetime(2026, 8, 10, 18, 0, tzinfo=timezone.utc)


def _observation(index: int) -> DiagnosticObservation:
    return DiagnosticObservation(
        observation_id=f"obs-{index}",
        source_authority="runtime_health_readiness",
        metric="failed_residents",
        value=1.0,
        observed_at=NOW + timedelta(minutes=index),
        evidence_codes=(f"runtime_snapshot:{index}",),
    )


def _proof_chain():
    diagnostic = GovernedSelfDiagnostics()
    report = diagnostic.diagnose(
        (_observation(1), _observation(2), _observation(3)),
        threshold=DiagnosticThreshold(
            metric="failed_residents",
            limit=0.0,
            direction="above",
            minimum_consecutive_samples=2,
        ),
    )
    hypothesis = DiagnosticHypothesis(
        "hyp-1",
        "candidate runtime readiness regression",
        ("obs-1", "obs-2"),
    )
    assessment = diagnostic.assess_hypothesis(report, hypothesis)
    proof = diagnostic.prepare_reproducible_proof(
        report,
        assessment,
        proof_id="proof-1",
    )
    result = diagnostic.run_reproducible_proof(report, proof)
    assert result.status is DiagnosticProofStatus.REPRODUCED
    return diagnostic, proof, result


def _request(**overrides: object) -> DiagnosticProposalRequest:
    values: dict[str, object] = {
        "proposal_id": "proposal-1",
        "title": "Review runtime readiness guard",
        "change_intent": "Adjust the explicit readiness guard after human review.",
        "affected_files": ("app/runtime_health_readiness.py",),
        "validation_tests": ("tests/test_runtime_health_readiness.py",),
        "risk_notes": ("May alter readiness classification.",),
    }
    values.update(overrides)
    return DiagnosticProposalRequest(**values)  # type: ignore[arg-type]


def test_m399_5_request_requires_safe_explicit_identity() -> None:
    with pytest.raises(ValueError, match="safe proposal_id"):
        _request(proposal_id="../escape")
    with pytest.raises(ValueError, match="safe proposal_id"):
        _request(proposal_id=" ")


def test_m399_5_request_requires_explicit_change_intent() -> None:
    with pytest.raises(ValueError, match="explicit change intent"):
        _request(change_intent=" ")


def test_m399_5_request_requires_files_and_validation_tests() -> None:
    with pytest.raises(ValueError, match="affected files"):
        _request(affected_files=())
    with pytest.raises(ValueError, match="validation tests"):
        _request(validation_tests=())


def test_m399_5_proposal_requires_reproduced_proof() -> None:
    diagnostic, proof, result = _proof_chain()
    changed = replace(result, status="not_reproduced")
    with pytest.raises(ValueError, match="requires reproduced proof"):
        diagnostic.prepare_isolated_proposal(proof, changed, _request())


def test_m399_5_proposal_requires_matching_proof_result() -> None:
    diagnostic, proof, result = _proof_chain()
    changed = replace(result, proof_id="proof-other")
    with pytest.raises(ValueError, match="must match proof"):
        diagnostic.prepare_isolated_proposal(proof, changed, _request())


def test_m399_5_proposal_is_draft_and_isolated() -> None:
    diagnostic, proof, result = _proof_chain()
    proposal = diagnostic.prepare_isolated_proposal(proof, result, _request())
    assert proposal.status is DiagnosticProposalStatus.DRAFT
    assert proposal.review_path == ".roby/review/proposals/proposal-1/proposal.json"
    assert proposal.proof_id == "proof-1"
    assert proposal.hypothesis_id == "hyp-1"
    assert proposal.evidence_digest == proof.evidence_digest


def test_m399_5_proposal_does_not_infer_remediation() -> None:
    diagnostic, proof, result = _proof_chain()
    proposal = diagnostic.prepare_isolated_proposal(proof, result, _request())
    assert "remediation_intent_was_explicit_not_inferred" in proposal.rationale
    assert "proposal_does_not_authorize_application" in proposal.rationale
    assert "human_decision_required_before_any_change" in proposal.rationale
    assert "prediction_is_not_certainty" in proposal.rationale


def test_m399_5_writer_only_creates_review_artifact(tmp_path: Path) -> None:
    diagnostic, proof, result = _proof_chain()
    proposal = diagnostic.prepare_isolated_proposal(proof, result, _request())
    operational = tmp_path / "app" / "runtime_health_readiness.py"
    operational.parent.mkdir(parents=True)
    operational.write_text("ORIGINAL\n", encoding="utf-8")

    destination = diagnostic.write_isolated_proposal(
        proposal,
        project_root=tmp_path,
    )

    assert destination == tmp_path / proposal.review_path
    assert destination.is_file()
    assert operational.read_text(encoding="utf-8") == "ORIGINAL\n"
    assert not (tmp_path / ".roby/review/proposals/proposal-1/patch.diff").exists()


def test_m399_5_writer_refuses_overwrite(tmp_path: Path) -> None:
    diagnostic, proof, result = _proof_chain()
    proposal = diagnostic.prepare_isolated_proposal(proof, result, _request())
    diagnostic.write_isolated_proposal(proposal, project_root=tmp_path)
    with pytest.raises(FileExistsError, match="already exists"):
        diagnostic.write_isolated_proposal(proposal, project_root=tmp_path)


def test_m399_5_proposal_has_no_approval_or_application_methods() -> None:
    diagnostic = GovernedSelfDiagnostics()
    for name in (
        "approve",
        "reject",
        "apply",
        "repair",
        "fix",
        "patch",
        "sandbox",
        "rollback",
        "run_forever",
    ):
        assert not hasattr(diagnostic, name)


def test_m399_5_proposal_module_contains_no_operational_mutation() -> None:
    source = Path("core/self_diagnostics/proposal.py").read_text(encoding="utf-8")
    for forbidden in (
        "subprocess",
        "os.system",
        "shutil.copy",
        "patch.diff",
        "git apply",
        "git checkout",
    ):
        assert forbidden not in source


def test_m399_5_keeps_single_self_diagnostics_authority() -> None:
    diagnostic = GovernedSelfDiagnostics()
    assert diagnostic.authority_id == "self_diagnostics"
    source = Path("core/self_diagnostics/proposal.py").read_text(encoding="utf-8")
    assert "AUTHORITY_ID" not in source
    assert "class Governed" not in source


def test_m399_5_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M399_5_GOVERNED_ISOLATED_DIAGNOSTIC_PROPOSAL.md"
    ).read_text(encoding="utf-8")
    assert "prueba reproducible → propuesta aislada" in document
    assert ".roby/review/proposals/" in document
    assert "predicción ≠ certeza" in document
    assert "no autoriza" in document
    assert "sin sandbox" in document
    assert "Milestone M399.5 — Governed Isolated Diagnostic Proposal" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M399.5 — Governed Isolated Diagnostic Proposal" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M399.5 — Regla de propuesta diagnóstica aislada" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
