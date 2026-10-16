from __future__ import annotations

import hashlib
from pathlib import Path

from app.governed_g7_approved_learning_memory_materialization import (
    GovernedG7ApprovedLearningMemoryMaterializationV1,
)
from app.official_runtime_composition import OfficialRuntimeComposition

ROOT = Path(__file__).resolve().parents[2]


def test_official_composition_declares_existing_g7_materialization() -> None:
    annotations = OfficialRuntimeComposition.__annotations__

    assert "g7_approved_learning_memory_materialization" in annotations


def test_official_factory_constructs_existing_g7_materialization_once() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(encoding="utf-8")

    assert source.count("GovernedG7ApprovedLearningMemoryMaterializationV1()") == 1
    assert "g7_approved_learning_memory_materialization=" in source


def test_reachability_does_not_auto_materialize_or_cross_write_boundary() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(encoding="utf-8")

    assert "GovernedG7ApprovedLearningMemoryMaterializationV1" in source
    assert ".build_structural_eligibility(" not in source
    assert ".propose(" not in source
    assert "remember_governed_learning(" not in source


def test_existing_g7_materialization_remains_the_exposed_contract() -> None:
    materialization = GovernedG7ApprovedLearningMemoryMaterializationV1()

    assert (
        materialization.__class__
        is GovernedG7ApprovedLearningMemoryMaterializationV1
    )


def test_protected_authorities_remain_byte_identical() -> None:
    reasoning = hashlib.sha256(
        (ROOT / "app/governed_reasoning_runtime.py").read_bytes()
    ).hexdigest()

    assert reasoning == (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    )
