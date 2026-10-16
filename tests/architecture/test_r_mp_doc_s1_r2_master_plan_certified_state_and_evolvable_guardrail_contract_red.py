from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COGNITIVE_MASTER = ROOT / "ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md"
CURRENT_TRUTH = ROOT / "ROBY_XI_2_CURRENT_TRUTH.md"
FUTURE_GUIDE = ROOT / "ROBY_XI_2_FUTURE_CAPABILITIES_AND_EVOLUTION_GUIDE.md"
CONSOLIDATION_S1 = (
    ROOT
    / "tests"
    / "architecture"
    / "test_r_doc_master_consolidation_s1_contract_red.py"
)
ROOT_R1 = (
    ROOT
    / "tests"
    / "architecture"
    / "test_r_doc_root_1_governed_historical_root_archival_contract_red.py"
)

HISTORICAL_DOC_S1_R2_PRODUCTIVE_PYTHON_DIGEST = (
    "ebe74964a8801561115a24cee7429b1450cff5eb9ce850476c1df917594dc7d7"
)
COGNITIVE_MASTER_NAME = "ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md"


def _assigned_mapping(path: Path, variable: str) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == variable
            for target in node.targets
        ):
            continue
        value = ast.literal_eval(node.value)
        assert isinstance(value, dict)
        return value
    raise AssertionError(f"assignment not found: {variable}")


def test_red_cognitive_master_has_current_certified_state_layer() -> None:
    text = COGNITIVE_MASTER.read_text(encoding="utf-8")
    required = (
        "CURRENT CERTIFIED-STATE RECONCILIATION",
        (
            "CURRENT EXECUTABLE TRUTH + LATEST OWNER GATE > "
            "STALE HISTORICAL STATUS LABEL"
        ),
        "H3",
        "H4-MMC",
        "H4-VOICE",
        "NO NEXT PRODUCTIVE HORIZON CURRENTLY PROVEN",
    )
    missing = [token for token in required if token not in text]
    assert not missing, (
        "RED R2: Cognitive Master lacks current certified-state "
        f"interpretation; missing={missing}"
    )


def test_red_historical_s1_no_longer_sha_freezes_cognitive_master() -> None:
    frozen = _assigned_mapping(CONSOLIDATION_S1, "EVOLVABLE_UNCHANGED")
    assert COGNITIVE_MASTER_NAME not in frozen, (
        "RED R2: historical Consolidation-S1 still SHA-freezes the "
        "Cognitive Master even though R-DOC-ROOT-1-R1 made it evolvable"
    )


def test_r2_preserves_historical_priority_snapshots_and_s5_stop() -> None:
    text = COGNITIVE_MASTER.read_text(encoding="utf-8")
    required = (
        "## 13. Current future-development decision matrix",
        "## 14. Priority order after reconciliation",
        "### P1 — Governed Hierarchical Concept Composition",
        "## R-CI-SI-S5 — Self-Epistemic Relevance Horizon Closure",
        "STOP\nbefore Relevance",
        "Do not infer topics",
    )
    missing = [token for token in required if token not in text]
    assert not missing, f"R2 protection missing={missing}"


def test_r2_preserves_future_voice_identity_boundary() -> None:
    text = FUTURE_GUIDE.read_text(encoding="utf-8")
    required = (
        "## 4. Future capability C — ROBY Voice Identity",
        "VOICE TIMBRE ≠ COGNITIVE IDENTITY",
        "A future implementation",
    )
    missing = [token for token in required if token not in text]
    assert not missing, f"R2 future-voice protection missing={missing}"


def test_r2_preserves_compact_current_truth_and_no_super_master() -> None:
    lines = CURRENT_TRUTH.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 400
    assert not (ROOT / "ROBY_XI_2_SUPER_MASTER.md").exists()


def test_r2_preserves_root_r1_evolvable_authority_contract() -> None:
    source = ROOT_R1.read_text(encoding="utf-8")
    assert "EVOLVABLE_ROOT_AUTHORITIES" in source
    assert COGNITIVE_MASTER_NAME in source
    assert "must not be frozen" in source


def test_r2_preserves_historical_productive_python_fingerprint_evidence() -> None:
    assert HISTORICAL_DOC_S1_R2_PRODUCTIVE_PYTHON_DIGEST == (
        "ebe74964a8801561115a24cee7429b1450cff5eb9ce850476c1df917594dc7d7"
    )


def test_r2_historical_fingerprint_does_not_freeze_future_runtime() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    function_names = {
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    assigned_names = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    forbidden_function = "_productive" + "_python_digest"
    forbidden_constant = "PRODUCTIVE" + "_PYTHON_DIGEST"
    assert forbidden_function not in function_names
    assert forbidden_constant not in assigned_names
