from __future__ import annotations

import hashlib
import importlib
import inspect
from pathlib import Path

from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessment,
    GovernedLongitudinalReasoningStatus,
)

ROOT = Path(__file__).resolve().parents[2]
MODULE_NAME = (
    "core.governed_reasoning."
    "longitudinal_reasoning_conversational_projection"
)
PROTECTED_RUNTIME = ROOT / "app" / "governed_reasoning_runtime.py"
EXPECTED_PROTECTED_RUNTIME_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)


def _projection_module():
    try:
        return importlib.import_module(MODULE_NAME)
    except ModuleNotFoundError:
        return None


def test_red_bounded_longitudinal_assessment_projection_exists() -> None:
    module = _projection_module()
    assert module is not None
    assert hasattr(module, "GovernedLongitudinalReasoningConversationalProjection")
    assert hasattr(module, "GovernedLongitudinalReasoningConversationalProjectorV1")


def test_red_projection_accepts_only_canonical_longitudinal_assessment() -> None:
    module = _projection_module()
    assert module is not None
    projector = module.GovernedLongitudinalReasoningConversationalProjectorV1
    source = inspect.getsource(projector.project)
    assert "GovernedLongitudinalReasoningAssessment" in source
    forbidden = ("observation", "memory", "method_outcome", "conversation_history")
    lowered = source.lower()
    for token in forbidden:
        assert token not in lowered


def test_red_projection_preserves_all_five_statuses_descriptively() -> None:
    module = _projection_module()
    assert module is not None
    projector = module.GovernedLongitudinalReasoningConversationalProjectorV1
    source = inspect.getsource(projector).lower()
    for status in GovernedLongitudinalReasoningStatus:
        assert status.value in source
    forbidden = ("improving", "declining", "mostly adequate", "probably")
    for token in forbidden:
        assert token not in source


def test_red_projection_is_bounded_derived_and_nonpersistent() -> None:
    module = _projection_module()
    assert module is not None
    projection = module.GovernedLongitudinalReasoningConversationalProjection
    fields = projection.__dataclass_fields__
    assert fields["canonical_authority"].default == "governed_reasoning"
    assert fields["read_only"].default is True
    assert fields["consultative"].default is True
    assert fields["derivational"].default is True
    assert fields["persists_results"].default is False
    assert fields["creates_memory"].default is False
    assert fields["creates_learning_candidate"].default is False


def test_red_projection_stops_at_descriptive_conversational_context() -> None:
    module = _projection_module()
    assert module is not None
    projector = module.GovernedLongitudinalReasoningConversationalProjectorV1
    source = inspect.getsource(projector).lower()
    assert "conversation" in source
    forbidden = (
        "initiative",
        "reflection",
        "learning",
        "planning",
        "authorization",
        "execution",
        "memory.write",
        "retain(",
        "inference_request",
    )
    for token in forbidden:
        assert token not in source


def test_contract_source_assessment_remains_non_authoritative() -> None:
    fields = GovernedLongitudinalReasoningAssessment.__dataclass_fields__
    assert fields["establishes_truth"].default is False
    assert fields["assigns_probability"].default is False
    assert fields["authorizes_review"].default is False
    assert fields["invokes_reflection"].default is False
    assert fields["invokes_learning"].default is False
    assert fields["persists_results"].default is False


def test_contract_status_surface_remains_exact_and_non_temporal() -> None:
    assert set(GovernedLongitudinalReasoningStatus) == {
        GovernedLongitudinalReasoningStatus.INSUFFICIENT_HISTORY,
        GovernedLongitudinalReasoningStatus.CONSISTENTLY_ADEQUATE,
        GovernedLongitudinalReasoningStatus.RECURRENT_LIMITATION,
        GovernedLongitudinalReasoningStatus.RECURRENT_REVIEW_REQUIRED,
        GovernedLongitudinalReasoningStatus.MIXED,
    }
    source = inspect.getsource(GovernedLongitudinalReasoningAssessment)
    assert "establishes_truth: bool = False" in source
    assert "authorizes_review: bool = False" in source


def test_contract_projection_does_not_reuse_wrong_authority_or_store() -> None:
    forbidden = (
        "core/longitudinal_metacognition_manager.py",
        "core/longitudinal_assessment_repository.py",
        "core/memory/longitudinal_assessment_projection.py",
        "app/longitudinal_metacognition_runtime.py",
        "app/longitudinal_assessment_store.py",
    )
    for relative_path in forbidden:
        assert not (ROOT / relative_path).exists()


def test_contract_projection_module_does_not_own_productive_wiring() -> None:
    source = inspect.getsource(_projection_module()).lower()
    assert "llmrequest" not in source
    assert "runtimecomposition" not in source
    assert "governedruntimepreparation" not in source


def test_contract_protected_reasoning_runtime_remains_byte_identical() -> None:
    digest = hashlib.sha256(PROTECTED_RUNTIME.read_bytes()).hexdigest()
    assert digest == EXPECTED_PROTECTED_RUNTIME_SHA256
