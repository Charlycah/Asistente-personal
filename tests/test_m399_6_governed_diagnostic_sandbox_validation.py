from pathlib import Path

import pytest

from core.self_diagnostics import (
    DiagnosticProposal,
    DiagnosticProposalStatus,
    DiagnosticSandboxFile,
    DiagnosticSandboxRequest,
    DiagnosticSandboxStatus,
    GovernedSelfDiagnostics,
)


def _proposal(**overrides: object) -> DiagnosticProposal:
    values: dict[str, object] = {
        "proposal_id": "proposal-1",
        "status": DiagnosticProposalStatus.DRAFT,
        "proof_id": "proof-1",
        "hypothesis_id": "hyp-1",
        "source_authority": "runtime_health_readiness",
        "metric": "failed_residents",
        "evidence_digest": "a" * 64,
        "title": "Review arithmetic defect",
        "change_intent": "Correct the isolated candidate implementation.",
        "affected_files": ("sample_module.py",),
        "validation_tests": ("tests/test_sample_module.py",),
        "risk_notes": ("Candidate may change arithmetic behavior.",),
        "review_path": ".roby/review/proposals/proposal-1/proposal.json",
        "rationale": (
            "proposal_is_isolated_from_operational_code",
            "proposal_does_not_authorize_application",
        ),
    }
    values.update(overrides)
    return DiagnosticProposal(**values)  # type: ignore[arg-type]


def _project(tmp_path: Path) -> Path:
    (tmp_path / "sample_module.py").write_text(
        "def answer():\n    return 1\n",
        encoding="utf-8",
    )
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_sample_module.py").write_text(
        "from sample_module import answer\n\n"
        "def test_answer():\n"
        "    assert answer() == 2\n",
        encoding="utf-8",
    )
    return tmp_path


def test_m399_6_request_requires_safe_identity_and_explicit_files() -> None:
    candidate = DiagnosticSandboxFile("sample_module.py", "x = 1\n")
    with pytest.raises(ValueError, match="safe sandbox_id"):
        DiagnosticSandboxRequest("../escape", (candidate,))
    with pytest.raises(ValueError, match="explicit candidate files"):
        DiagnosticSandboxRequest("sandbox-1", ())


def test_m399_6_candidate_path_must_be_safe() -> None:
    with pytest.raises(ValueError, match="safe relative path"):
        DiagnosticSandboxFile("../sample_module.py", "x = 1\n")
    with pytest.raises(ValueError, match="safe relative path"):
        DiagnosticSandboxFile("/sample_module.py", "x = 1\n")


def test_m399_6_rejects_candidate_not_declared_by_proposal(tmp_path: Path) -> None:
    request = DiagnosticSandboxRequest(
        "sandbox-1",
        (DiagnosticSandboxFile("other.py", "x = 1\n"),),
    )
    with pytest.raises(ValueError, match="declared by proposal"):
        GovernedSelfDiagnostics().validate_in_sandbox(
            _proposal(),
            request,
            project_root=_project(tmp_path),
        )


def test_m399_6_candidate_changes_only_isolated_copy_and_passes(tmp_path: Path) -> None:
    project = _project(tmp_path)
    original = (project / "sample_module.py").read_text(encoding="utf-8")
    request = DiagnosticSandboxRequest(
        "sandbox-1",
        (DiagnosticSandboxFile("sample_module.py", "def answer():\n    return 2\n"),),
    )

    result = GovernedSelfDiagnostics().validate_in_sandbox(
        _proposal(),
        request,
        project_root=project,
    )

    assert result.status is DiagnosticSandboxStatus.PASSED
    assert result.return_code == 0
    assert result.sandbox_path.endswith("/sandbox/sandbox-1")
    assert (project / "sample_module.py").read_text(encoding="utf-8") == original
    sandbox_file = project / result.sandbox_path / "sample_module.py"
    assert "return 2" in sandbox_file.read_text(encoding="utf-8")


def test_m399_6_failed_tests_are_evidence_not_application(tmp_path: Path) -> None:
    project = _project(tmp_path)
    request = DiagnosticSandboxRequest(
        "sandbox-2",
        (DiagnosticSandboxFile("sample_module.py", "def answer():\n    return 3\n"),),
    )

    result = GovernedSelfDiagnostics().validate_in_sandbox(
        _proposal(),
        request,
        project_root=project,
    )

    assert result.status is DiagnosticSandboxStatus.FAILED
    assert result.return_code != 0
    assert "sandbox_result_does_not_authorize_application" in result.rationale
    assert "return 1" in (project / "sample_module.py").read_text(encoding="utf-8")


def test_m399_6_refuses_existing_sandbox(tmp_path: Path) -> None:
    project = _project(tmp_path)
    request = DiagnosticSandboxRequest(
        "sandbox-1",
        (DiagnosticSandboxFile("sample_module.py", "def answer():\n    return 2\n"),),
    )
    diagnostic = GovernedSelfDiagnostics()
    diagnostic.validate_in_sandbox(_proposal(), request, project_root=project)
    with pytest.raises(FileExistsError, match="already exists"):
        diagnostic.validate_in_sandbox(_proposal(), request, project_root=project)


def test_m399_6_rejects_pytest_options_as_validation_tests(tmp_path: Path) -> None:
    project = _project(tmp_path)
    request = DiagnosticSandboxRequest(
        "sandbox-options",
        (DiagnosticSandboxFile("sample_module.py", "def answer():\n    return 2\n"),),
    )
    proposal = _proposal(validation_tests=("-p",))
    with pytest.raises(ValueError, match="safe test paths"):
        GovernedSelfDiagnostics().validate_in_sandbox(
            proposal,
            request,
            project_root=project,
        )


def test_m399_6_has_no_apply_approval_or_rollback_methods() -> None:
    diagnostic = GovernedSelfDiagnostics()
    for name in ("apply", "approve", "repair", "fix", "patch", "rollback"):
        assert not hasattr(diagnostic, name)


def test_m399_6_sandbox_runner_has_no_free_shell_execution() -> None:
    source = Path("core/self_diagnostics/sandbox.py").read_text(encoding="utf-8")
    for forbidden in ("shell=True", "os.system", "git apply", "git checkout"):
        assert forbidden not in source
    assert '"-m", "pytest", "-q"' in source


def test_m399_6_keeps_single_self_diagnostics_authority() -> None:
    assert GovernedSelfDiagnostics().authority_id == "self_diagnostics"
    source = Path("core/self_diagnostics/sandbox.py").read_text(encoding="utf-8")
    assert "AUTHORITY_ID" not in source
    assert "class Governed" not in source


def test_m399_6_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M399_6_GOVERNED_DIAGNOSTIC_SANDBOX_VALIDATION.md"
    ).read_text(encoding="utf-8")
    assert "propuesta aislada → sandbox → tests" in document
    assert "predicción ≠ certeza" in document
    assert "no autoriza aplicación" in document
    assert "copia aislada" in document
    assert "Milestone M399.6 — Governed Diagnostic Sandbox Validation" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M399.6 — Governed Diagnostic Sandbox Validation" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M399.6 — Regla de sandbox diagnóstico gobernado" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
