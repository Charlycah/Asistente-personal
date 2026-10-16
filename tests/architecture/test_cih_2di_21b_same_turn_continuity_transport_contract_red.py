from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

import pytest

from app.longitudinal_intellectual_identity_productive_adapter import (
    LongitudinalIntellectualIdentityProductiveAdapterV1,
)
from core.cognitive_runtime_orchestration.models import CognitiveRuntimeContributor
from core.cognitive_runtime_orchestration.runtime import CognitiveRuntimeOrchestrator
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PATH = ROOT / "app/governed_reasoning_runtime.py"
CERTIFIED_RUNTIME_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)
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


def _adapter_invokes_di18() -> bool:
    source = inspect.getsource(LongitudinalIntellectualIdentityProductiveAdapterV1)
    return (
        "PositiveSameExplanatoryModelContinuityConsumerV1" in source
        and ".consume(" in source
        and "bounded_candidate" in source
        and "assessment" in source
    )


def _orchestrator_accepts_turn_bound_transport() -> bool:
    parameters = inspect.signature(CognitiveRuntimeOrchestrator.enrich).parameters
    return (
        "continuity_selection" in parameters
        and "continuity_context_surface" in parameters
        and parameters["continuity_selection"].default is None
        and parameters["continuity_context_surface"].default is None
    )


def _preparation_forwards_same_turn_continuity() -> bool:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    return (
        "continuity_selection" in source
        and "continuity_context_surface" in source
        and "cognitive_runtime.enrich(" in source
    )


def _green_shape_present() -> bool:
    return (
        _adapter_invokes_di18()
        and _orchestrator_accepts_turn_bound_transport()
        and _preparation_forwards_same_turn_continuity()
    )


def test_cih_2di_21b_residual_requires_same_turn_di18_and_opaque_transport() -> None:
    runtime_digest = hashlib.sha256(RUNTIME_PATH.read_bytes()).hexdigest()
    assert runtime_digest == CERTIFIED_RUNTIME_SHA256

    assert _green_shape_present(), (
        "CIH-2DI.21B RED: DI.20B remains reachable and the protected runtime is "
        "preserved, but the productive turn does not yet invoke existing DI.18 "
        "with candidate + assessment and transport its certified selection "
        "opaquely through preparation/orchestration"
    )


@pytest.fixture(autouse=True)
def _require_same_turn_reachability(request: pytest.FixtureRequest):
    if request.node.name == (
        "test_cih_2di_21b_residual_requires_same_turn_di18_and_opaque_transport"
    ):
        return
    if not _green_shape_present():
        pytest.skip("CIH-2DI.21B RED same-turn transport is intentionally absent")


def test_cih_2di_21b_runtime_remains_byte_identical() -> None:
    digest = hashlib.sha256(RUNTIME_PATH.read_bytes()).hexdigest()
    assert digest == CERTIFIED_RUNTIME_SHA256


def test_cih_2di_21b_adapter_reuses_existing_di18_without_reassessing_same() -> None:
    source = inspect.getsource(LongitudinalIntellectualIdentityProductiveAdapterV1)
    assert "PositiveSameExplanatoryModelContinuityConsumerV1" in source
    assert ".consume(" in source
    assert source.count("GovernedLongitudinalIntellectualIdentityFoundationV1") == 1


def test_cih_2di_21b_transport_is_optional_and_turn_bound() -> None:
    parameters = inspect.signature(CognitiveRuntimeOrchestrator.enrich).parameters
    assert parameters["continuity_selection"].default is None
    assert parameters["continuity_context_surface"].default is None


def test_cih_2di_21b_orchestrator_remains_opaque_to_same_semantics() -> None:
    source = inspect.getsource(CognitiveRuntimeOrchestrator)
    forbidden = (
        "LongitudinalIntellectualIdentityStatus",
        "PositiveSameExplanatoryModelContinuityConsumerV1",
        "GovernedLongitudinalIntellectualIdentityFoundationV1",
        "GovernedEvidenceDrivenExplanatoryModelRevisionV1",
    )
    assert all(token not in source for token in forbidden)


def test_cih_2di_21b_generic_contributor_protocol_is_not_expanded() -> None:
    parameters = inspect.signature(CognitiveRuntimeContributor.contribute).parameters
    assert "continuity_selection" not in parameters
    assert "continuity_context_surface" not in parameters


def test_cih_2di_21b_preparation_forwards_without_persistence_or_store() -> None:
    source = inspect.getsource(GovernedRuntimePreparation)
    assert "continuity_selection" in source
    forbidden = (
        "ContinuityStore",
        "continuity_selections =",
        "persist_continuity",
        "save_continuity",
    )
    assert all(token not in source for token in forbidden)


def test_cih_2di_21b_preserves_existing_semantic_owners() -> None:
    for relative_path, certified_hash in PROTECTED_FILES.items():
        current_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert current_hash == certified_hash


def test_cih_2di_21b_no_revision_or_new_authority_coupling() -> None:
    adapter_source = inspect.getsource(
        LongitudinalIntellectualIdentityProductiveAdapterV1
    )
    preparation_source = inspect.getsource(GovernedRuntimePreparation)
    orchestrator_source = inspect.getsource(CognitiveRuntimeOrchestrator)
    combined = "\n".join((adapter_source, preparation_source, orchestrator_source))
    forbidden = (
        "GovernedEvidenceDrivenExplanatoryModelRevisionV1",
        "ContinuityAuthority",
        "ContinuityStore",
    )
    assert all(token not in combined for token in forbidden)
