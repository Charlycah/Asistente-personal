from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT_TRUTH = ROOT / "ROBY_XI_2_CURRENT_TRUTH.md"
MASTER_PLAN = ROOT / "ROBY_XI_2_PLAN_MAESTRO_EVOLUCION_POST_INTEGRACION_ES.txt"

EVOLVABLE_DOCUMENTARY_AUTHORITIES = (
    ROOT / "ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md",
    ROOT / "ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md",
)

PROTECTED_DOCUMENTS = {
    ROOT / "architecture_rules.md": (
        "bb1520a81c32bc2e7c692ef2b1eff8badaf9ced30ff4e239aed75150c33c189b"
    ),
}

# Historical code hashes certify what the documentary-only 12.698 increment
# left untouched. They are evidence of that closed increment, not a permanent
# freeze on later Owner-governed productive evolution.
HISTORICAL_12698_CODE_BASELINE = {
    "core/runtime_composition_root/preparation.py": (
        "362b4dad0304d89abd584439a7542e12eef7ee9c4a718d8e10c36c0fe410e1b3"
    ),
    "app/governed_reasoning_runtime.py": (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    ),
}

def _current_truth() -> str:
    return CURRENT_TRUTH.read_text(encoding="utf-8")


def test_red_d1_current_truth_promotes_owner_certified_12698_precedence() -> None:
    text = _current_truth()
    heading = "POST-12.698 LONGITUDINAL ASSESSMENT"
    assert heading in text
    assert "12,698 PASS · 0 FAIL · Ruff clean" in text
    assert text.index(heading) < text.index("POST-12.648")


def test_red_d1_current_truth_records_exact_closed_ordinary_turn_boundary() -> None:
    text = _current_truth()
    required = (
        "longitudinal reasoning assessment",
        "conversational projection",
        "LLMRequest",
        "STOP",
    )
    for token in required:
        assert token in text


def test_red_d1_current_truth_preserves_semantic_non_claims() -> None:
    text = _current_truth()
    for token in (
        "SAME",
        "Identity",
        "Learning",
        "Initiative",
        "Planning",
        "Authorization",
        "Execution",
    ):
        assert token in text
    assert "Continuity ≠ SAME" in text


def test_red_d2_spanish_master_plan_is_integrated_at_project_root() -> None:
    assert MASTER_PLAN.is_file()


def test_red_d2_master_plan_is_compass_not_implementation_authorization() -> None:
    assert MASTER_PLAN.is_file(), (
        "RED: new Spanish Master Plan is not integrated at root"
    )
    text = MASTER_PLAN.read_text(encoding="utf-8")
    required = (
        "CREATE → GROW → TRANSCEND",
        "INVENTORY BEFORE SURGERY",
        "ONE BRAIN",
        "EVIDENCE BEFORE EXPANSION",
        "NO SYNTHETIC EVIDENCE",
        "UTILIDAD INTELECTUAL LONGITUDINAL GOBERNADA SIN IDENTIDAD FORZADA",
    )
    for token in required:
        assert token in text
    lowered = text.lower()
    assert "no autoriza implementaciones" in lowered
    assert "brújula" in lowered


def test_contract_documentary_green_preserves_documentary_authorities_and_baseline(
) -> None:
    for path in EVOLVABLE_DOCUMENTARY_AUTHORITIES:
        assert path.is_file(), path.relative_to(ROOT)

    for path, expected_sha256 in PROTECTED_DOCUMENTS.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == expected_sha256, path.relative_to(ROOT)

    assert HISTORICAL_12698_CODE_BASELINE == {
        "core/runtime_composition_root/preparation.py": (
            "362b4dad0304d89abd584439a7542e12eef7ee9c4a718d8e10c36c0fe410e1b3"
        ),
        "app/governed_reasoning_runtime.py": (
            "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
        ),
    }
