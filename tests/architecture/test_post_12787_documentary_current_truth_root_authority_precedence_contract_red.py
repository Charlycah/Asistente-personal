from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT_TRUTH = ROOT / "ROBY_XI_2_CURRENT_TRUTH.md"
MASTER_GUIDE = ROOT / "ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md"
REGISTRY = ROOT / "ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md"
MASTER_PLAN = ROOT / "ROBY_XI_2_PLAN_MAESTRO_EVOLUCION_POST_INTEGRACION_ES.txt"

PROTECTED_SURFACES = {
    ROOT / "app/unified_brain.py": (
        "05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750"
    ),
    ROOT / "app/runtime_ui_adapter.py": (
        "2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1"
    ),
    ROOT / "app/same_episode_explicit_evidence_convergence_adapter.py": (
        "5be01adfe0c0e3a32065bcb15918013d7e20e5cb7e0092072c88df1dea5aef3d"
    ),
    ROOT / "app/ordinary_turn_multisource_reachability_adapter.py": (
        "b943f0d354fc4b7fa0dbb0d4e055e9e35289ce2a3d87a855038af4bcf73c7e97"
    ),
    ROOT / "ROBY_XI_2_FUTURE_CAPABILITIES_AND_EVOLUTION_GUIDE.md": (
        "9706ee24bec3a4d507b4ed3fe90a23684f784a407bd63537e1969530ffde1c42"
    ),
    ROOT / "architecture_rules.md": (
        "bb1520a81c32bc2e7c692ef2b1eff8badaf9ced30ff4e239aed75150c33c189b"
    ),
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_red_d1_current_truth_promotes_post_12782_owner_certified_precedence() -> None:
    text = _text(CURRENT_TRUTH)
    heading = "POST-12.782"
    assert heading in text, (
        "RED D1: Current Truth does not yet record the latest closed POST-12.782 "
        "product-surface explicit multisource reachability increment"
    )
    assert "12,787 PASS · 0 FAIL · Ruff clean" in text, (
        "RED D1: Current Truth does not yet expose the latest Owner-certified gate"
    )
    assert text.index(heading) < text.index("POST-12.698"), (
        "RED D1: latest certified truth must precede historical 12.698 provenance"
    )


def test_red_d1_current_truth_summarizes_certified_multisource_closure() -> None:
    text = _text(CURRENT_TRUTH)
    required = (
        "explicit",
        "multisource",
        "Reasoning",
        "POST-12.782",
        "12,787 PASS",
        "STOP",
    )
    for token in required:
        assert token in text, (
            f"RED D1: Current Truth missing certified closure token: {token}"
        )


def test_red_d2_master_guide_marks_12471_as_historical_reconciliation_baseline(
) -> None:
    text = _text(MASTER_GUIDE)
    assert "Current baseline pointer" in text
    assert "12,471 PASS · 0 FAIL · Ruff clean" in text
    assert "Official baseline:** 12,471" not in text, (
        "RED D2: Master Guide still presents 12,471 as an unqualified official baseline"
    )
    assert "CURRENT_TRUTH" in text or "CURRENT TRUTH" in text


def test_red_d3_registry_defers_current_baseline_to_current_truth() -> None:
    text = _text(REGISTRY)
    assert "Current baseline pointer" in text
    assert "12,471 PASS · 0 FAIL · Ruff clean" in text
    assert "Official current baseline is **12,471" not in text, (
        "RED D3: Capability Registry still claims historical 12,471 as current"
    )
    assert "CURRENT_TRUTH" in text or "CURRENT TRUTH" in text


def test_red_d4_master_plan_distinguishes_closed_from_future_convergence() -> None:
    text = _text(MASTER_PLAN)
    assert "COMPOSICIÓN INTELECTUAL MULTIMODAL GOBERNADA" in text
    assert "POST-12.782" in text, (
        "RED D4: Master Plan does not yet acknowledge the certified bounded explicit "
        "multisource/multimodal convergence"
    )
    assert "12.787" in text or "12,787" in text, (
        "RED D4: Master Plan does not yet anchor that bounded closure to the Owner gate"
    )
    lowered = text.lower()
    assert "explícit" in lowered and "futur" in lowered, (
        "RED D4: Master Plan must preserve the distinction between certified explicit "
        "convergence and future autonomous/general source discovery"
    )


def test_contract_red_preserves_productive_runtime_and_historical_future_guide(
) -> None:
    for path, expected_sha256 in PROTECTED_SURFACES.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == expected_sha256, path.relative_to(ROOT)
