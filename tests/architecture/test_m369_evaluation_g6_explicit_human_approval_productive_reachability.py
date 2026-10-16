from __future__ import annotations

import hashlib
from pathlib import Path

from app.governed_g6_explicit_human_learning_approval import (
    GovernedG6ExplicitHumanLearningApprovalV1,
)
from app.official_runtime_composition import OfficialRuntimeComposition

ROOT = Path(__file__).resolve().parents[2]


def test_official_composition_declares_existing_g6_human_approval() -> None:
    annotations = OfficialRuntimeComposition.__annotations__

    assert "g6_explicit_human_learning_approval" in annotations


def test_official_factory_constructs_existing_g6_human_approval_once() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(encoding="utf-8")

    assert source.count("GovernedG6ExplicitHumanLearningApprovalV1()") == 1
    assert "g6_explicit_human_learning_approval=" in source


def test_reachability_does_not_auto_approve_or_cross_g7_boundary() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(encoding="utf-8")

    assert "GovernedG6ExplicitHumanLearningApprovalV1" in source
    assert "GovernedExplicitHumanLearningApprovalResponse(" not in source
    assert "OfficialMemoryGateway(" not in source


def test_existing_g6_human_approval_remains_the_exposed_contract() -> None:
    approval = GovernedG6ExplicitHumanLearningApprovalV1()

    assert approval.__class__ is GovernedG6ExplicitHumanLearningApprovalV1


def test_protected_authorities_remain_byte_identical() -> None:
    reasoning = hashlib.sha256(
        (ROOT / "app/governed_reasoning_runtime.py").read_bytes()
    ).hexdigest()

    assert reasoning == (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    )
