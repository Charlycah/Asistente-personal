from __future__ import annotations

import hashlib
from pathlib import Path

from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationV1,
)
from app.official_runtime_composition import OfficialRuntimeComposition

ROOT = Path(__file__).resolve().parents[2]


def test_official_composition_declares_existing_m369_evaluation() -> None:
    annotations = OfficialRuntimeComposition.__annotations__

    assert "learning_candidate_m369_evaluation" in annotations


def test_official_factory_constructs_existing_m369_evaluation_once() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(
        encoding="utf-8"
    )

    assert source.count("GovernedLearningCandidateM369EvaluationV1()") == 1
    assert "learning_candidate_m369_evaluation=" in source


def test_reachability_reuses_existing_evaluation_without_new_authority() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(
        encoding="utf-8"
    )

    assert "GovernedLearningCandidateM369EvaluationV1" in source
    assert "SafeLearningPolicies(" not in source
    assert "LearningFoundation(" not in source
    assert "OfficialMemoryGateway(" not in source


def test_existing_m369_evaluation_remains_the_exposed_contract() -> None:
    evaluator = GovernedLearningCandidateM369EvaluationV1()

    assert evaluator.__class__ is GovernedLearningCandidateM369EvaluationV1


def test_protected_authorities_remain_byte_identical() -> None:
    reasoning = hashlib.sha256(
        (ROOT / "app/governed_reasoning_runtime.py").read_bytes()
    ).hexdigest()

    assert reasoning == (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    )
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source
