from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessment,
    GovernedLongitudinalReasoningAssessmentFoundationV1,
    GovernedLongitudinalReasoningStatus,
)
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]
PROTECTED_RUNTIME = ROOT / "app" / "governed_reasoning_runtime.py"
EXPECTED_PROTECTED_RUNTIME_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)


def test_red_productive_retention_exposes_exact_admitted_observation() -> None:
    helper = GovernedRuntimePreparation._retain_productive_epistemic_observation
    source = inspect.getsource(helper)

    assert "-> GovernedReasoningAssessmentObservation | None" in source
    assert "return observation" in source


def test_red_preparation_has_bounded_longitudinal_assessment_composer() -> None:
    helper = getattr(
        GovernedRuntimePreparation,
        "_compose_productive_longitudinal_reasoning_assessment",
        None,
    )
    assert helper is not None

    source = inspect.getsource(helper)
    assert "retention.retrieve" in source
    assert "source_reference=observation.source_reference" in source
    assert "GovernedLongitudinalReasoningAssessmentFoundationV1" in source
    assert ".assess(" in source


def test_red_longitudinal_composer_is_fail_closed_and_does_not_widen_scope() -> None:
    helper = getattr(
        GovernedRuntimePreparation,
        "_compose_productive_longitudinal_reasoning_assessment",
        None,
    )
    assert helper is not None

    source = inspect.getsource(helper)
    assert "if observation is None or retention is None" in source
    assert "except (TypeError, ValueError" in source
    forbidden = (
        "topic",
        "session",
        "memory",
        "method_outcome",
        "method_provenance",
        "predecessor",
        "similar",
    )
    lowered = source.lower()
    for token in forbidden:
        assert token not in lowered


def test_red_prepare_supplies_admitted_observation_to_longitudinal_composer() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)

    assert (
        "epistemic_observation = self._retain_productive_epistemic_observation"
        in source
    )
    assert "_compose_productive_longitudinal_reasoning_assessment" in source
    assert "observation=epistemic_observation" in source
    assert "retention=epistemic_observation_retention" in source


def test_red_productive_composition_stops_at_derived_assessment() -> None:
    helper = getattr(
        GovernedRuntimePreparation,
        "_compose_productive_longitudinal_reasoning_assessment",
        None,
    )
    assert helper is not None

    source = inspect.getsource(helper).lower()
    assert "return" in source
    forbidden = (
        "initiative",
        "reflection",
        "learning",
        "planning",
        "authorization",
        "execution",
        "prompt",
        "inference_request",
        ".retain(",
    )
    for token in forbidden:
        assert token not in source


def test_contract_existing_foundation_remains_comparability_authority() -> None:
    source = inspect.getsource(
        GovernedLongitudinalReasoningAssessmentFoundationV1._validate_series
    )
    assert "source_reference" in source
    assert "not comparable" in source
    assert "quality_assessment_id" in source
    assert "sufficiency_assessment_id" in source


def test_contract_insufficient_history_remains_valid_governed_result() -> None:
    assert (
        GovernedLongitudinalReasoningAssessmentFoundationV1.MINIMUM_PATTERN_EPISODES
        == 2
    )
    source = inspect.getsource(
        GovernedLongitudinalReasoningAssessmentFoundationV1._derive_status
    )
    assert "INSUFFICIENT_HISTORY" in source


def test_contract_longitudinal_assessment_remains_derived_and_nonpersistent() -> None:
    fields = GovernedLongitudinalReasoningAssessment.__dataclass_fields__
    assert fields["persists_results"].default is False
    assert fields["creates_memory"].default is False
    assert fields["creates_learning_candidate"].default is False
    assert fields["invokes_reflection"].default is False
    assert fields["invokes_learning"].default is False
    assert fields["authorizes_review"].default is False
    assert fields["authorizes_stopping"].default is False


def test_contract_status_surface_does_not_create_temporal_or_identity_claims() -> None:
    assert set(GovernedLongitudinalReasoningStatus) == {
        GovernedLongitudinalReasoningStatus.INSUFFICIENT_HISTORY,
        GovernedLongitudinalReasoningStatus.CONSISTENTLY_ADEQUATE,
        GovernedLongitudinalReasoningStatus.RECURRENT_LIMITATION,
        GovernedLongitudinalReasoningStatus.RECURRENT_REVIEW_REQUIRED,
        GovernedLongitudinalReasoningStatus.MIXED,
    }
    source = inspect.getsource(GovernedLongitudinalReasoningAssessmentFoundationV1)
    assert "longitudinal:not_temporal_trend" in source
    assert "same" not in source.lower()


def test_contract_productive_composition_creates_no_parallel_authority_or_store(
) -> None:
    forbidden = (
        "core/longitudinal_metacognition_manager.py",
        "core/longitudinal_assessment_repository.py",
        "core/reasoning_history_repository.py",
        "app/longitudinal_metacognition_runtime.py",
        "app/longitudinal_assessment_store.py",
    )
    for relative_path in forbidden:
        assert not (ROOT / relative_path).exists()


def test_contract_protected_reasoning_runtime_remains_byte_identical() -> None:
    digest = hashlib.sha256(PROTECTED_RUNTIME.read_bytes()).hexdigest()
    assert digest == EXPECTED_PROTECTED_RUNTIME_SHA256
