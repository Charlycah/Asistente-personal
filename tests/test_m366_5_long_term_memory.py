from pathlib import Path

import pytest

from app.long_term_memory_foundation import LongTermMemoryFoundation
from core.long_term_memory_foundation import (
    LongTermAdmissionMode,
    LongTermMemoryAuthority,
    LongTermMemoryLayer,
    LongTermRetentionMode,
)


def test_m366_5_declares_existing_long_term_layers_once() -> None:
    snapshot = LongTermMemoryFoundation().snapshot

    assert snapshot.schema_version == "m366.5"
    assert tuple(item.layer for item in snapshot.authorities) == tuple(
        LongTermMemoryLayer
    )


def test_m366_5_preserves_one_canonical_long_term_authority() -> None:
    snapshot = LongTermMemoryFoundation().snapshot

    assert snapshot.canonical_authority == "memory_gateway"
    assert {item.authority_key for item in snapshot.authorities} == {
        "memory_gateway"
    }


def test_durable_personal_memory_reuses_existing_runtime() -> None:
    authority = LongTermMemoryFoundation().snapshot.authority_for(
        "durable_personal_memory"
    )

    assert authority.implementation_path == (
        "core.memory_runtime_integration:MemoryRuntimeIntegration"
    )
    assert authority.admission_mode is LongTermAdmissionMode.EXPLICIT_REQUEST
    assert authority.retention_mode is (
        LongTermRetentionMode.ACTIVE_UNTIL_REVISED_OR_ARCHIVED
    )
    assert authority.persistent is True


def test_revisable_knowledge_preserves_revision_history() -> None:
    authority = LongTermMemoryFoundation().snapshot.authority_for(
        "revisable_knowledge"
    )

    assert authority.implementation_path == (
        "domain.governed_permanent_knowledge:GovernedPermanentKnowledge"
    )
    assert authority.retention_mode is LongTermRetentionMode.REVISION_HISTORY


def test_household_memory_preserves_supervised_lifecycle() -> None:
    authority = LongTermMemoryFoundation().snapshot.authority_for(
        "household_lifecycle"
    )

    assert authority.implementation_path == (
        "core.household_memory:HouseholdMemoryManager"
    )
    assert authority.admission_mode is (
        LongTermAdmissionMode.SUPERVISED_LIFECYCLE
    )


def test_consolidation_and_forgetting_remain_governed() -> None:
    snapshot = LongTermMemoryFoundation().snapshot

    assert snapshot.consolidation_requires_governance is True
    assert snapshot.forgetting_is_reviewable is True
    assert all(
        item.automatic_consolidation is False for item in snapshot.authorities
    )
    assert all(
        item.irreversible_forgetting is False for item in snapshot.authorities
    )


def test_continuity_does_not_claim_consciousness() -> None:
    snapshot = LongTermMemoryFoundation().snapshot

    assert snapshot.autobiographical_continuity_supported is True
    assert snapshot.consciousness_established is False
    assert all(item.consciousness_claim is False for item in snapshot.authorities)


def test_authority_rejects_automatic_irreversible_or_consciousness_claims() -> None:
    common = dict(
        layer=LongTermMemoryLayer.DURABLE_PERSONAL_MEMORY,
        authority_key="memory_gateway",
        implementation_path="module:Symbol",
        purpose="test",
        admission_mode=LongTermAdmissionMode.EXPLICIT_REQUEST,
        retention_mode=LongTermRetentionMode.ACTIVE_UNTIL_REVISED_OR_ARCHIVED,
        persistent=True,
        runtime_connected=False,
    )
    with pytest.raises(ValueError, match="automatic consolidation"):
        LongTermMemoryAuthority(**common, automatic_consolidation=True)
    with pytest.raises(ValueError, match="irreversible forgetting"):
        LongTermMemoryAuthority(**common, irreversible_forgetting=True)
    with pytest.raises(ValueError, match="machine consciousness"):
        LongTermMemoryAuthority(**common, consciousness_claim=True)


def test_existing_long_term_implementations_remain_available() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "core/memory_runtime_integration/runtime.py").exists()
    assert (root / "domain/governed_permanent_knowledge.py").exists()
    assert (root / "core/household_memory.py").exists()


def test_m366_5_documentation_and_root_register_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M366_5_LONG_TERM_MEMORY.md").read_text(
        encoding="utf-8"
    )

    assert "MemoryRuntimeIntegration" in document
    assert "GovernedPermanentKnowledge" in document
    assert "HouseholdMemoryManager" in document
    assert "continuidad autobiográfica no demuestra consciencia" in document
    assert "M366.5" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M366.5 — Long-Term Memory" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
