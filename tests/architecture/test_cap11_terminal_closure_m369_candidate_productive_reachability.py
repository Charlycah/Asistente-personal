from __future__ import annotations

import hashlib
from pathlib import Path

from app.governed_investigation_learning_candidate_admission import (
    GovernedInvestigationLearningCandidateAdmissionV1,
)
from app.official_runtime_composition import OfficialRuntimeComposition

ROOT = Path(__file__).resolve().parents[2]


def test_official_composition_declares_existing_g5_admission() -> None:
    annotations = OfficialRuntimeComposition.__annotations__

    assert "investigation_learning_candidate_admission" in annotations


def test_official_factory_constructs_existing_g5_admission_once() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(
        encoding="utf-8"
    )

    assert source.count("GovernedInvestigationLearningCandidateAdmissionV1()") == 1
    assert "investigation_learning_candidate_admission=(" in source


def test_reachability_reuses_existing_admission_without_new_authority() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(
        encoding="utf-8"
    )

    assert "GovernedInvestigationLearningCandidateAdmissionV1" in source
    assert "LearningFoundation(" not in source
    assert "PersonalKnowledgeBaseManager(" not in source
    assert "OfficialMemoryGateway(" not in source


def test_existing_g5_admission_remains_the_exposed_contract() -> None:
    admission = GovernedInvestigationLearningCandidateAdmissionV1()

    assert admission.__class__ is GovernedInvestigationLearningCandidateAdmissionV1


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
