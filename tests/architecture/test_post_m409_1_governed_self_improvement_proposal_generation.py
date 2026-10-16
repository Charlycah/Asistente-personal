from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.self_improvement_proposal_generation import (
    DiagnosticProjectEvidence,
    DiagnosticProjectFileEvidence,
    generate_diagnostic_proposal_request,
)
from core.self_diagnostics import (
    DiagnosticHypothesis,
    DiagnosticObservation,
    DiagnosticProofStatus,
    DiagnosticThreshold,
    GovernedSelfDiagnostics,
)

NOW = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)


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
        "hyp-2b",
        "candidate runtime readiness regression",
        ("obs-1", "obs-2"),
    )
    assessment = diagnostic.assess_hypothesis(report, hypothesis)
    proof = diagnostic.prepare_reproducible_proof(
        report,
        assessment,
        proof_id="proof-2b",
    )
    result = diagnostic.run_reproducible_proof(report, proof)
    assert result.status is DiagnosticProofStatus.REPRODUCED
    return diagnostic, proof, result


def _write(root: Path, relative: str, content: str) -> DiagnosticProjectFileEvidence:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return DiagnosticProjectFileEvidence(
        relative_path=relative,
        content_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        rationale=f"Explicit diagnostic evidence for {relative}",
    )


def _evidence(root: Path) -> DiagnosticProjectEvidence:
    return DiagnosticProjectEvidence(
        affected_files=(
            _write(root, "app/runtime_health_readiness.py", "READY = True\n"),
        ),
        validation_tests=(
            _write(
                root,
                "tests/test_runtime_health_readiness.py",
                "def test_ready(): pass\n",
            ),
        ),
    )


def test_2b_generates_m399_5_request_from_reproduced_proof(tmp_path: Path) -> None:
    _, proof, result = _proof_chain()
    request = generate_diagnostic_proposal_request(
        proof,
        result,
        _evidence(tmp_path),
        project_root=tmp_path,
        proposal_id="proposal-2b",
    )
    assert request.proposal_id == "proposal-2b"
    assert request.affected_files == ("app/runtime_health_readiness.py",)
    assert request.validation_tests == ("tests/test_runtime_health_readiness.py",)
    assert "failed_residents" in request.title
    assert "runtime_health_readiness" in request.change_intent
    assert "without expanding authority" in request.change_intent


def test_2b_rejects_non_reproduced_proof(tmp_path: Path) -> None:
    _, proof, result = _proof_chain()
    changed = replace(result, status="not_reproduced")
    with pytest.raises(ValueError, match="requires reproduced proof"):
        generate_diagnostic_proposal_request(
            proof,
            changed,
            _evidence(tmp_path),
            project_root=tmp_path,
            proposal_id="proposal-2b",
        )


def test_2b_fails_closed_on_unverified_project_evidence(tmp_path: Path) -> None:
    _, proof, result = _proof_chain()
    evidence = _evidence(tmp_path)
    target = tmp_path / evidence.affected_files[0].relative_path
    target.write_text("CHANGED\n", encoding="utf-8")
    with pytest.raises(ValueError, match="content digest mismatch"):
        generate_diagnostic_proposal_request(
            proof,
            result,
            evidence,
            project_root=tmp_path,
            proposal_id="proposal-2b",
        )


def test_2b_requires_existing_test_evidence(tmp_path: Path) -> None:
    source = _write(tmp_path, "app/runtime_health_readiness.py", "READY = True\n")
    with pytest.raises(ValueError, match="existing tests"):
        DiagnosticProjectEvidence(
            affected_files=(source,),
            validation_tests=(
                _write(tmp_path, "docs/check.md", "check\n"),
            ),
        )


def test_2b_blocks_self_diagnostics_and_governance_scope(tmp_path: Path) -> None:
    _, proof, result = _proof_chain()
    protected = _write(tmp_path, "core/self_diagnostics/foundation.py", "LOCKED\n")
    test = _write(
        tmp_path,
        "tests/test_runtime_health_readiness.py",
        "def test_ready(): pass\n",
    )
    with pytest.raises(ValueError, match="protected governance scope"):
        generate_diagnostic_proposal_request(
            proof,
            result,
            DiagnosticProjectEvidence((protected,), (test,)),
            project_root=tmp_path,
            proposal_id="proposal-2b",
        )


def test_2b_rejects_over_broad_affected_file_scope(tmp_path: Path) -> None:
    affected = tuple(
        _write(tmp_path, f"app/component_{index}.py", f"VALUE = {index}\n")
        for index in range(5)
    )
    test = _write(
        tmp_path,
        "tests/test_runtime_health_readiness.py",
        "def test_ready(): pass\n",
    )
    with pytest.raises(ValueError, match="affected-file scope is too broad"):
        DiagnosticProjectEvidence(affected, (test,))


def test_2b_rejects_over_broad_validation_test_scope(tmp_path: Path) -> None:
    source = _write(tmp_path, "app/runtime_health_readiness.py", "READY = True\n")
    tests = tuple(
        _write(
            tmp_path,
            f"tests/test_runtime_health_readiness_{index}.py",
            "def test_ready(): pass\n",
        )
        for index in range(9)
    )
    with pytest.raises(ValueError, match="validation-test scope is too broad"):
        DiagnosticProjectEvidence((source,), tests)


@pytest.mark.parametrize(
    "protected_path",
    (
        "app/cognitive_authority_map.py",
        "app/m369_explicit_human_learning_approval.py",
        "core/permission_consent.py",
        "core/unified_permission_consent/engine.py",
        "docs/quality/M399_8_SELF_DIAGNOSTICS_CLOSURE.json",
        "docs/M398_1_PHYSICAL_TRANSPORT_CONSTITUTION.md",
        "app/self_improvement_proposal_generation.py",
        "architecture_rules.md",
    ),
)
def test_2b_blocks_expanded_protected_governance_surfaces(
    tmp_path: Path, protected_path: str
) -> None:
    _, proof, result = _proof_chain()
    protected = _write(tmp_path, protected_path, "LOCKED\n")
    test = _write(
        tmp_path,
        "tests/test_runtime_health_readiness.py",
        "def test_ready(): pass\n",
    )
    with pytest.raises(ValueError, match="protected governance scope"):
        generate_diagnostic_proposal_request(
            proof,
            result,
            DiagnosticProjectEvidence((protected,), (test,)),
            project_root=tmp_path,
            proposal_id="proposal-2b",
        )


def test_2b_generated_request_reuses_existing_m399_5_pipeline(tmp_path: Path) -> None:
    diagnostic, proof, result = _proof_chain()
    operational = tmp_path / "app/runtime_health_readiness.py"
    evidence = _evidence(tmp_path)
    before = operational.read_text(encoding="utf-8")
    request = generate_diagnostic_proposal_request(
        proof,
        result,
        evidence,
        project_root=tmp_path,
        proposal_id="proposal-2b",
    )
    proposal = diagnostic.prepare_isolated_proposal(proof, result, request)
    assert proposal.change_intent == request.change_intent
    assert proposal.affected_files == request.affected_files
    assert proposal.validation_tests == request.validation_tests
    assert operational.read_text(encoding="utf-8") == before
    assert "proposal_does_not_authorize_application" in proposal.rationale


def test_2b_is_deterministic_for_same_proof_and_evidence(tmp_path: Path) -> None:
    _, proof, result = _proof_chain()
    evidence = _evidence(tmp_path)
    first = generate_diagnostic_proposal_request(
        proof,
        result,
        evidence,
        project_root=tmp_path,
        proposal_id="proposal-2b",
    )
    second = generate_diagnostic_proposal_request(
        proof,
        result,
        evidence,
        project_root=tmp_path,
        proposal_id="proposal-2b",
    )
    assert first == second


def test_2b_adds_no_authority_or_operational_mutation_api() -> None:
    source = Path("app/self_improvement_proposal_generation.py").read_text(
        encoding="utf-8"
    )
    assert "AUTHORITY_ID" not in source
    assert "class Governed" not in source
    for forbidden in (
        "subprocess",
        "os.system",
        "git apply",
        "git checkout",
        "write_text(",
        "write_bytes(",
    ):
        assert forbidden not in source
