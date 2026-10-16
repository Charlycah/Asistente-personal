from pathlib import Path

import pytest

from app.episodic_memory_foundation import EpisodicMemoryFoundation
from core.episodic_memory_foundation import (
    EpisodicAdmissionMode,
    EpisodicMemoryAuthority,
    EpisodicMemoryLayer,
)


def test_m366_2_declares_both_existing_episodic_layers_once() -> None:
    snapshot = EpisodicMemoryFoundation().snapshot

    assert snapshot.schema_version == "m366.2"
    assert tuple(item.layer for item in snapshot.authorities) == tuple(
        EpisodicMemoryLayer
    )


def test_m366_2_preserves_one_canonical_episodic_authority() -> None:
    snapshot = EpisodicMemoryFoundation().snapshot

    assert snapshot.canonical_authority == "episodic_memory"
    assert {item.authority_key for item in snapshot.authorities} == {
        "episodic_memory"
    }


def test_cognitive_cycle_layer_reuses_rp17_implementation() -> None:
    authority = EpisodicMemoryFoundation().snapshot.authority_for(
        "cognitive_cycle"
    )

    assert authority.implementation_path == (
        "app.cognitive_episodic_memory:CognitiveEpisodicMemory"
    )
    assert authority.admission_mode is EpisodicAdmissionMode.OBSERVED_TRANSITION
    assert authority.runtime_connected is True
    assert authority.persistent is False


def test_governed_aggregate_reuses_m85_implementation() -> None:
    authority = EpisodicMemoryFoundation().snapshot.authority_for(
        EpisodicMemoryLayer.GOVERNED_AGGREGATE
    )

    assert authority.implementation_path == (
        "core.adaptive_cognition.episodic_memory:EpisodicMemoryManager"
    )
    assert authority.admission_mode is EpisodicAdmissionMode.EXPLICIT_CAPTURE
    assert authority.runtime_connected is False


def test_m366_2_adds_no_persistence_capture_or_runtime_behavior() -> None:
    snapshot = EpisodicMemoryFoundation().snapshot

    assert snapshot.persistence_added is False
    assert snapshot.automatic_capture_added is False
    assert snapshot.runtime_behavior_changed is False
    assert all(item.automatic_consolidation is False for item in snapshot.authorities)


def test_authority_rejects_automatic_consolidation() -> None:
    with pytest.raises(ValueError, match="cannot enable automatic"):
        EpisodicMemoryAuthority(
            layer=EpisodicMemoryLayer.COGNITIVE_CYCLE,
            authority_key="episodic_memory",
            implementation_path="module:Symbol",
            purpose="test",
            admission_mode=EpisodicAdmissionMode.OBSERVED_TRANSITION,
            persistent=False,
            runtime_connected=True,
            automatic_consolidation=True,
        )


def test_authority_requires_symbol_path() -> None:
    with pytest.raises(ValueError, match="identify a symbol"):
        EpisodicMemoryAuthority(
            layer=EpisodicMemoryLayer.GOVERNED_AGGREGATE,
            authority_key="episodic_memory",
            implementation_path="module.only",
            purpose="test",
            admission_mode=EpisodicAdmissionMode.EXPLICIT_CAPTURE,
            persistent=False,
            runtime_connected=False,
        )


def test_existing_episodic_implementations_remain_unchanged() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "app/cognitive_episodic_memory.py").exists()
    assert (root / "core/adaptive_cognition/episodic_memory.py").exists()


def test_m366_2_documentation_declares_reconciliation_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M366_2_EPISODIC_MEMORY.md").read_text(
        encoding="utf-8"
    )

    assert "CognitiveEpisodicMemory" in document
    assert "EpisodicMemoryManager" in document
    assert "no crea un tercer modelo" in document
    assert "no habilita persistencia nueva" in document


def test_root_documents_register_m366_2() -> None:
    root = Path(__file__).resolve().parents[1]

    assert "M366.2" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M366.2 — Episodic Memory" in (root / "CHANGELOG.md").read_text(
        encoding="utf-8"
    )
    assert "## M366.2 — Episodic Memory" in (
        root / "CHANGELOG_ARCHITECTURE.md"
    ).read_text(encoding="utf-8")
