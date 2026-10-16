from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from app.approved_learning_memory_materialization import (
    ApprovedLearningScope,
    GovernedMemoryMaterializationProposal,
)
from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.curiosity_m369_learning_evaluation import CuriosityLearningKind
from core.memory_consolidation_foundation import (
    ConsolidationAssessment,
    ConsolidationDisposition,
    ConsolidationReason,
    ConsolidationTarget,
)

ROOT = Path(__file__).resolve().parents[2]


def _proposal(**changes):
    values = {
        "proposal_id": "approved-learning-memory-proposal-1234567890abcdef",
        "learning_candidate_id": "learning-candidate-1",
        "preference_candidate_id": "preference-candidate-1",
        "subject": "Carlos",
        "value": "ejecutar Ruff antes de pytest",
        "approval_id": "approval-1",
        "approver": "Carlos",
        "approval_scope": ApprovedLearningScope.PROJECT,
        "human_response_reference": "conversation:turn-300",
        "m369_evaluation_fingerprint": "a" * 64,
        "human_approval_fingerprint": "b" * 64,
        "confidence": 0.82,
        "evidence_ids": ("evidence-1", "evidence-2"),
        "consolidation": ConsolidationAssessment(
            candidate_id="approved-learning-preference-candidate-1",
            disposition=ConsolidationDisposition.PROPOSE_LONG_TERM,
            proposed_target=ConsolidationTarget.LONG_TERM,
            reasons=(ConsolidationReason.EXPLICIT_USER_INTENT,),
            requires_human_confirmation=False,
        ),
        "source_fingerprint": "c" * 64,
        "learning_kind": CuriosityLearningKind.PREFERENCE,
    }
    values.update(changes)
    return GovernedMemoryMaterializationProposal(**values)


def test_v1_adapts_proposal_to_inert_official_memory_write_request() -> None:
    proposal = _proposal()
    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)
    assert request.materialization_proposal_id == proposal.proposal_id
    assert request.memory_item.content == proposal.value
    assert request.writer_authority == "memory_gateway"
    assert request.writer_component == "OfficialMemoryGateway"
    assert request.writer_method == "remember_governed_learning"
    assert request.requires_official_memory_gateway is True
    assert request.write_performed is False
    assert request.creates_memory is False


def test_v1_preserves_scope_confidence_and_learning_lineage() -> None:
    proposal = _proposal()
    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)
    metadata = request.memory_item.metadata
    assert metadata["approval_scope"] == "project"
    assert float(metadata["confidence"]) == proposal.confidence
    assert metadata["learning_candidate_id"] == proposal.learning_candidate_id
    assert metadata["preference_candidate_id"] == proposal.preference_candidate_id
    assert metadata["m369_evaluation_fingerprint"] == (
        proposal.m369_evaluation_fingerprint
    )
    assert metadata["human_approval_fingerprint"] == (
        proposal.human_approval_fingerprint
    )
    assert tuple(json.loads(metadata["evidence_ids"])) == proposal.evidence_ids


def test_v1_prepares_deterministic_idempotency_identity() -> None:
    proposal = _proposal()
    foundation = GovernedMemoryWriteAdapterFoundation()
    first = foundation.adapt(proposal)
    second = foundation.adapt(proposal)
    assert first == second
    assert first.idempotency_key.startswith("memory-write-")
    assert first.memory_item.metadata["idempotency_key"] == first.idempotency_key


def test_v1_changed_scope_changes_idempotency_identity() -> None:
    foundation = GovernedMemoryWriteAdapterFoundation()
    project = foundation.adapt(_proposal())
    personal = foundation.adapt(
        _proposal(approval_scope=ApprovedLearningScope.PERSONAL)
    )
    assert project.idempotency_key != personal.idempotency_key


def test_v1_declares_certified_writer_guarantees() -> None:
    request = GovernedMemoryWriteAdapterFoundation().adapt(_proposal())
    assert request.semantic_mapping_supported is True
    assert request.idempotent_write_supported is True
    assert request.memory_item.metadata["semantic_mapping_supported"] == "true"
    assert request.memory_item.metadata["idempotent_write_supported"] == "true"


@pytest.mark.parametrize(
    "scope",
    (ApprovedLearningScope.SESSION, ApprovedLearningScope.UNSPECIFIED),
)
def test_v1_rejects_non_durable_or_ambiguous_scope(scope) -> None:
    with pytest.raises(ValueError, match="explicit durable scope"):
        GovernedMemoryWriteAdapterFoundation().adapt(
            _proposal(approval_scope=scope)
        )


def test_v1_upstream_m366_6_already_forbids_persisted_assessment() -> None:
    with pytest.raises(ValueError, match="cannot persist memory"):
        ConsolidationAssessment(
            candidate_id="already-persisted",
            disposition=ConsolidationDisposition.PROPOSE_LONG_TERM,
            proposed_target=ConsolidationTarget.LONG_TERM,
            reasons=(ConsolidationReason.EXPLICIT_USER_INTENT,),
            requires_human_confirmation=False,
            persistence_performed=True,
        )


def test_v1_requires_learning_evidence_lineage() -> None:
    with pytest.raises(ValueError, match="learning evidence lineage"):
        GovernedMemoryWriteAdapterFoundation().adapt(
            _proposal(evidence_ids=())
        )


def test_v1_does_not_import_or_call_official_memory_gateway() -> None:
    source = (
        ROOT / "app" / "approved_learning_memory_write_adapter.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "app.memory_consolidation" not in imports
    assert "OfficialMemoryGateway(" not in source
    assert ".remember(" not in source
    assert ".store_explicit(" not in source


def test_v1_adds_no_parallel_memory_writer_or_authority() -> None:
    source = (
        ROOT / "app" / "approved_learning_memory_write_adapter.py"
    ).read_text(encoding="utf-8")
    assert "class LearningWriter" not in source
    assert "class CuriosityMemoryWriter" not in source
    assert "class CuriosityMemoryAuthority" not in source
    assert "sqlite3" not in source
