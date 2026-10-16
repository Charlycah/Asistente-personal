from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.internal_world_model_foundation import (
    InternalWorldAuthority,
    InternalWorldDomain,
)


def test_m367_1_declares_one_internal_world_authority() -> None:
    snapshot = InternalWorldModelFoundation().snapshot

    assert snapshot.schema_version == "m367.1"
    assert snapshot.canonical_authority == "internal_world_model"
    assert {item.authority_key for item in snapshot.authorities} == {
        "internal_world_model"
    }


def test_m367_1_declares_every_world_domain_once() -> None:
    snapshot = InternalWorldModelFoundation().snapshot

    assert snapshot.supported_domains == tuple(InternalWorldDomain)
    assert tuple(item.domain for item in snapshot.authorities) == tuple(
        InternalWorldDomain
    )


def test_existing_mental_model_is_reused_not_replaced() -> None:
    authority = InternalWorldModelFoundation().snapshot.authority_for("self")

    assert authority.implementation_path == (
        "core.adaptive_cognition.mental_models:MentalModel"
    )


def test_context_reuses_unified_cognitive_blackboard() -> None:
    authority = InternalWorldModelFoundation().snapshot.authority_for("context")

    assert "UnifiedCognitiveBlackboard" in authority.implementation_path
    assert authority.runtime_connected is True


def test_memory_reuses_canonical_memory_facade() -> None:
    authority = InternalWorldModelFoundation().snapshot.authority_for("memory")

    assert authority.implementation_path == (
        "app.canonical_memory_facade:CanonicalMemoryFacade"
    )
    assert authority.persistent is True


def test_capabilities_do_not_imply_authorization() -> None:
    authority = InternalWorldModelFoundation().snapshot.authority_for(
        InternalWorldDomain.CAPABILITIES
    )

    assert authority.implementation_path == (
        "core.capability_registry:CapabilityRegistry"
    )
    assert "sin autorizarlas" in authority.purpose


def test_m367_1_is_read_only_and_adds_no_inference_or_persistence() -> None:
    snapshot = InternalWorldModelFoundation().snapshot

    assert snapshot.read_only is True
    assert snapshot.inference_added is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False
    assert snapshot.consciousness_claimed is False


def test_authority_contract_rejects_invalid_implementation_path() -> None:
    with pytest.raises(ValueError, match="module:Symbol"):
        InternalWorldAuthority(
            domain=InternalWorldDomain.SELF,
            authority_key="internal_world_model",
            implementation_path="invalid",
            purpose="test",
            runtime_connected=False,
            persistent=False,
        )


def test_existing_world_model_components_remain_available() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "core/adaptive_cognition/mental_models.py").exists()
    assert (root / "core/unified_cognitive_blackboard.py").exists()
    assert (root / "core/mental_state.py").exists()
    assert (root / "core/capability_registry.py").exists()


def test_m367_1_documentation_records_governed_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M367_1_INTERNAL_WORLD_MODEL_FOUNDATION.md").read_text(
        encoding="utf-8"
    )

    assert "MentalModel" in document
    assert "UnifiedCognitiveBlackboard" in document
    assert "no agrega inferencia" in document
    assert "M367.1" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M367.1 — Internal World Model Foundation" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
