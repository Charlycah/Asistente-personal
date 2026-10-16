from __future__ import annotations

from app.approved_learning_memory_materialization import ApprovedLearningScope
from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.governed_g6_explicit_human_learning_approval import (
    GovernedExplicitHumanLearningApprovalResponse,
    GovernedG6ExplicitHumanLearningApprovalV1,
)
from app.governed_g7_approved_learning_memory_materialization import (
    GovernedG7ApprovedLearningMemoryMaterializationV1,
)
from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationStatus,
)
from app.governed_relational_abstraction_learning_bridge import (
    GovernedRelationalAbstractionLearningBridge,
)
from app.m369_explicit_human_learning_approval import HumanLearningApprovalOutcome
from app.memory_consolidation import OfficialMemoryGateway
from core.cognitive_memory_recall import (
    CognitiveMemoryRecallItem,
    CognitiveMemoryRecallResult,
)
from core.cognitive_memory_store import CognitiveMemorySearch
from core.governed_reasoning.recalled_knowledge_structural_projection import (
    GovernedRecalledKnowledgeStructuralProjector,
    RecalledKnowledgeStructuralProjectionStatus,
)
from core.governed_reasoning.relational_abstraction import (
    GovernedRelationalAbstractionInducer,
    RelationalAbstractionExample,
    RelationalAbstractionStatus,
)
from core.governed_reasoning.structural_knowledge_transfer import (
    GovernedStructuralKnowledgeTransferMatcher,
    StructuralKnowledgeTransferStatus,
)
from core.governed_reasoning.target_problem_structural_projection import (
    GovernedTargetProblemStructuralProjector,
    TargetProblemStructuralProjectionStatus,
)
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)

SCOPE = "hce:relational-abstraction"


def _abstraction():
    examples = tuple(
        RelationalAbstractionExample(
            example_id=example_id,
            scope_reference=SCOPE,
            relation="required_for",
            outcome="blocked_when_unavailable",
            source_fingerprint=f"fp-{example_id}",
        )
        for example_id in ("factory", "clinic", "archive")
    )
    return GovernedRelationalAbstractionInducer().induce(
        examples=examples,
        counterexamples=(),
        scope_reference=SCOPE,
    )


def _approval_response(evaluation, text="Sí"):
    assert evaluation.policy_candidate is not None
    foundation = GovernedG6ExplicitHumanLearningApprovalV1()
    return GovernedExplicitHumanLearningApprovalResponse(
        approval_request_id="abstraction-approval-1",
        source_evaluation_fingerprint=foundation.source_evaluation_fingerprint(
            evaluation
        ),
        learning_candidate_id=evaluation.source_candidate.candidate_id,
        policy_candidate_id=evaluation.policy_candidate.candidate_id,
        human_response_reference="conversation:abstraction-approval",
        response_text=text,
        approver="Carlos",
        scope=ApprovedLearningScope.PROJECT,
        exact_linkage=True,
    )


def _approved_materialization():
    abstraction = _abstraction()
    assert abstraction.status is RelationalAbstractionStatus.REVIEW_REQUIRED
    evaluation = GovernedRelationalAbstractionLearningBridge().evaluate(abstraction)
    approval_foundation = GovernedG6ExplicitHumanLearningApprovalV1()
    approval = approval_foundation.evaluate(
        evaluation,
        _approval_response(evaluation),
    )
    assert approval.outcome is HumanLearningApprovalOutcome.APPROVED
    evidence = approval.approved_evidence
    assert evidence is not None
    materialization = GovernedG7ApprovedLearningMemoryMaterializationV1()
    eligibility = materialization.build_structural_eligibility(evaluation, evidence)
    assert eligibility is not None
    proposal = materialization.propose(
        evaluation,
        evidence,
        structural_eligibility=eligibility,
    ).proposal
    assert proposal is not None
    return abstraction, evaluation, proposal


def test_abstraction_enters_existing_m369_as_stable_knowledge_review_candidate():
    abstraction = _abstraction()
    evaluation = GovernedRelationalAbstractionLearningBridge().evaluate(abstraction)
    assert (
        evaluation.status
        is GovernedLearningCandidateM369EvaluationStatus.REVIEW_REQUIRED
    )
    assert evaluation.policy_candidate is not None
    assert len(evaluation.policy_candidate.evidence_ids) == 3
    assert evaluation.source_candidate.proposed_value.startswith("Usá esta regla:")
    assert abstraction.creates_learning_candidate is False


def test_contested_abstraction_is_not_admitted_to_learning():
    candidate = GovernedRelationalAbstractionInducer().induce(
        examples=(
            RelationalAbstractionExample(
                "a", SCOPE, "required_for", "blocked_when_unavailable", "a"
            ),
            RelationalAbstractionExample(
                "b", SCOPE, "required_for", "blocked_when_unavailable", "b"
            ),
        ),
        counterexamples=(
            RelationalAbstractionExample(
                "c", SCOPE, "required_for", "remains_available", "c"
            ),
        ),
        scope_reference=SCOPE,
    )
    result = GovernedRelationalAbstractionLearningBridge().evaluate(candidate)
    assert result.status is GovernedLearningCandidateM369EvaluationStatus.NOT_ELIGIBLE
    assert result.policy_candidate is None
    assert result.safe_learning_decision is None


def test_explicit_rejection_never_materializes_abstraction():
    evaluation = GovernedRelationalAbstractionLearningBridge().evaluate(_abstraction())
    approval = GovernedG6ExplicitHumanLearningApprovalV1().evaluate(
        evaluation,
        _approval_response(evaluation, text="No"),
    )
    assert approval.outcome is HumanLearningApprovalOutcome.REJECTED
    assert approval.approved_evidence is None


def test_approved_abstraction_uses_existing_memory_gateway_once(tmp_path):
    _, _, proposal = _approved_materialization()
    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)
    runtime = MemoryRuntimeIntegration(
        MemoryRuntimeConfig(root_path=str(tmp_path / "memory"))
    )
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")
    first = gateway.remember_governed_learning(request)
    second = gateway.remember_governed_learning(request)
    assert first.stored_count == 1
    assert second.stored_count == 0
    assert runtime.count(owner="Carlos") == 1


def test_approved_abstraction_is_recalled_and_reused_on_novel_domain(tmp_path):
    _, _, proposal = _approved_materialization()
    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)
    runtime = MemoryRuntimeIntegration(
        MemoryRuntimeConfig(root_path=str(tmp_path / "memory"))
    )
    OfficialMemoryGateway(runtime, owner="Carlos").remember_governed_learning(request)
    record = runtime.private_store("Carlos").search(CognitiveMemorySearch(limit=10))[0]

    recall = CognitiveMemoryRecallResult(
        should_use_memory=True,
        items=(
            CognitiveMemoryRecallItem(
                memory=record, score=0.95, matched_signals=("stable_knowledge",)
            ),
        ),
        reason="relevant_memory_found",
    )
    source = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=recall, scope_reference=SCOPE
    )
    assert (
        source.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.PROJECTED
    )

    target = GovernedTargetProblemStructuralProjector().project(
        text=(
            "La expedición necesita como único medio el puente norte para "
            "cruzar el río. "
            "El puente norte quedó inutilizable y carece de ruta alternativa."
        ),
        source_reference="conversation:novel-expedition",
        scope_reference=SCOPE,
    )
    assert target.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    transfer = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target,
        known=(source.items[0].grounding,),
        scope_reference=SCOPE,
    )
    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )
