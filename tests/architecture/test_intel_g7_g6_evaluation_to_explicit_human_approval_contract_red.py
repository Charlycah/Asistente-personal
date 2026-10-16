from __future__ import annotations

import ast
import importlib
from pathlib import Path

from app.approved_learning_memory_materialization import ApprovedLearningScope
from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationStatus,
    GovernedLearningCandidateM369EvaluationV1,
)
from app.learning_foundation import LearningFoundation
from app.m369_explicit_human_learning_approval import HumanLearningApprovalOutcome
from core.learning_foundation import LearningObservation
from core.safe_learning_policies import SafeLearningDisposition

MODULE = "app.governed_g6_explicit_human_learning_approval"
ROOT = Path(__file__).resolve().parents[2]


def _api():
    module = importlib.import_module(MODULE)
    return (
        module.GovernedExplicitHumanLearningApprovalResponse,
        module.GovernedApprovedLearningEvidence,
        module.GovernedG6HumanLearningApprovalResult,
        module.GovernedG6ExplicitHumanLearningApprovalV1,
    )


def _candidate(suffix: str, *, confidence: float = 0.90):
    observation = LearningObservation(
        observation_id=f"intel-g7-investigation-observation-{suffix}",
        statement="la lectura gobernada fue 42.0",
        source="governed_investigation_evidence",
        source_reference=f"level2-read-only-execution-intel-g7-{suffix}",
        confidence=confidence,
    )
    return LearningFoundation().structure_candidate(
        subject="temperatura del entorno observado",
        proposed_value="la lectura gobernada fue 42.0",
        observations=(observation,),
        confidence=confidence,
    )


def _review_required_evaluation():
    return GovernedLearningCandidateM369EvaluationV1().evaluate(
        _candidate("a", confidence=0.90),
        corroborating_candidates=(_candidate("b", confidence=0.80),),
        age_days=0,
    )


def _insufficient_evaluation():
    return GovernedLearningCandidateM369EvaluationV1().evaluate(
        _candidate("single"),
        age_days=0,
    )


def _response(response_type, foundation, evaluation, text="Sí", **overrides):
    assert evaluation.policy_candidate is not None
    values = {
        "approval_request_id": "intel-g7-human-approval-request-1",
        "source_evaluation_fingerprint": foundation.source_evaluation_fingerprint(
            evaluation
        ),
        "learning_candidate_id": evaluation.source_candidate.candidate_id,
        "policy_candidate_id": evaluation.policy_candidate.candidate_id,
        "human_response_reference": "conversation:intel-g7-explicit-approval",
        "response_text": text,
        "approver": "Carlos",
        "scope": ApprovedLearningScope.GENERAL,
        "exact_linkage": True,
    }
    values.update(overrides)
    return response_type(**values)


def test_intel_g7_exact_linked_review_required_can_be_explicitly_approved() -> None:
    response_type, evidence_type, result_type, foundation_type = _api()
    evaluation = _review_required_evaluation()
    foundation = foundation_type()

    assert (
        evaluation.status
        is GovernedLearningCandidateM369EvaluationStatus.REVIEW_REQUIRED
    )
    assert evaluation.safe_learning_decision is not None
    assert (
        evaluation.safe_learning_decision.disposition
        is SafeLearningDisposition.REVIEW_REQUIRED
    )
    assert evaluation.safe_learning_decision.review_authorized is True
    assert evaluation.safe_learning_decision.acceptance_authorized is False
    assert evaluation.safe_learning_decision.persistence_authorized is False
    assert evaluation.safe_learning_decision.adaptation_authorized is False

    response = _response(response_type, foundation, evaluation)
    result = foundation.evaluate(evaluation, response)

    assert isinstance(result, result_type)
    assert result.outcome is HumanLearningApprovalOutcome.APPROVED
    assert isinstance(result.approved_evidence, evidence_type)
    assert (
        result.approved_evidence.learning_candidate_id
        == evaluation.source_candidate.candidate_id
    )
    assert (
        result.approved_evidence.policy_candidate_id
        == evaluation.policy_candidate.candidate_id
    )
    assert (
        result.approved_evidence.source_evaluation_fingerprint
        == response.source_evaluation_fingerprint
    )
    assert (
        result.approved_evidence.human_response_reference
        == response.human_response_reference
    )
    assert result.approved_evidence.scope is ApprovedLearningScope.GENERAL
    assert result.read_only is True
    assert result.persists_results is False
    assert result.writes_memory is False
    assert result.writes_knowledge is False
    assert result.materializes_learning is False


def test_intel_g7_wrong_linkage_abstains_before_human_approval_semantics() -> None:
    response_type, _, _, foundation_type = _api()
    evaluation = _review_required_evaluation()
    foundation = foundation_type()
    response = _response(
        response_type,
        foundation,
        evaluation,
        policy_candidate_id="wrong-policy-candidate",
    )

    result = foundation.evaluate(evaluation, response)

    assert result.outcome is HumanLearningApprovalOutcome.ABSTAIN
    assert result.approved_evidence is None
    assert "exact_g6_learning_approval_linkage_required" in result.rationale_codes


def test_intel_g7_non_review_g6_state_cannot_be_human_overridden() -> None:
    response_type, _, _, foundation_type = _api()
    evaluation = _insufficient_evaluation()
    foundation = foundation_type()
    response = _response(response_type, foundation, evaluation, text="Sí")

    assert (
        evaluation.status
        is GovernedLearningCandidateM369EvaluationStatus.INSUFFICIENT_EVIDENCE
    )
    assert evaluation.safe_learning_decision is not None
    assert evaluation.safe_learning_decision.review_authorized is False

    result = foundation.evaluate(evaluation, response)

    assert result.outcome is HumanLearningApprovalOutcome.ABSTAIN
    assert result.approved_evidence is None
    assert "g6_review_required_source_required" in result.rationale_codes


def test_intel_g7_preserves_existing_explicit_human_response_semantics() -> None:
    response_type, _, _, foundation_type = _api()
    evaluation = _review_required_evaluation()
    foundation = foundation_type()

    expected = (
        ("No", HumanLearningApprovalOutcome.REJECTED),
        ("Más tarde", HumanLearningApprovalOutcome.DEFERRED),
        ("Quizás", HumanLearningApprovalOutcome.UNCLEAR),
        (
            "Sí, supongo que estaría bien por ahora",
            HumanLearningApprovalOutcome.ABSTAIN,
        ),
    )
    for text, outcome in expected:
        result = foundation.evaluate(
            evaluation,
            _response(response_type, foundation, evaluation, text=text),
        )
        assert result.outcome is outcome
        assert result.approved_evidence is None


def test_intel_g7_adds_no_curiosity_preference_memory_or_parallel_authority() -> None:
    _api()
    source_path = ROOT / "app/governed_g6_explicit_human_learning_approval.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_symbols = (
        "CuriosityM369LearningEvaluationReport",
        "CuriosityM369LearningEvaluationFoundation",
        "CuriosityKnowledgeCandidate",
        "PreferenceCandidate",
        "preference_candidate_id",
        "ApprovedLearningEvidence",
        "ApprovedLearningMemoryMaterializationProposalFoundation",
        "GovernedMemoryMaterializationProposal",
        "GovernedMemoryWriteRequest",
        "OfficialMemoryGateway",
        "ProductiveGovernedLearningWiring",
        "LearningManager",
        "ApprovalManager",
        "KnowledgeManager",
        "MemoryManager",
        "OfficialRuntimeCapabilityRegistry",
    )
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
    forbidden_exact = set(forbidden_symbols)
    assert not (forbidden_exact & identifiers)
    assert not (forbidden_exact & imported)
    assert "M369ExplicitHumanLearningApprovalEvidenceFoundation" in source
    assert all(
        not (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name
            in {
                "persist",
                "write",
                "materialize",
                "plan",
                "execute",
                "research",
                "learn",
            }
        )
        for node in ast.walk(tree)
    )
