from __future__ import annotations

from dataclasses import replace

from app.approved_learning_memory_materialization import (
    ApprovedLearningMemoryMaterializationProposalFoundation,
)
from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.curiosity_m369_learning_evaluation import CuriosityLearningKind
from app.m369_explicit_human_learning_approval import (
    ApprovedLearningScope,
    ExplicitHumanLearningApprovalResponse,
    HumanLearningApprovalOutcome,
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)
from app.memory_consolidation import OfficialMemoryGateway
from core.cognitive_memory import LearningCategory
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)

from .test_post_m409_1_m369_explicit_human_learning_approval_v1 import _evaluation


def _response(evaluation, *, kind=CuriosityLearningKind.STABLE_KNOWLEDGE, text="Sí"):
    preference = evaluation.preference_candidate
    assert preference is not None
    return ExplicitHumanLearningApprovalResponse(
        approval_request_id="structural-learning-approval-1",
        evaluation_report_id=evaluation.report_id,
        learning_candidate_id=evaluation.learning_candidate_id,
        preference_candidate_id=preference.preference_id,
        human_response_reference="conversation:structural-approval",
        response_text=text,
        approver="Carlos",
        scope=ApprovedLearningScope.PROJECT,
        exact_linkage=True,
        learning_kind=kind,
    )



_STRUCTURAL_RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)


def _with_structural_eligibility(evaluation, evidence):
    preference = evaluation.preference_candidate
    assert preference is not None
    evaluation = replace(
        evaluation,
        preference_candidate=replace(
            preference,
            preferred_value=_STRUCTURAL_RULE,
        ),
    )
    foundation = ApprovedLearningMemoryMaterializationProposalFoundation()
    eligibility = foundation.build_structural_eligibility(evaluation, evidence)
    assert eligibility is not None
    evidence = replace(
        evidence,
        structural_evidence_fingerprint=eligibility.source_fingerprint,
        structural_eligibility=eligibility,
    )
    return evaluation, evidence


def _runtime(tmp_path):
    return MemoryRuntimeIntegration(MemoryRuntimeConfig(root_path=tmp_path / "memory"))


def test_c1_typed_approval_causes_stable_category_and_persistence(tmp_path) -> None:
    evaluation = _evaluation()
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation, _response(evaluation)
    )
    assert approval.outcome is HumanLearningApprovalOutcome.APPROVED
    evidence = approval.approved_evidence
    assert evidence is not None
    assert evidence.learning_kind is CuriosityLearningKind.STABLE_KNOWLEDGE
    evaluation, evidence = _with_structural_eligibility(evaluation, evidence)

    materialization = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    proposal = materialization.proposal
    assert proposal is not None
    assert proposal.learning_category is LearningCategory.STABLE_KNOWLEDGE

    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)
    assert request.learning_category is LearningCategory.STABLE_KNOWLEDGE

    runtime = _runtime(tmp_path)
    result = OfficialMemoryGateway(runtime, owner="Carlos").remember_governed_learning(
        request
    )
    assert result.stored_count == 1
    record = runtime.private_store("Carlos").search(
        __import__(
            "core.cognitive_memory_store", fromlist=["CognitiveMemorySearch"]
        ).CognitiveMemorySearch(limit=10)
    )[0]
    assert record.category is LearningCategory.STABLE_KNOWLEDGE
    assert record.tags[-1] == "stable_knowledge"


def test_c2_kind_ablation_preserves_preference_semantics(tmp_path) -> None:
    evaluation = _evaluation()
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, kind=CuriosityLearningKind.PREFERENCE),
    )
    evidence = approval.approved_evidence
    assert evidence is not None
    proposal = (
        ApprovedLearningMemoryMaterializationProposalFoundation()
        .propose(evaluation, evidence)
        .proposal
    )
    assert proposal is not None
    assert proposal.learning_category is LearningCategory.USER_PREFERENCE

    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)
    runtime = _runtime(tmp_path)
    OfficialMemoryGateway(runtime, owner="Carlos").remember_governed_learning(request)
    record = runtime.private_store("Carlos").search(
        __import__(
            "core.cognitive_memory_store", fromlist=["CognitiveMemorySearch"]
        ).CognitiveMemorySearch(limit=10)
    )[0]
    assert record.category is LearningCategory.USER_PREFERENCE
    assert record.tags[-1] == "preference"


def test_c3_rejection_ablation_prevents_materialization() -> None:
    evaluation = _evaluation()
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation, _response(evaluation, text="No")
    )
    assert approval.outcome is HumanLearningApprovalOutcome.REJECTED
    assert approval.approved_evidence is None


def test_c4_wrong_linkage_abstains_before_materialization() -> None:
    evaluation = _evaluation()
    response = replace(
        _response(evaluation),
        learning_candidate_id="learning-candidate-forged",
    )
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation, response
    )
    assert approval.outcome is HumanLearningApprovalOutcome.ABSTAIN
    assert approval.approved_evidence is None


def test_c5_non_durable_scope_blocks_write_request() -> None:
    evaluation = _evaluation()
    response = replace(_response(evaluation), scope=ApprovedLearningScope.SESSION)
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation, response
    )
    evidence = approval.approved_evidence
    assert evidence is not None
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is None


def test_c6_same_stable_request_is_idempotent(tmp_path) -> None:
    evaluation = _evaluation()
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation, _response(evaluation)
    )
    evidence = approval.approved_evidence
    assert evidence is not None
    evaluation, evidence = _with_structural_eligibility(evaluation, evidence)
    proposal = (
        ApprovedLearningMemoryMaterializationProposalFoundation()
        .propose(evaluation, evidence)
        .proposal
    )
    assert proposal is not None
    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)

    runtime = _runtime(tmp_path)
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")
    first = gateway.remember_governed_learning(request)
    second = gateway.remember_governed_learning(request)
    assert first.stored_count == 1
    assert second.stored_count == 0
    assert runtime.count(owner="Carlos") == 1


def test_c7_structural_fingerprint_propagates_when_present() -> None:
    evaluation = _evaluation()
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation, _response(evaluation)
    )
    evidence = approval.approved_evidence
    assert evidence is not None
    evaluation, evidence = _with_structural_eligibility(evaluation, evidence)
    proposal = (
        ApprovedLearningMemoryMaterializationProposalFoundation()
        .propose(evaluation, evidence)
        .proposal
    )
    assert proposal is not None
    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)
    fingerprint = evidence.structural_eligibility.source_fingerprint
    assert proposal.structural_evidence_fingerprint == fingerprint
    assert request.structural_evidence_fingerprint == fingerprint
    assert request.memory_item.metadata["structural_evidence_fingerprint"] == (
        fingerprint
    )


def test_c8_empty_structural_fingerprint_blocks_stable_persistence() -> None:
    evaluation = _evaluation()
    approval = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation, _response(evaluation)
    )
    evidence = approval.approved_evidence
    assert evidence is not None
    assert evidence.structural_evidence_fingerprint == ""
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation, evidence
    )
    assert result.proposal is None

