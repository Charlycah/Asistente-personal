from pathlib import Path

import pytest

from app.semantic_memory_foundation import SemanticMemoryFoundation
from core.semantic_memory_foundation import (
    SemanticAdmissionMode,
    SemanticMemoryAuthority,
    SemanticMemoryLayer,
)


def test_m366_3_declares_existing_semantic_layers_once() -> None:
    snapshot = SemanticMemoryFoundation().snapshot

    assert snapshot.schema_version == "m366.3"
    assert tuple(item.layer for item in snapshot.authorities) == tuple(
        SemanticMemoryLayer
    )


def test_m366_3_preserves_one_canonical_semantic_authority() -> None:
    snapshot = SemanticMemoryFoundation().snapshot

    assert snapshot.canonical_authority == "memory_gateway"
    assert {item.authority_key for item in snapshot.authorities} == {"memory_gateway"}


def test_governed_facts_reuse_permanent_knowledge() -> None:
    authority = SemanticMemoryFoundation().snapshot.authority_for("governed_facts")

    assert authority.implementation_path == (
        "domain.governed_permanent_knowledge:GovernedPermanentKnowledge"
    )
    assert authority.admission_mode is SemanticAdmissionMode.EXPLICIT_ACCEPTANCE
    assert authority.runtime_connected is False


def test_personal_knowledge_reuses_existing_base() -> None:
    authority = SemanticMemoryFoundation().snapshot.authority_for(
        SemanticMemoryLayer.PERSONAL_KNOWLEDGE
    )

    assert authority.implementation_path == (
        "core.personal_knowledge_base:PersonalKnowledgeBase"
    )
    assert authority.admission_mode is SemanticAdmissionMode.CURATED_ITEM


def test_household_knowledge_preserves_supervised_runtime() -> None:
    authority = SemanticMemoryFoundation().snapshot.authority_for("household_knowledge")

    assert authority.implementation_path == (
        "app.household_knowledge:HouseholdKnowledgeService"
    )
    assert authority.admission_mode is SemanticAdmissionMode.SUPERVISED_CONFIRMATION
    assert authority.runtime_connected is True
    assert authority.persistent is True


def test_external_retrieval_is_not_declared_as_semantic_memory() -> None:
    snapshot = SemanticMemoryFoundation().snapshot

    assert snapshot.external_retrieval_is_memory is False
    assert all(
        "knowledge_gateway" not in item.implementation_path
        for item in snapshot.authorities
    )


def test_m366_3_adds_no_persistence_learning_or_runtime_behavior() -> None:
    snapshot = SemanticMemoryFoundation().snapshot

    assert snapshot.persistence_added is False
    assert snapshot.automatic_learning_added is False
    assert snapshot.runtime_behavior_changed is False
    assert all(item.automatic_promotion is False for item in snapshot.authorities)


def test_authority_rejects_automatic_promotion() -> None:
    with pytest.raises(ValueError, match="cannot enable automatic"):
        SemanticMemoryAuthority(
            layer=SemanticMemoryLayer.GOVERNED_FACTS,
            authority_key="memory_gateway",
            implementation_path="module:Symbol",
            purpose="test",
            admission_mode=SemanticAdmissionMode.EXPLICIT_ACCEPTANCE,
            persistent=False,
            runtime_connected=False,
            automatic_promotion=True,
        )


def test_existing_semantic_implementations_remain_available() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "domain/governed_permanent_knowledge.py").exists()
    assert (root / "core/personal_knowledge_base.py").exists()
    assert (root / "app/household_knowledge.py").exists()


def test_m366_3_documentation_and_root_register_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M366_3_SEMANTIC_MEMORY.md").read_text(encoding="utf-8")

    assert "GovernedPermanentKnowledge" in document
    assert "PersonalKnowledgeBase" in document
    assert "HouseholdKnowledgeService" in document
    assert "recuperación externa no es memoria semántica" in document
    assert "M366.3" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M366.3 — Semantic Memory" in (root / "CHANGELOG.md").read_text(
        encoding="utf-8"
    )
