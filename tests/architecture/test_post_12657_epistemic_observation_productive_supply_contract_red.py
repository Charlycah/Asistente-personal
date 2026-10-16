from __future__ import annotations

import hashlib
import inspect
from dataclasses import fields
from pathlib import Path

from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedReasoningAssessmentObservation,
)
from core.runtime_composition_root.models import RuntimeCompositionDependencies
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "app" / "runtime_root_factory.py"
PROTECTED_RUNTIME = ROOT / "app" / "governed_reasoning_runtime.py"
EXPECTED_PROTECTED_RUNTIME_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)


def test_red_dependencies_transport_existing_epistemic_observation_retention() -> None:
    names = {item.name for item in fields(RuntimeCompositionDependencies)}
    assert "epistemic_observation_retention" in names


def test_red_factory_builds_configurable_dedicated_retention_transport() -> None:
    source = FACTORY.read_text(encoding="utf-8")

    assert "GovernedEpistemicObservationRetentionV1" in source
    assert "ROBY_EPISTEMIC_OBSERVATION_PATH" in source
    assert ".roby/epistemic_observations" in source
    assert "epistemic_observation_retention=" in source


def test_red_preparation_has_bounded_productive_observation_retention_helper() -> None:
    helper = getattr(
        GovernedRuntimePreparation,
        "_retain_productive_epistemic_observation",
        None,
    )
    assert helper is not None

    source = inspect.getsource(helper)
    assert "GovernedReasoningAssessmentObservation.from_assessments" in source
    assert "retention.retain" in source


def test_red_prepare_supplies_exact_productive_episode_to_retention_helper() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)

    assert "epistemic_observation_retention" in source
    assert "_retain_productive_epistemic_observation" in source
    assert "epistemic_episode=epistemic_episode" in source


def test_red_productive_retention_is_fail_closed_and_does_not_reconstruct_lineage(
) -> None:
    helper = getattr(
        GovernedRuntimePreparation,
        "_retain_productive_epistemic_observation",
        None,
    )
    assert helper is not None

    source = inspect.getsource(helper)
    assert "getattr(epistemic_episode, \"quality\", None)" in source
    assert "getattr(epistemic_episode, \"sufficiency\", None)" in source
    assert "if" in source
    assert "method_outcome" not in source
    assert "method_provenance" not in source
    assert "deepening" not in source
    assert "memory" not in source.lower()


def test_contract_existing_observation_admission_remains_semantic_authority() -> None:
    source = inspect.getsource(GovernedReasoningAssessmentObservation.from_assessments)
    assert "_validate_assessment_pair" in source


def test_contract_retention_remains_existing_governed_reasoning_transport() -> None:
    from core.governed_reasoning.epistemic_observation_retention import (
        GovernedEpistemicObservationRetentionV1,
    )

    assert GovernedEpistemicObservationRetentionV1.CANONICAL_AUTHORITY == (
        "governed_reasoning"
    )
    source = inspect.getsource(GovernedEpistemicObservationRetentionV1)
    assert "retain" in source
    assert "retrieve" in source


def test_contract_productive_supply_does_not_create_parallel_authority() -> None:
    forbidden = (
        "core/epistemic_observation_manager.py",
        "core/metacognitive_persistence_coordinator.py",
        "app/epistemic_observation_manager.py",
        "app/longitudinal_metacognition_runtime.py",
        "app/reasoning_history_service.py",
    )
    for relative_path in forbidden:
        assert not (ROOT / relative_path).exists()


def test_contract_productive_supply_does_not_touch_longitudinal_consumption() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    marker = "_retain_productive_epistemic_observation"
    if marker not in source:
        return
    retention_tail = source[source.index(marker) :]
    assert "GovernedLongitudinalReasoningAssessmentFoundationV1" not in retention_tail
    assert "InitiativeEngine" not in retention_tail


def test_contract_protected_reasoning_runtime_remains_byte_identical() -> None:
    digest = hashlib.sha256(PROTECTED_RUNTIME.read_bytes()).hexdigest()
    assert digest == EXPECTED_PROTECTED_RUNTIME_SHA256
