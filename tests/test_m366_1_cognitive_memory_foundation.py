from pathlib import Path

import pytest

from app.cognitive_memory_foundation import CognitiveMemoryFoundation
from core.cognitive_memory_foundation import (
    CognitiveMemoryDomain,
    CognitiveMemoryKind,
    CognitiveMemoryPersistence,
    CognitiveMemoryWriteMode,
)


def test_foundation_declares_all_four_memory_kinds_once() -> None:
    snapshot = CognitiveMemoryFoundation().snapshot

    assert snapshot.schema_version == "m366.1"
    assert tuple(domain.kind for domain in snapshot.domains) == tuple(
        CognitiveMemoryKind
    )


def test_foundation_reuses_the_canonical_memory_authority() -> None:
    snapshot = CognitiveMemoryFoundation().snapshot

    assert snapshot.canonical_authority == "memory_gateway"
    assert snapshot.domain_for("episodic").authority_key == "episodic_memory"
    assert snapshot.domain_for("semantic").authority_key == "memory_gateway"
    assert snapshot.domain_for("procedural").authority_key == "memory_gateway"
    assert snapshot.domain_for("long_term").authority_key == "memory_gateway"


def test_m366_1_does_not_enable_persistence_or_automatic_learning() -> None:
    snapshot = CognitiveMemoryFoundation().snapshot

    assert snapshot.persistence_enabled is False
    assert snapshot.automatic_learning_enabled is False
    assert all(domain.operational is False for domain in snapshot.domains)


def test_semantic_memory_requires_explicit_acceptance() -> None:
    semantic = CognitiveMemoryFoundation().snapshot.domain_for(
        CognitiveMemoryKind.SEMANTIC
    )

    assert semantic.persistence is CognitiveMemoryPersistence.PERSISTENT
    assert semantic.write_mode is CognitiveMemoryWriteMode.EXPLICIT_ACCEPTANCE
    assert semantic.stores_personal_data is True


def test_procedural_memory_is_descriptive_not_executable() -> None:
    procedural = CognitiveMemoryFoundation().snapshot.domain_for("procedural")

    assert procedural.stores_personal_data is False
    assert procedural.operational is False
    assert procedural.write_mode is CognitiveMemoryWriteMode.EXPLICIT_ACCEPTANCE


def test_episodic_and_long_term_memory_require_governed_consolidation() -> None:
    snapshot = CognitiveMemoryFoundation().snapshot

    assert snapshot.domain_for("episodic").write_mode is (
        CognitiveMemoryWriteMode.GOVERNED_CONSOLIDATION
    )
    assert snapshot.domain_for("long_term").write_mode is (
        CognitiveMemoryWriteMode.GOVERNED_CONSOLIDATION
    )


def test_domain_rejects_blank_governance_fields() -> None:
    with pytest.raises(ValueError, match="purpose must not be blank"):
        CognitiveMemoryDomain(
            kind=CognitiveMemoryKind.SEMANTIC,
            purpose=" ",
            authority_key="memory_gateway",
            persistence=CognitiveMemoryPersistence.PERSISTENT,
            write_mode=CognitiveMemoryWriteMode.EXPLICIT_ACCEPTANCE,
            stores_personal_data=True,
        )


def test_domain_cannot_become_operational_in_m366_1() -> None:
    with pytest.raises(ValueError, match="must remain non-operational"):
        CognitiveMemoryDomain(
            kind=CognitiveMemoryKind.PROCEDURAL,
            purpose="Procedures",
            authority_key="memory_gateway",
            persistence=CognitiveMemoryPersistence.PERSISTENT,
            write_mode=CognitiveMemoryWriteMode.EXPLICIT_ACCEPTANCE,
            stores_personal_data=False,
            operational=True,
        )


def test_m366_1_documentation_declares_foundation_only_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M366_1_COGNITIVE_MEMORY_FOUNDATION.md").read_text(
        encoding="utf-8"
    )

    assert "CanonicalMemoryFacade" in document
    assert "episódica" in document
    assert "semántica" in document
    assert "procedimental" in document
    assert "largo plazo" in document
    assert "no crea un nuevo store" in document


def test_root_documents_preserve_m366_1_history() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    architecture = (root / "CHANGELOG_ARCHITECTURE.md").read_text(encoding="utf-8")
    plan = (root / "docs/M360_0E_PHASE_II_MASTER_PLAN.md").read_text(
        encoding="utf-8"
    )

    assert "M366_1_COGNITIVE_MEMORY_FOUNDATION.md" in readme
    assert "## M366.1 — Cognitive Memory Foundation" in changelog
    assert "## M366.1 — Cognitive Memory Foundation" in architecture
    assert "M366 — Memoria Cognitiva" in plan
