from __future__ import annotations

import inspect
from dataclasses import fields
from pathlib import Path

from app.approved_learning_memory_materialization import (
    ApprovedLearningEvidence,
    ApprovedLearningMemoryMaterializationProposalFoundation,
    GovernedMemoryMaterializationProposal,
)
from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.curiosity_m369_learning_evaluation import CuriosityLearningKind

ROOT = Path(__file__).resolve().parents[2]


def _field_names(model) -> set[str]:
    return {field.name for field in fields(model)}


# RED-01 — structural evidence must be typed, not an opaque string only.
def test_red_01_typed_structural_eligibility_evidence_exists() -> None:
    module = __import__(
        "app.approved_learning_memory_materialization",
        fromlist=["StructuralEligibilityEvidence"],
    )
    assert hasattr(module, "StructuralEligibilityEvidence")


# RED-02 — evidence must bind exact learned content.
def test_red_02_structural_evidence_binds_content_fingerprint() -> None:
    module = __import__(
        "app.approved_learning_memory_materialization",
        fromlist=["StructuralEligibilityEvidence"],
    )
    model = getattr(module, "StructuralEligibilityEvidence")
    assert "learned_content_fingerprint" in _field_names(model)


# RED-03 — evidence must bind the originating evaluation/candidate.
def test_red_03_structural_evidence_binds_learning_identity() -> None:
    module = __import__(
        "app.approved_learning_memory_materialization",
        fromlist=["StructuralEligibilityEvidence"],
    )
    model = getattr(module, "StructuralEligibilityEvidence")
    names = _field_names(model)
    assert "evaluation_fingerprint" in names
    assert "learning_candidate_id" in names


# RED-04 — evidence must bind scope.
def test_red_04_structural_evidence_binds_scope() -> None:
    module = __import__(
        "app.approved_learning_memory_materialization",
        fromlist=["StructuralEligibilityEvidence"],
    )
    model = getattr(module, "StructuralEligibilityEvidence")
    assert "scope_reference" in _field_names(model)


# RED-05 — evidence must preserve grounding and compilation lineage.
def test_red_05_structural_evidence_binds_reasoning_lineage() -> None:
    module = __import__(
        "app.approved_learning_memory_materialization",
        fromlist=["StructuralEligibilityEvidence"],
    )
    model = getattr(module, "StructuralEligibilityEvidence")
    names = _field_names(model)
    assert "grounding_fingerprint" in names
    assert "compilation_fingerprint" in names


# RED-06 — evidence must carry a recomputable aggregate fingerprint.
def test_red_06_structural_evidence_has_aggregate_fingerprint() -> None:
    module = __import__(
        "app.approved_learning_memory_materialization",
        fromlist=["StructuralEligibilityEvidence"],
    )
    model = getattr(module, "StructuralEligibilityEvidence")
    assert "source_fingerprint" in _field_names(model)


# RED-07 — approval must carry typed structural evidence, not fingerprint alone.
def test_red_07_approved_evidence_carries_structural_eligibility() -> None:
    assert "structural_eligibility" in _field_names(ApprovedLearningEvidence)


# RED-08 — materialization proposal must preserve typed eligibility evidence.
def test_red_08_materialization_carries_structural_eligibility() -> None:
    assert "structural_eligibility" in _field_names(
        GovernedMemoryMaterializationProposal
    )


# RED-09 — materializer must expose an explicit stable-knowledge eligibility gate.
def test_red_09_materializer_exposes_structural_validation_boundary() -> None:
    methods = dict(
        inspect.getmembers(
            ApprovedLearningMemoryMaterializationProposalFoundation,
            predicate=inspect.isfunction,
        )
    )
    assert "_validate_structural_eligibility" in methods


# RED-10 — adapter must defend against forged stable proposals.
def test_red_10_write_adapter_exposes_structural_validation_boundary() -> None:
    methods = dict(
        inspect.getmembers(
            GovernedMemoryWriteAdapterFoundation,
            predicate=inspect.isfunction,
        )
    )
    assert "_validate_structural_eligibility" in methods


# RED-11 — opaque fingerprint transport alone is no longer sufficient.
def test_red_11_materializer_does_not_treat_opaque_fingerprint_as_contract() -> None:
    source = (
        ROOT / "app" / "approved_learning_memory_materialization.py"
    ).read_text(encoding="utf-8")
    assert (
        "structural_evidence_fingerprint: str = \"\""
        not in source
    )


# RED-12 — eligibility producer must reuse governed reasoning authority.
def test_red_12_existing_reasoning_chain_is_reused_for_eligibility() -> None:
    source = (
        ROOT / "app" / "approved_learning_memory_materialization.py"
    ).read_text(encoding="utf-8")
    assert "GovernedContextualRuleInterpretationProducer" in source
    assert "GovernedBoundedSemanticRoleRelationGrounder" in source
    assert "GovernedContextualRuleGroundingCompiler" in source


# GREEN GUARD-01 — stable knowledge remains the existing learning kind.
def test_guard_01_existing_stable_learning_kind_remains() -> None:
    assert CuriosityLearningKind.STABLE_KNOWLEDGE.value == "stable_knowledge"


# GREEN GUARD-02 — materializer remains read-only and does not become Memory.
def test_guard_02_materializer_does_not_write_memory() -> None:
    source = (
        ROOT / "app" / "approved_learning_memory_materialization.py"
    ).read_text(encoding="utf-8")
    assert "OfficialMemoryGateway(" not in source
    assert ".store_governed_learning(" not in source


# GREEN GUARD-03 — no new structural-learning authority is introduced.
def test_guard_03_no_parallel_structural_learning_authority() -> None:
    prohibited = (
        "structural_learning_manager.py",
        "structural_eligibility_orchestrator.py",
        "stable_knowledge_memory_gateway.py",
    )
    assert all(not (ROOT / "app" / name).exists() for name in prohibited)


# GREEN GUARD-04 — preference path remains represented.
def test_guard_04_preference_learning_kind_remains() -> None:
    assert CuriosityLearningKind.PREFERENCE.value == "preference"
