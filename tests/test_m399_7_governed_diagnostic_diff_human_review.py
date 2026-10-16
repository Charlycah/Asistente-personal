from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.self_diagnostics import (
    DiagnosticHumanDecision,
    DiagnosticHypothesis,
    DiagnosticObservation,
    DiagnosticProofStatus,
    DiagnosticProposalRequest,
    DiagnosticReviewDecision,
    DiagnosticSandboxFile,
    DiagnosticSandboxRequest,
    DiagnosticSandboxStatus,
    DiagnosticThreshold,
    GovernedSelfDiagnostics,
)

NOW = datetime(2026, 8, 10, 21, 0, tzinfo=timezone.utc)


def _observation(index: int) -> DiagnosticObservation:
    return DiagnosticObservation(
        observation_id=f"obs-{index}",
        source_authority="runtime_health_readiness",
        metric="failed_residents",
        value=1.0,
        observed_at=NOW + timedelta(minutes=index),
        evidence_codes=(f"runtime_snapshot:{index}",),
    )


def _chain(tmp_path: Path):
    source = tmp_path / "app" / "runtime_health_readiness.py"
    source.parent.mkdir(parents=True)
    source.write_text("VALUE = 1\n", encoding="utf-8")
    test_file = tmp_path / "tests" / "test_runtime_health_readiness.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_value():\n    assert True\n", encoding="utf-8")

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
    proof_result = diagnostic.run_reproducible_proof(report, proof)
    assert proof_result.status is DiagnosticProofStatus.REPRODUCED
    proposal = diagnostic.prepare_isolated_proposal(
        proof,
        proof_result,
        DiagnosticProposalRequest(
            proposal_id="proposal-1",
            title="Review readiness guard",
            change_intent="Change explicit test value after human review.",
            affected_files=("app/runtime_health_readiness.py",),
            validation_tests=("tests/test_runtime_health_readiness.py",),
        ),
    )
    sandbox = diagnostic.validate_in_sandbox(
        proposal,
        DiagnosticSandboxRequest(
            sandbox_id="sandbox-1",
            candidate_files=(
                DiagnosticSandboxFile(
                    "app/runtime_health_readiness.py",
                    "VALUE = 2\n",
                ),
            ),
        ),
        project_root=tmp_path,
    )
    assert sandbox.status is DiagnosticSandboxStatus.PASSED
    return diagnostic, proposal, sandbox, source


def test_m399_7_review_requires_passed_matching_sandbox(tmp_path: Path) -> None:
    diagnostic, proposal, sandbox, _ = _chain(tmp_path)
    with pytest.raises(ValueError, match="requires passed sandbox"):
        diagnostic.prepare_human_review(
            proposal,
            replace(sandbox, status="failed"),
            project_root=tmp_path,
            review_id="review-1",
        )
    with pytest.raises(ValueError, match="must match proposal"):
        diagnostic.prepare_human_review(
            proposal,
            replace(sandbox, proposal_id="other"),
            project_root=tmp_path,
            review_id="review-1",
        )


def test_m399_7_review_contains_unified_diff_and_explanation(tmp_path: Path) -> None:
    diagnostic, proposal, sandbox, _ = _chain(tmp_path)
    review = diagnostic.prepare_human_review(
        proposal,
        sandbox,
        project_root=tmp_path,
        review_id="review-1",
    )
    assert review.proposal_id == proposal.proposal_id
    assert review.sandbox_id == sandbox.sandbox_id
    assert len(review.diff_files) == 1
    diff = review.diff_files[0].unified_diff
    assert "--- a/app/runtime_health_readiness.py" in diff
    assert "+++ b/app/runtime_health_readiness.py" in diff
    assert "-VALUE = 1" in diff
    assert "+VALUE = 2" in diff
    assert "sandbox success is evidence, not authorization" in review.explanation
    assert "approval_does_not_apply_code" in review.rationale


def test_m399_7_review_rejects_no_change(tmp_path: Path) -> None:
    diagnostic, proposal, sandbox, _ = _chain(tmp_path)
    sandbox_root = tmp_path / sandbox.sandbox_path
    (sandbox_root / "app/runtime_health_readiness.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="explicit candidate diff"):
        diagnostic.prepare_human_review(
            proposal,
            sandbox,
            project_root=tmp_path,
            review_id="review-1",
        )


def test_m399_7_review_artifact_stays_under_review_root(tmp_path: Path) -> None:
    diagnostic, proposal, sandbox, _ = _chain(tmp_path)
    review = diagnostic.prepare_human_review(
        proposal,
        sandbox,
        project_root=tmp_path,
        review_id="review-1",
    )
    destination = diagnostic.write_human_review(review, project_root=tmp_path)
    assert destination.is_file()
    assert destination.as_posix().endswith(
        ".roby/review/proposals/proposal-1/review/review-1/review.json"
    )
    with pytest.raises(FileExistsError, match="already exists"):
        diagnostic.write_human_review(review, project_root=tmp_path)


def test_m399_7_human_decision_is_explicit_and_inert(tmp_path: Path) -> None:
    diagnostic, proposal, sandbox, source = _chain(tmp_path)
    review = diagnostic.prepare_human_review(
        proposal,
        sandbox,
        project_root=tmp_path,
        review_id="review-1",
    )
    before = source.read_text(encoding="utf-8")
    decision = DiagnosticHumanDecision(
        review_id=review.review_id,
        reviewer="Carlos",
        decision=DiagnosticReviewDecision.APPROVED_FOR_MANUAL_APPLICATION,
        explanation="Reviewed diff and sandbox evidence.",
    )
    destination = diagnostic.record_human_decision(
        review,
        decision,
        project_root=tmp_path,
    )
    assert destination.is_file()
    assert source.read_text(encoding="utf-8") == before
    assert "decision.json" in destination.as_posix()


def test_m399_7_human_decision_must_match_review(tmp_path: Path) -> None:
    diagnostic, proposal, sandbox, _ = _chain(tmp_path)
    review = diagnostic.prepare_human_review(
        proposal,
        sandbox,
        project_root=tmp_path,
        review_id="review-1",
    )
    decision = DiagnosticHumanDecision(
        review_id="other",
        reviewer="Cristina",
        decision=DiagnosticReviewDecision.REJECTED,
        explanation="Needs more evidence.",
    )
    with pytest.raises(ValueError, match="must match diagnostic review"):
        diagnostic.record_human_decision(
            review,
            decision,
            project_root=tmp_path,
        )


def test_m399_7_decision_cannot_be_overwritten(tmp_path: Path) -> None:
    diagnostic, proposal, sandbox, _ = _chain(tmp_path)
    review = diagnostic.prepare_human_review(
        proposal,
        sandbox,
        project_root=tmp_path,
        review_id="review-1",
    )
    decision = DiagnosticHumanDecision(
        review_id=review.review_id,
        reviewer="Cristina",
        decision=DiagnosticReviewDecision.REJECTED,
        explanation="Reject candidate.",
    )
    diagnostic.record_human_decision(review, decision, project_root=tmp_path)
    with pytest.raises(FileExistsError, match="already exists"):
        diagnostic.record_human_decision(
            review,
            decision,
            project_root=tmp_path,
        )


def test_m399_7_has_no_application_mechanism() -> None:
    diagnostic = GovernedSelfDiagnostics()
    for name in (
        "apply",
        "apply_review",
        "apply_patch",
        "repair",
        "fix",
        "rollback",
        "auto_approve",
        "run_forever",
    ):
        assert not hasattr(diagnostic, name)


def test_m399_7_review_module_has_no_operational_application() -> None:
    source = Path("core/self_diagnostics/review.py").read_text(encoding="utf-8")
    for forbidden in (
        "subprocess",
        "os.system",
        "git apply",
        "git checkout",
        "shutil.copy",
        "write_text(candidate",
    ):
        assert forbidden not in source


def test_m399_7_keeps_single_self_diagnostics_authority() -> None:
    diagnostic = GovernedSelfDiagnostics()
    assert diagnostic.authority_id == "self_diagnostics"
    source = Path("core/self_diagnostics/review.py").read_text(encoding="utf-8")
    assert "AUTHORITY_ID" not in source
    assert "class Governed" not in source


def test_m399_7_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M399_7_GOVERNED_DIAGNOSTIC_DIFF_HUMAN_REVIEW.md"
    ).read_text(encoding="utf-8")
    assert "sandbox → tests → diff → explicación → decisión humana" in document
    assert "aprobación ≠ aplicación" in document
    assert "predicción ≠ certeza" in document
    assert "sin aplicación automática" in document
    assert "Milestone M399.7 — Governed Diagnostic Diff & Human Review" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M399.7 — Governed Diagnostic Diff & Human Review" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M399.7 — Regla de diff y revisión humana gobernada" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
