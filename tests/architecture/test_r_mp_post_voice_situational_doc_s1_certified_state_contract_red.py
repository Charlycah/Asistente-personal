from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT_TRUTH = ROOT / "ROBY_XI_2_CURRENT_TRUTH.md"
COGNITIVE_MASTER = (
    ROOT / "ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md"
)
CAPABILITY_REGISTRY = ROOT / "ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md"
NORTH_STAR = ROOT / "ROBY_XI_2_CONVERSATIONAL_IDENTITY_SELF_INQUIRY_NORTH_STAR.md"
FUTURE_GUIDE = ROOT / "ROBY_XI_2_FUTURE_CAPABILITIES_AND_EVOLUTION_GUIDE.md"


def test_red_current_truth_records_voice_situational_certified_state() -> None:
    text = CURRENT_TRUTH.read_text(encoding="utf-8")
    required = (
        "Voice-Situational S1",
        "13,152 PASS",
        "0 FAIL",
        "STOP BEFORE S2",
        "Voice Identity",
        "FUTURE",
    )
    missing = [token for token in required if token not in text]
    assert not missing, (
        "RED: Current Truth lacks the post-Voice-Situational certified state; "
        f"missing={missing}"
    )


def test_red_cognitive_master_records_voice_situational_certified_state() -> None:
    text = COGNITIVE_MASTER.read_text(encoding="utf-8")
    required = (
        "Voice-Situational S1",
        "OWNER-CERTIFIED",
        "13,152 PASS",
        "NO CURRENT PRODUCTIVE RESIDUAL PROVEN",
        "STOP BEFORE S2",
        "rate / pitch / volume",
    )
    missing = [token for token in required if token not in text]
    assert not missing, (
        "RED: Cognitive Master lacks the post-Voice-Situational certified "
        f"state; missing={missing}"
    )


def test_contract_preserves_compact_current_truth_and_no_super_master() -> None:
    lines = CURRENT_TRUTH.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 400
    assert not (ROOT / "ROBY_XI_2_SUPER_MASTER.md").exists()


def test_contract_preserves_existing_master_authority_residency() -> None:
    for path in (
        CURRENT_TRUTH,
        COGNITIVE_MASTER,
        CAPABILITY_REGISTRY,
        NORTH_STAR,
        FUTURE_GUIDE,
    ):
        assert path.is_file(), path.relative_to(ROOT)


def test_contract_preserves_north_star_expression_truth_boundary() -> None:
    text = NORTH_STAR.read_text(encoding="utf-8")
    assert "EXPRESSIVITY ≠ RANDOM EMOTION." in text
    assert "expressing cognitive state without falsifying emotion" in text


def test_contract_preserves_future_voice_identity_boundary() -> None:
    text = FUTURE_GUIDE.read_text(encoding="utf-8")
    required = (
        "ROBY Voice Identity",
        "VOICE TIMBRE ≠ COGNITIVE IDENTITY",
    )
    missing = [token for token in required if token not in text]
    assert not missing, f"future voice boundary missing={missing}"


def test_contract_does_not_promote_acoustic_controls_to_canonical_decision() -> None:
    combined = "\n".join(
        (
            CURRENT_TRUTH.read_text(encoding="utf-8"),
            COGNITIVE_MASTER.read_text(encoding="utf-8"),
        )
    )
    forbidden = (
        "rate is canonically decided",
        "pitch is canonically decided",
        "volume is canonically decided",
    )
    assert not any(token in combined for token in forbidden)


def test_contract_does_not_reintroduce_global_productive_fingerprint() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden_name = "PRODUCTIVE" + "_PYTHON_DIGEST"
    forbidden_helper = "_productive" + "_python_digest"
    assert forbidden_name not in source
    assert forbidden_helper not in source
