from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.self_diagnostics import GovernedSelfDiagnostics

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/M399_8_GOVERNED_SELF_DIAGNOSTICS_STABILIZATION_CLOSURE.md"
MANIFEST = ROOT / "docs/quality/M399_8_SELF_DIAGNOSTICS_CLOSURE.json"
PACKAGE = ROOT / "core/self_diagnostics"


def _doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_m399_8_declares_c00_through_c13() -> None:
    text = _doc()
    for number in range(14):
        assert f"M399-C{number:02d}" in text


def test_m399_8_closure_adds_no_new_capability() -> None:
    text = _doc()
    assert "adds no new diagnostic capability" in text
    assert "must open a new stage" in text


def test_m399_8_self_diagnostics_domain_is_single_package() -> None:
    expected = {
        "__init__.py",
        "foundation.py",
        "hypothesis.py",
        "models.py",
        "proof.py",
        "proposal.py",
        "review.py",
        "sandbox.py",
    }
    assert {path.name for path in PACKAGE.glob("*.py")} == expected


def test_m399_8_manifest_preserves_self_diagnostics_by_hash() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = data["self_diagnostics_files"]
    assert len(files) == 8
    for relative, expected in files.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected, relative


def test_m399_8_manifest_declares_single_authority_and_no_application() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authority = data["authority"]
    assert authority["self_diagnostics"].endswith("GovernedSelfDiagnostics")
    assert authority["operational_code_application"] == "outside M399"
    assert data["application_authorized"] is False


def test_m399_8_closed_chain_is_complete_and_ordered() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["closed_chain"] == [
        "observation",
        "trend",
        "anomaly",
        "hypothesis",
        "confidence",
        "evidence",
        "reproducible_proof",
        "isolated_proposal",
        "sandbox",
        "tests",
        "diff",
        "explanation",
        "human_decision",
    ]


def test_m399_8_public_api_is_frozen() -> None:
    expected = {
        "assess_hypothesis",
        "authority_id",
        "diagnose",
        "prepare_human_review",
        "prepare_isolated_proposal",
        "prepare_reproducible_proof",
        "record_human_decision",
        "run_reproducible_proof",
        "validate_in_sandbox",
        "write_human_review",
        "write_isolated_proposal",
    }
    public = {
        name
        for name, value in vars(GovernedSelfDiagnostics).items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, property))
    }
    assert public == expected


def test_m399_8_contains_no_automatic_application_api() -> None:
    diagnostic = GovernedSelfDiagnostics()
    forbidden = (
        "apply",
        "apply_patch",
        "auto_apply",
        "auto_approve",
        "repair",
        "fix",
        "rollback",
        "self_modify",
        "run_forever",
    )
    assert all(not hasattr(diagnostic, name) for name in forbidden)


def test_m399_8_review_and_proposal_do_not_apply_operational_code() -> None:
    source = "\n".join(
        (PACKAGE / name).read_text(encoding="utf-8").casefold()
        for name in ("proposal.py", "review.py")
    )
    forbidden = (
        "git apply",
        "git checkout",
        "os.system",
        "subprocess",
        "patch.diff",
    )
    assert not any(token in source for token in forbidden)


def test_m399_8_sandbox_execution_remains_bounded() -> None:
    source = (PACKAGE / "sandbox.py").read_text(encoding="utf-8")
    assert "python" not in source.casefold() or "sys.executable" in source
    assert '"-m", "pytest", "-q"' in source
    assert "value.startswith(\"-\")" in source
    assert 'path.parts[0] != "tests"' in source
    assert "shell=True" not in source


def test_m399_8_one_authority_id_exists_in_package() -> None:
    occurrences = sum(
        path.read_text(encoding="utf-8").count('AUTHORITY_ID = "self_diagnostics"')
        for path in PACKAGE.glob("*.py")
    )
    assert occurrences == 1


def test_m399_8_documentation_is_synchronized() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    assert "## Milestone M399.8" in readme
    assert "## M399.8" in changelog
    assert "M399.8 — Regla de cierre de Self-Diagnostics" in rules
    assert readme.startswith("## Milestone M393.1")
    assert changelog.startswith("# M347.15 — Estabilización de la serie")


def test_m399_8_closure_requires_full_quality_gate() -> None:
    text = _doc()
    assert "M361 regeneration" in text
    assert "`ruff check .`" in text
    assert "complete `pytest -q`" in text
    assert "is CLOSED" in text
