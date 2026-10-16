from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_maturity import (
    COGNITIVE_MATURITY_CATALOG,
    CognitiveMaturityEvidence,
    CognitiveMaturityLevel,
    cognitive_maturity_criterion,
)

EXPECTED_CAPABILITIES = {
    "structured_cognition",
    "memory",
    "communication",
    "knowledge",
    "inner_world",
    "family_empathy",
    "simulated_emotion",
    "perception",
    "learning",
    "analysis",
    "reflection_health",
    "governed_autonomy",
    "own_deep_learning",
    "consciousness",
}


def test_m386_1_catalog_covers_the_complete_agreed_scope() -> None:
    capability_ids = {
        criterion.capability_id for criterion in COGNITIVE_MATURITY_CATALOG
    }
    assert capability_ids == EXPECTED_CAPABILITIES
    assert len(capability_ids) == len(COGNITIVE_MATURITY_CATALOG)


def test_m386_1_high_means_runtime_and_diagnostic_evidence() -> None:
    for criterion in COGNITIVE_MATURITY_CATALOG:
        if criterion.target_level is CognitiveMaturityLevel.HIGH:
            assert CognitiveMaturityEvidence.CONTRACT in criterion.required_evidence
            assert CognitiveMaturityEvidence.UNIT_TEST in criterion.required_evidence
            assert (
                CognitiveMaturityEvidence.ARCHITECTURE_TEST
                in criterion.required_evidence
            )
            assert (
                CognitiveMaturityEvidence.RUNTIME_INTEGRATION
                in criterion.required_evidence
            )
            assert (
                CognitiveMaturityEvidence.OPERATIONAL_DIAGNOSTIC
                in criterion.required_evidence
            )


def test_m386_1_perception_requires_real_channel_certification() -> None:
    perception = cognitive_maturity_criterion("perception")
    assert (
        CognitiveMaturityEvidence.PHYSICAL_CHANNEL_CERTIFICATION
        in perception.required_evidence
    )
    assert any("por separado" in item for item in perception.high_requirements)


def test_m386_1_learning_and_autonomy_remain_human_governed() -> None:
    for capability_id in ("learning", "governed_autonomy"):
        criterion = cognitive_maturity_criterion(capability_id)
        assert CognitiveMaturityEvidence.HUMAN_REVIEW in criterion.required_evidence
    autonomy = cognitive_maturity_criterion("governed_autonomy")
    assert autonomy.target_level is CognitiveMaturityLevel.MEDIUM_HIGH
    assert any("Autoampliación" in item for item in autonomy.exclusions)


def test_m386_1_neural_training_is_research_not_productive_autonomy() -> None:
    neural = cognitive_maturity_criterion("own_deep_learning")
    assert neural.target_level is CognitiveMaturityLevel.MEDIUM
    assert CognitiveMaturityEvidence.RUNTIME_INTEGRATION not in neural.required_evidence
    assert any("actualiza" in item for item in neural.high_requirements)


def test_m386_1_consciousness_cannot_be_promoted_by_the_scale() -> None:
    consciousness = cognitive_maturity_criterion("consciousness")
    assert consciousness.current_level is CognitiveMaturityLevel.NOT_DEMONSTRATED
    assert consciousness.target_level is CognitiveMaturityLevel.NOT_DEMONSTRATED
    assert any("conducta convincente" in item for item in consciousness.exclusions)


def test_m386_1_criteria_are_immutable_and_lookup_rejects_unknown_ids() -> None:
    criterion = cognitive_maturity_criterion("analysis")
    with pytest.raises(FrozenInstanceError):
        criterion.title = "altered"
    with pytest.raises(KeyError):
        cognitive_maturity_criterion("invented_capability")
