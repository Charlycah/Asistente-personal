from __future__ import annotations

from dataclasses import replace
from importlib import import_module

import pytest

from app.approved_learning_memory_materialization import (
    ApprovedLearningMemoryMaterializationProposalFoundation,
)
from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.curiosity_m369_learning_evaluation import CuriosityLearningKind
from app.m369_explicit_human_learning_approval import (
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)

from .test_post_m409_1_m369_explicit_human_learning_approval_v1 import _evaluation

_bridge = import_module(
    ".test_post_m409_1_approved_structural_knowledge_bridge_"
    "causal_certification_v1",
    package=__package__,
)

def _approved_stable():
    evaluation = _evaluation()
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _bridge._response(evaluation, kind=CuriosityLearningKind.STABLE_KNOWLEDGE),
    )
    evidence = approval.approved_evidence
    assert evidence is not None
    return evaluation, evidence


def test_se_c1_valid_existing_reasoning_chain_causes_materialization() -> None:
    evaluation, evidence = _approved_stable()
    evaluation, evidence = _bridge._with_structural_eligibility(
        evaluation, evidence
    )
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is not None
    assert result.proposal.structural_eligibility is not None


def test_se_c2_remove_eligibility_blocks_same_stable_candidate() -> None:
    evaluation, evidence = _approved_stable()
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is None
    assert "structural_eligibility_required" in result.rationale_codes


def test_se_c3_changed_content_invalidates_precomputed_evidence() -> None:
    evaluation, evidence = _approved_stable()
    evaluation, evidence = _bridge._with_structural_eligibility(
        evaluation, evidence
    )
    preference = evaluation.preference_candidate
    assert preference is not None
    changed = replace(
        evaluation,
        preference_candidate=replace(
            preference,
            preferred_value=preference.preferred_value + " alterado",
        ),
    )
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        changed, evidence
    )
    assert result.proposal is None


def test_se_c4_wrong_evaluation_fingerprint_fails_closed() -> None:
    evaluation, evidence = _approved_stable()
    evaluation, evidence = _bridge._with_structural_eligibility(
        evaluation, evidence
    )
    eligibility = evidence.structural_eligibility
    assert eligibility is not None
    forged = object.__new__(type(eligibility))
    for field in eligibility.__dataclass_fields__:
        object.__setattr__(forged, field, getattr(eligibility, field))
    object.__setattr__(forged, "evaluation_fingerprint", "forged-evaluation")
    evidence = replace(evidence, structural_eligibility=forged)
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is None


def test_se_c5_wrong_candidate_identity_fails_closed() -> None:
    evaluation, evidence = _approved_stable()
    evaluation, evidence = _bridge._with_structural_eligibility(
        evaluation, evidence
    )
    eligibility = evidence.structural_eligibility
    assert eligibility is not None
    forged = object.__new__(type(eligibility))
    for field in eligibility.__dataclass_fields__:
        object.__setattr__(forged, field, getattr(eligibility, field))
    object.__setattr__(forged, "learning_candidate_id", "forged-candidate")
    evidence = replace(evidence, structural_eligibility=forged)
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is None


def test_se_c6_wrong_scope_fails_closed() -> None:
    evaluation, evidence = _approved_stable()
    evaluation, evidence = _bridge._with_structural_eligibility(
        evaluation, evidence
    )
    eligibility = evidence.structural_eligibility
    assert eligibility is not None
    forged = object.__new__(type(eligibility))
    for field in eligibility.__dataclass_fields__:
        object.__setattr__(forged, field, getattr(eligibility, field))
    object.__setattr__(forged, "scope_reference", "session")
    evidence = replace(evidence, structural_eligibility=forged)
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is None


def test_se_c7_tampered_aggregate_fingerprint_fails_closed() -> None:
    evaluation, evidence = _approved_stable()
    evaluation, evidence = _bridge._with_structural_eligibility(
        evaluation, evidence
    )
    eligibility = evidence.structural_eligibility
    assert eligibility is not None
    forged = object.__new__(type(eligibility))
    for field in eligibility.__dataclass_fields__:
        object.__setattr__(forged, field, getattr(eligibility, field))
    object.__setattr__(forged, "source_fingerprint", "forged-fingerprint")
    evidence = replace(evidence, structural_eligibility=forged)
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is None


def test_se_c8_unsupported_structure_produces_no_eligibility() -> None:
    evaluation, evidence = _approved_stable()
    foundation = ApprovedLearningMemoryMaterializationProposalFoundation()
    assert foundation.build_structural_eligibility(evaluation, evidence) is None


def test_se_c9_preference_remains_independent_of_structural_eligibility() -> None:
    evaluation = _evaluation()
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _bridge._response(evaluation, kind=CuriosityLearningKind.PREFERENCE),
    )
    evidence = approval.approved_evidence
    assert evidence is not None
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is not None
    assert result.proposal.structural_eligibility is None


def test_se_c10_adapter_rejects_forged_stable_proposal_without_evidence() -> None:
    evaluation, evidence = _approved_stable()
    evaluation, evidence = _bridge._with_structural_eligibility(
        evaluation, evidence
    )
    proposal = (
        ApprovedLearningMemoryMaterializationProposalFoundation()
        .propose(evaluation, evidence)
        .proposal
    )
    assert proposal is not None
    forged = replace(
        proposal,
        structural_eligibility=None,
        structural_evidence_fingerprint="opaque-only",
    )
    with pytest.raises(ValueError, match="structural eligibility"):
        GovernedMemoryWriteAdapterFoundation().adapt(forged)
