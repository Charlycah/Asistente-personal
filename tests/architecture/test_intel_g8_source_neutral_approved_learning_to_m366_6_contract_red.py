from __future__ import annotations

import ast
import importlib
from dataclasses import replace
from pathlib import Path

import pytest

from app.approved_learning_memory_materialization import (
    ApprovedLearningScope,
    GovernedMemoryMaterializationProposal,
    LearningMemoryMaterializationOutcome,
    StructuralEligibilityEvidence,
)
from app.governed_g6_explicit_human_learning_approval import (
    GovernedExplicitHumanLearningApprovalResponse,
    GovernedG6ExplicitHumanLearningApprovalV1,
)
from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationStatus,
    GovernedLearningCandidateM369EvaluationV1,
)
from app.learning_foundation import LearningFoundation
from core.cognitive_memory import LearningCategory
from core.learning_foundation import LearningObservation

MODULE = "app.governed_g7_approved_learning_memory_materialization"
ROOT = Path(__file__).resolve().parents[2]

_STRUCTURAL_RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)


def _api():
    module = importlib.import_module(MODULE)
    return module.GovernedG7ApprovedLearningMemoryMaterializationV1


def _candidate(suffix: str, *, confidence: float):
    observation = LearningObservation(
        observation_id=f"intel-g8-investigation-observation-{suffix}",
        statement=_STRUCTURAL_RULE,
        source="governed_investigation_evidence",
        source_reference=f"level2-read-only-execution-intel-g8-{suffix}",
        confidence=confidence,
    )
    return LearningFoundation().structure_candidate(
        subject="temperatura del entorno observado",
        proposed_value=_STRUCTURAL_RULE,
        observations=(observation,),
        confidence=confidence,
    )


def _approved_pair(*, scope: ApprovedLearningScope = ApprovedLearningScope.GENERAL):
    evaluation = GovernedLearningCandidateM369EvaluationV1().evaluate(
        _candidate("a", confidence=0.90),
        corroborating_candidates=(_candidate("b", confidence=0.80),),
        age_days=0,
    )
    assert (
        evaluation.status
        is GovernedLearningCandidateM369EvaluationStatus.REVIEW_REQUIRED
    )
    assert evaluation.policy_candidate is not None

    approval_foundation = GovernedG6ExplicitHumanLearningApprovalV1()
    response = GovernedExplicitHumanLearningApprovalResponse(
        approval_request_id="intel-g8-human-approval-request-1",
        source_evaluation_fingerprint=(
            approval_foundation.source_evaluation_fingerprint(evaluation)
        ),
        learning_candidate_id=evaluation.source_candidate.candidate_id,
        policy_candidate_id=evaluation.policy_candidate.candidate_id,
        human_response_reference="conversation:intel-g8-explicit-approval",
        response_text="Sí",
        approver="Carlos",
        scope=scope,
        exact_linkage=True,
    )
    result = approval_foundation.evaluate(evaluation, response)
    assert result.approved_evidence is not None
    return evaluation, result.approved_evidence


def test_intel_g8_approved_learning_reuses_reasoning_and_m366_6_proposal() -> None:
    foundation_type = _api()
    evaluation, approval = _approved_pair()
    foundation = foundation_type()

    structural = foundation.build_structural_eligibility(evaluation, approval)

    assert isinstance(structural, StructuralEligibilityEvidence)
    assert structural.canonical_authority == "governed_reasoning"
    assert structural.learning_candidate_id == approval.learning_candidate_id
    assert structural.evaluation_fingerprint == approval.source_evaluation_fingerprint
    assert structural.scope_reference == approval.scope.value

    report = foundation.propose(
        evaluation,
        approval,
        structural_eligibility=structural,
    )

    assert report.outcome is LearningMemoryMaterializationOutcome.PROPOSAL_READY
    assert isinstance(report.proposal, GovernedMemoryMaterializationProposal)
    proposal = report.proposal
    assert proposal.learning_category is LearningCategory.STABLE_KNOWLEDGE
    assert proposal.learning_candidate_id == approval.learning_candidate_id
    assert proposal.policy_candidate_id == approval.policy_candidate_id
    assert proposal.preference_candidate_id == ""
    assert proposal.subject == evaluation.source_candidate.subject
    assert proposal.value == evaluation.source_candidate.proposed_value
    assert proposal.confidence == evaluation.policy_candidate.confidence
    assert proposal.evidence_ids == evaluation.policy_candidate.evidence_ids
    assert (
        proposal.m369_evaluation_fingerprint
        == approval.source_evaluation_fingerprint
    )
    assert proposal.human_approval_fingerprint == approval.source_fingerprint
    assert proposal.consolidation.persistence_performed is False
    assert report.persistence_performed is False
    assert report.official_memory_gateway_called is False


def test_intel_g8_exact_g6_g7_linkage_is_required_before_materialization() -> None:
    foundation_type = _api()
    evaluation, approval = _approved_pair()
    foundation = foundation_type()
    wrong = replace(approval, learning_candidate_id="wrong-learning-candidate")

    with pytest.raises(ValueError, match="linkage"):
        foundation.build_structural_eligibility(evaluation, wrong)


def test_intel_g8_stable_knowledge_requires_structural_eligibility() -> None:
    foundation_type = _api()
    evaluation, approval = _approved_pair()

    report = foundation_type().propose(
        evaluation,
        approval,
        structural_eligibility=None,
    )

    assert report.outcome is LearningMemoryMaterializationOutcome.REVIEW_REQUIRED
    assert report.proposal is None
    assert "structural_eligibility_required" in report.rationale_codes
    assert report.persistence_performed is False
    assert report.official_memory_gateway_called is False


def test_intel_g8_non_durable_scope_never_produces_durable_proposal() -> None:
    foundation_type = _api()
    evaluation, approval = _approved_pair(scope=ApprovedLearningScope.SESSION)
    foundation = foundation_type()
    structural = foundation.build_structural_eligibility(evaluation, approval)

    report = foundation.propose(
        evaluation,
        approval,
        structural_eligibility=structural,
    )

    assert report.outcome is LearningMemoryMaterializationOutcome.REVIEW_REQUIRED
    assert report.proposal is None
    assert "durable_scope_required" in report.rationale_codes
    assert report.persistence_performed is False
    assert report.official_memory_gateway_called is False


def test_intel_g8_adds_no_curiosity_preference_writer_or_parallel_authority() -> None:
    _api()
    source_path = ROOT / "app/governed_g7_approved_learning_memory_materialization.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_symbols = {
        "CuriosityM369LearningEvaluationReport",
        "CuriosityM369LearningEvaluationFoundation",
        "CuriosityKnowledgeCandidate",
        "CuriosityLearningKind",
        "PreferenceCandidate",
        "GovernedMemoryWriteRequest",
        "GovernedMemoryWriteAdapterFoundation",
        "OfficialMemoryGateway",
        "ProductiveGovernedLearningWiring",
        "LearningManager",
        "KnowledgeManager",
        "MemoryManager",
        "MaterializationManager",
        "OfficialRuntimeCapabilityRegistry",
    }
    identifiers = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not (forbidden_symbols & identifiers)
    assert not (forbidden_symbols & imported)
    assert "ApprovedLearningMemoryMaterializationProposalFoundation" in source
    assert "GovernedMemoryMaterializationProposal" in source
    assert "StructuralEligibilityEvidence" in source
    assert "LearningCategory" in source
    assert all(
        not (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name
            in {
                "persist",
                "write",
                "remember",
                "execute",
                "research",
                "learn",
            }
        )
        for node in ast.walk(tree)
    )
