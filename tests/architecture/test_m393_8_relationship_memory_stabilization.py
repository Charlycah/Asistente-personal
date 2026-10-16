from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.relationship_memory import (
    EnrichedRelationshipMemoryView,
    RelationshipAuditView,
    RelationshipConsistencyView,
    RelationshipConsolidationView,
    RelationshipEvidenceKind,
    RelationshipEvidenceReference,
    RelationshipEvidenceValidation,
    RelationshipEvolutionView,
    RelationshipMemoryManager,
    RelationshipTraceabilityView,
)

ROOT = Path(__file__).resolve().parents[2]


def _manager_with_evidence() -> tuple[
    RelationshipMemoryManager, tuple[RelationshipEvidenceReference, ...]
]:
    manager = RelationshipMemoryManager()
    manager.observe_turn("prefiero mantener el mismo método")
    record = manager.records[0]
    evidence = (
        RelationshipEvidenceReference(
            record_id=record.record_id,
            evidence_ref="m393.8-explicit-evidence",
            kind=RelationshipEvidenceKind.DECLARATION,
            source_authority="relationship_memory",
            epistemic_level="fact",
            validation=RelationshipEvidenceValidation.VERIFIED,
        ),
    )
    return manager, evidence


def test_m393_8_preserves_single_relationship_authority_end_to_end() -> None:
    manager, evidence = _manager_with_evidence()
    consistency = manager.consistency_view(evidence)
    evolution = manager.evolution_view(consistency, consistency)
    traceability = manager.traceability_view(consistency, evolution)
    audit = manager.audit_view(traceability)

    views = (
        manager.enriched_view(evidence),
        manager.consolidation_view(evidence),
        consistency,
        evolution,
        traceability,
        audit,
    )
    assert all(view.authority_id == "relationship_memory" for view in views)


def test_m393_8_stabilized_pipeline_is_deterministic() -> None:
    manager, evidence = _manager_with_evidence()

    first = manager.consistency_view(evidence)
    second = manager.consistency_view(evidence)
    first_evolution = manager.evolution_view(first, second)
    second_evolution = manager.evolution_view(first, second)

    assert first == second
    assert first_evolution == second_evolution
    first_trace = manager.traceability_view(second, first_evolution)
    second_trace = manager.traceability_view(second, second_evolution)
    assert first_trace == second_trace


def test_m393_8_diagnostic_views_do_not_mutate_relationship_history() -> None:
    manager, evidence = _manager_with_evidence()
    before = manager.history
    consistency = manager.consistency_view(evidence)
    evolution = manager.evolution_view(consistency, consistency)
    traceability = manager.traceability_view(consistency, evolution)
    manager.audit_view(traceability)

    assert manager.history == before


def test_m393_8_public_views_remain_immutable() -> None:
    manager, evidence = _manager_with_evidence()
    enriched = manager.enriched_view(evidence)
    consolidation = manager.consolidation_view(evidence)
    consistency = manager.consistency_view(evidence)
    evolution = manager.evolution_view(consistency, consistency)
    traceability = manager.traceability_view(consistency, evolution)
    audit = manager.audit_view(traceability)

    views: tuple[
        EnrichedRelationshipMemoryView
        | RelationshipConsolidationView
        | RelationshipConsistencyView
        | RelationshipEvolutionView
        | RelationshipTraceabilityView
        | RelationshipAuditView,
        ...,
    ] = (enriched, consolidation, consistency, evolution, traceability, audit)
    for view in views:
        with pytest.raises(FrozenInstanceError):
            view.authority_id = "parallel"  # type: ignore[misc]


def test_m393_8_audit_preserves_explicit_evidence_lineage() -> None:
    manager, evidence = _manager_with_evidence()
    consistency = manager.consistency_view(evidence)
    evolution = manager.evolution_view(consistency, consistency)
    traceability = manager.traceability_view(consistency, evolution)
    audit = manager.audit_view(traceability)

    assert traceability.traced_evidence_refs == ("m393.8-explicit-evidence",)
    assert audit.clear_record_ids == (manager.records[0].record_id,)


def test_m393_8_stabilization_adds_no_new_manager_api() -> None:
    expected = {
        "audit_view",
        "consistency_view",
        "consolidation_view",
        "enriched_view",
        "evolution_view",
        "observe_turn",
        "system_prompt_lines",
        "traceability_view",
    }
    public_methods = {
        name
        for name, value in vars(RelationshipMemoryManager).items()
        if callable(value) and not name.startswith("_")
    }

    assert public_methods == expected


def test_m393_8_canonical_core_contract_remains_present() -> None:
    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")

    assert occurrences >= 1


def test_m393_8_closure_documentation_is_synchronized() -> None:
    document_path = ROOT / "docs" / "M393_8_RELATIONSHIP_MEMORY_STABILIZATION.md"
    document = document_path.read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")

    assert "M393.8" in document
    assert "serie M393" in document
    assert "## Milestone M393.8" in readme
    assert "## M393.8" in changelog
    assert "M393.8" in rules
    assert readme.startswith("## Milestone M393.1")
    assert changelog.startswith("# M347.15 — Estabilización de la serie")
