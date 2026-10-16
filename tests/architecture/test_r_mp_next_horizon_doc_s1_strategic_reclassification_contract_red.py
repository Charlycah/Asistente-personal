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


def test_red_current_truth_reclassifies_persistent_companion() -> None:
    text = CURRENT_TRUTH.read_text(encoding="utf-8")
    required = (
        "Persistent Cognitive Companion",
        "REALIZED / BOUNDED",
        "Voice Identity",
        "FUTURE",
    )
    missing = [token for token in required if token not in text]
    assert not missing, (
        "RED: Current Truth lacks the strategic Persistent Cognitive Companion "
        f"reclassification; missing={missing}"
    )
    assert "partial integration horizon" not in text


def test_red_cognitive_master_reclassifies_persistent_companion() -> None:
    text = COGNITIVE_MASTER.read_text(encoding="utf-8")
    required = (
        "Persistent Cognitive Companion",
        "REALIZED / BOUNDED",
        "existing authorities",
        "Voice Identity remains FUTURE",
    )
    missing = [token for token in required if token not in text]
    assert not missing, (
        "RED: Cognitive Master lacks the strategic Persistent Cognitive "
        f"Companion reclassification; missing={missing}"
    )
    assert "Persistent Cognitive Companion remains PARTIAL" not in text


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


def test_contract_preserves_voice_identity_as_future() -> None:
    combined = "\n".join(
        (
            CURRENT_TRUTH.read_text(encoding="utf-8"),
            COGNITIVE_MASTER.read_text(encoding="utf-8"),
            FUTURE_GUIDE.read_text(encoding="utf-8"),
        )
    )
    assert "Voice Identity" in combined
    assert "FUTURE" in combined
    assert "VOICE TIMBRE ≠ COGNITIVE IDENTITY" in combined


def test_contract_does_not_promote_multimodal_admission_authority() -> None:
    combined = "\n".join(
        (
            CURRENT_TRUTH.read_text(encoding="utf-8"),
            COGNITIVE_MASTER.read_text(encoding="utf-8"),
        )
    )
    forbidden = (
        "generic multimodal admission authority is PRODUCTIVE",
        "M401 is the generic multimodal admission authority",
    )
    assert not any(token in combined for token in forbidden)


def test_contract_preserves_human_governed_learning_boundary() -> None:
    text = COGNITIVE_MASTER.read_text(encoding="utf-8")
    required = (
        "CLOSED LOOP / HUMAN-GOVERNED / SUBSTANTIAL",
        "unrestricted autonomous learning is neither required nor authorized",
    )
    missing = [token for token in required if token not in text]
    assert not missing, f"learning boundary missing={missing}"


def test_contract_does_not_authorize_persistence_bypass() -> None:
    combined = "\n".join(
        (
            CURRENT_TRUTH.read_text(encoding="utf-8"),
            COGNITIVE_MASTER.read_text(encoding="utf-8"),
        )
    )
    forbidden = (
        "persistence bypasses Relevance",
        "persistence bypasses Planning",
        "persistence bypasses Authorization",
        "retrieval authorizes execution",
    )
    assert not any(token in combined for token in forbidden)


def test_contract_does_not_reintroduce_global_productive_fingerprint() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden_name = "PRODUCTIVE" + "_PYTHON_DIGEST"
    forbidden_helper = "_productive" + "_python_digest"
    assert forbidden_name not in source
    assert forbidden_helper not in source
