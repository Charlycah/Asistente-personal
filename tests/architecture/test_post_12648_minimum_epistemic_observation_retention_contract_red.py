from __future__ import annotations

import importlib
import inspect
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.governed_reasoning.epistemic_sufficiency import EpistemicSufficiencyStatus
from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessment,
    GovernedReasoningAssessmentObservation,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityStatus,
)

ROOT = Path(__file__).resolve().parents[2]
RETENTION_MODULE = "core.governed_reasoning.epistemic_observation_retention"
RETENTION_TYPE = "GovernedEpistemicObservationRetentionV1"


def _retention_type():
    try:
        module = importlib.import_module(RETENTION_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: no bounded persistence transport exists yet for admitted minimum "
            "epistemic observations"
        )
    retention = getattr(module, RETENTION_TYPE, None)
    if retention is None:
        pytest.fail(
            "RED: epistemic observation retention has no bounded V1 transport surface"
        )
    return retention


def _observation(*, suffix: str, source_reference: str = "reasoning-source:alpha"):
    return GovernedReasoningAssessmentObservation(
        quality_assessment_id=f"reasoning-quality-{suffix}",
        quality_status=GovernedReasoningQualityStatus.ADEQUATE,
        sufficiency_assessment_id=f"epistemic-sufficiency-{suffix}",
        sufficiency_status=EpistemicSufficiencyStatus.SUFFICIENT,
        source_reference=source_reference,
        world_snapshot_id=f"world-snapshot-{suffix}",
        quality_source_fingerprint=f"quality-fingerprint-{suffix}",
        sufficiency_source_fingerprint=f"sufficiency-fingerprint-{suffix}",
    )


def test_red_bounded_retention_surface_exists_without_new_cognitive_authority() -> None:
    retention = _retention_type()
    source = inspect.getsource(retention)

    assert "retain" in source
    assert "retrieve" in source
    assert "governed_reasoning" in source


def test_red_retained_observation_survives_retention_reinstantiation(
    tmp_path: Path,
) -> None:
    retention_type = _retention_type()
    storage_path = tmp_path / "epistemic-observations"
    observation = _observation(suffix="one")

    first = retention_type(storage_path=storage_path)
    first.retain(observation)

    second = retention_type(storage_path=storage_path)
    restored = second.retrieve(source_reference=observation.source_reference)

    assert restored == (observation,)


def test_red_retention_is_idempotent_and_retrieval_is_deterministic(
    tmp_path: Path,
) -> None:
    retention_type = _retention_type()
    retention = retention_type(storage_path=tmp_path / "epistemic-observations")
    second = _observation(suffix="two")
    first = _observation(suffix="one")

    retention.retain(second)
    retention.retain(first)
    retention.retain(first)

    restored = retention.retrieve(source_reference=first.source_reference)
    restored_ids = tuple(item.quality_assessment_id for item in restored)
    assert restored_ids == tuple(sorted(set(restored_ids)))
    assert len(restored) == 2


def test_red_retrieval_is_exactly_scoped_by_existing_source_lineage(
    tmp_path: Path,
) -> None:
    retention_type = _retention_type()
    retention = retention_type(storage_path=tmp_path / "epistemic-observations")
    alpha = _observation(suffix="alpha", source_reference="reasoning-source:alpha")
    beta = _observation(suffix="beta", source_reference="reasoning-source:beta")

    retention.retain(alpha)
    retention.retain(beta)

    assert retention.retrieve(source_reference="reasoning-source:alpha") == (alpha,)
    assert retention.retrieve(source_reference="reasoning-source:beta") == (beta,)
    assert retention.retrieve(source_reference="reasoning-source:missing") == ()


def test_red_retention_rejects_non_admitted_or_synthetic_material(
    tmp_path: Path,
) -> None:
    retention_type = _retention_type()
    retention = retention_type(storage_path=tmp_path / "epistemic-observations")
    synthetic = SimpleNamespace(
        quality_assessment_id="reasoning-quality-synthetic",
        sufficiency_assessment_id="epistemic-sufficiency-synthetic",
        source_reference="reasoning-source:alpha",
        world_snapshot_id="world-snapshot-synthetic",
    )

    with pytest.raises((TypeError, ValueError)):
        retention.retain(synthetic)


def test_contract_observation_is_already_the_minimum_sufficient_domain_model() -> None:
    names = {item.name for item in fields(GovernedReasoningAssessmentObservation)}
    assert {
        "quality_assessment_id",
        "quality_status",
        "sufficiency_assessment_id",
        "sufficiency_status",
        "source_reference",
        "world_snapshot_id",
        "quality_source_fingerprint",
        "sufficiency_source_fingerprint",
    }.issubset(names)
    assert "method_provenance" not in names
    assert "reasoning_state" not in names
    assert "intellectual_identity_id" not in names


def test_contract_existing_admission_validates_exact_quality_sufficiency_lineage(
) -> None:
    source = inspect.getsource(GovernedReasoningAssessmentObservation.from_assessments)
    validation = inspect.getsource(
        GovernedReasoningAssessmentObservation._validate_assessment_pair
    )

    assert "_validate_assessment_pair" in source
    assert "source_epistemic_sufficiency_assessment_id" in validation
    assert "source_reference" in validation
    assert "world_snapshot_id" in validation
    assert "source_fingerprint" in validation


def test_contract_longitudinal_assessment_remains_derived_and_non_persistent() -> None:
    names = {item.name for item in fields(GovernedLongitudinalReasoningAssessment)}
    assert "persists_results" in names
    assert "creates_memory" in names
    assert "creates_learning_candidate" in names

    observation = _observation(suffix="constitutional")
    from core.governed_reasoning.longitudinal_reasoning_assessment import (
        GovernedLongitudinalReasoningAssessmentFoundationV1,
    )

    result = GovernedLongitudinalReasoningAssessmentFoundationV1().assess(
        (observation,)
    )
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.invokes_reflection is False
    assert result.authorizes_review is False


def test_contract_retention_does_not_create_parallel_brain_memory_or_history_store(
) -> None:
    forbidden = (
        "core/metacognitive_memory.py",
        "core/longitudinal_metacognition_manager.py",
        "core/reasoning_history_repository.py",
        "app/metacognitive_brain.py",
        "app/reasoning_history_repository.py",
    )
    for relative_path in forbidden:
        assert not (ROOT / relative_path).exists()
