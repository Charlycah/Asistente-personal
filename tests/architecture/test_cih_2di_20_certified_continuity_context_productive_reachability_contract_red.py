from __future__ import annotations

import hashlib
import importlib
import inspect
from dataclasses import replace
from pathlib import Path

import pytest

from app.positive_same_explanatory_model_continuity_consumer import (
    PositiveSameExplanatoryModelContinuitySelection,
)
from core.reasoning_runtime_integration import ReasoningRuntimeContributor

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PATH = ROOT / "app/governed_reasoning_runtime.py"
CERTIFIED_RUNTIME_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)
SURFACE_MODULE = (
    "app.positive_same_explanatory_model_continuity_productive_surface"
)
SURFACE_CLASS = "PositiveSameExplanatoryModelContinuityProductiveSurfaceV1"
PROTECTED_FILES = {
    "app/positive_same_explanatory_model_continuity_consumer.py": (
        "20b2b0b72168e8dae8617c3d8f8865700c62a9b186435e6370317412e08fd90f"
    ),
    "app/positive_same_explanatory_model_continuity_context_projection.py": (
        "908c2d3a8762d07974486a838516fa27f987640e2bf468802f677f768dce6d4d"
    ),
    "app/governed_explanatory_model_revision.py": (
        "d9d420442c72b588ea7d70000fed821b63b042cd1b83d5fb48f87649d09c92b4"
    ),
}


def _surface_class():
    try:
        module = importlib.import_module(SURFACE_MODULE)
    except ModuleNotFoundError:
        return None
    return getattr(module, SURFACE_CLASS, None)


def _contributor_parameters():
    return inspect.signature(ReasoningRuntimeContributor.contribute).parameters


def _green_shape_present() -> bool:
    parameters = _contributor_parameters()
    return (
        _surface_class() is not None
        and "continuity_selection" in parameters
        and "continuity_context_surface" in parameters
    )


def test_cih_2di_20b_residual_requires_external_surface_and_transient_transport(
) -> None:
    runtime_digest = hashlib.sha256(RUNTIME_PATH.read_bytes()).hexdigest()
    assert runtime_digest == CERTIFIED_RUNTIME_SHA256

    assert _green_shape_present(), (
        "CIH-2DI.20B RED: the byte-protected runtime is preserved, but no minimal "
        "external DI.19-delegating continuity surface plus transient contributor "
        "transport exists yet"
    )


@pytest.fixture(autouse=True)
def _require_external_reachability_surface(request: pytest.FixtureRequest):
    if request.node.name == (
        "test_cih_2di_20b_residual_requires_external_surface_and_transient_transport"
    ):
        return
    if not _green_shape_present():
        pytest.skip("CIH-2DI.20B RED external reachability is intentionally absent")


def test_cih_2di_20b_runtime_remains_byte_identical() -> None:
    digest = hashlib.sha256(RUNTIME_PATH.read_bytes()).hexdigest()
    assert digest == CERTIFIED_RUNTIME_SHA256


def test_cih_2di_20b_surface_delegates_existing_di19_with_exact_provenance() -> None:
    surface = _surface_class()()
    selection = PositiveSameExplanatoryModelContinuitySelection(
        candidate_model_id="model-prior-1",
        assessment_id="assessment-same-1",
    )
    context = surface.project(selection=selection)
    assert context is not None
    assert context.candidate_model_id == selection.candidate_model_id
    assert context.assessment_id == selection.assessment_id
    assert context.context_lines() == surface.context_lines(selection=selection)


def test_cih_2di_20b_surface_fails_closed_for_invalid_selection() -> None:
    surface = _surface_class()()
    selection = PositiveSameExplanatoryModelContinuitySelection(
        candidate_model_id="model-prior-1",
        assessment_id="assessment-same-1",
    )
    invalid = replace(selection, authorizes_revision=True)
    assert surface.project(selection=invalid) is None
    assert surface.context_lines(selection=invalid) == ()


def test_cih_2di_20b_contributor_accepts_only_transient_continuity_inputs() -> None:
    parameters = _contributor_parameters()
    assert "continuity_selection" in parameters
    assert "continuity_context_surface" in parameters
    assert parameters["continuity_selection"].default is None
    assert parameters["continuity_context_surface"].default is None


def test_cih_2di_20b_contributor_remains_composition_only() -> None:
    source = inspect.getsource(ReasoningRuntimeContributor.contribute)
    assert "continuity_context_surface" in source
    assert ".context_lines(" in source
    forbidden = (
        "LongitudinalIntellectualIdentity",
        "PositiveSameExplanatoryModelContinuityContextProjectionV1",
        "GovernedEvidenceDrivenExplanatoryModelRevisionV1",
    )
    assert all(token not in source for token in forbidden)


def test_cih_2di_20b_surface_is_not_parallel_runtime_or_store() -> None:
    module = importlib.import_module(SURFACE_MODULE)
    source = inspect.getsource(module)
    forbidden = (
        "GovernedLongitudinalIntellectualIdentityFoundationV1",
        "GovernedEvidenceDrivenExplanatoryModelRevisionV1",
        "CanonicalProductiveReasoningSource",
        "OfficialGovernedReasoningRuntimeGateway",
        "ContinuityStore",
        "continuity_selections =",
        "continuity_contexts =",
    )
    assert all(token not in source for token in forbidden)


def test_cih_2di_20b_absent_inputs_preserve_optional_behavior() -> None:
    parameters = _contributor_parameters()
    assert parameters["continuity_selection"].default is None
    assert parameters["continuity_context_surface"].default is None


def test_cih_2di_20b_preserves_existing_semantic_owners() -> None:
    for relative_path, certified_hash in PROTECTED_FILES.items():
        current_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert current_hash == certified_hash
