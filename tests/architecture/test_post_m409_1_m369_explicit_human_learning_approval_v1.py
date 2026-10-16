from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.approved_learning_memory_materialization import ApprovedLearningScope
from app.curiosity_m369_learning_evaluation import (
    CuriosityLearningKind,
    CuriosityM369EvaluationContext,
    CuriosityM369LearningEvaluationFoundation,
)
from app.m369_explicit_human_learning_approval import (
    ExplicitHumanLearningApprovalResponse,
    HumanLearningApprovalOutcome,
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)
from core.cognitive_maturity.curiosity_human_answer_evidence import (
    CuriosityHumanAnswerEvidenceFoundation,
    ExplicitHumanAnswerEvidence,
    HumanAnswerKind,
)
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)
from core.preference_learning import PreferenceEvidence

ROOT = Path(__file__).resolve().parents[2]


def _evaluation():
    curiosity = GovernedEpistemicCuriosityFoundation().evaluate(
        MultisourceKnowledgeGapEvidence(
            subject="orden de validación",
            source_kind=EpistemicCuriositySourceKind.CONVERSATION,
            source_reference="conversation:question",
            known_elements=("Carlos valida el proyecto",),
            unknown_element="qué orden prefiere",
            evidence_codes=("explicit_gap",),
            relevance=EpistemicCuriosityRelevance.RELEVANT,
            target_person="Carlos",
        )
    )
    question = curiosity.question_candidate
    assert question is not None
    answer = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        curiosity,
        ExplicitHumanAnswerEvidence(
            curiosity_report_id=curiosity.report_id,
            question_id=question.question_id,
            human_answer_reference="conversation:answer",
            answer_text="Prefiero ejecutar Ruff antes de pytest.",
            answer_kind=HumanAnswerKind.ANSWER,
            speaker="Carlos",
            evidence_codes=("explicit_reply",),
        ),
    )
    candidate = answer.knowledge_candidate
    assert candidate is not None
    prior = (
        PreferenceEvidence(
            candidate_id="prior-candidate-1",
            subject=candidate.subject,
            proposed_value=candidate.statement,
            observation_ids=("prior-observation-1",),
            confidence=0.9,
        ),
        PreferenceEvidence(
            candidate_id="prior-candidate-2",
            subject=candidate.subject,
            proposed_value=candidate.statement,
            observation_ids=("prior-observation-2",),
            confidence=0.9,
        ),
    )
    return CuriosityM369LearningEvaluationFoundation().evaluate(
        candidate,
        CuriosityM369EvaluationContext(
            learning_kind=CuriosityLearningKind.PREFERENCE,
            confidence=0.9,
            age_days=0,
            consent_present=True,
        ),
        prior_preference_evidence=prior,
    )


def _response(evaluation, text="Sí", **changes):
    preference = evaluation.preference_candidate
    assert preference is not None
    values = {
        "approval_request_id": "learning-approval-request-1",
        "evaluation_report_id": evaluation.report_id,
        "learning_candidate_id": evaluation.learning_candidate_id,
        "preference_candidate_id": preference.preference_id,
        "human_response_reference": "conversation:approval-answer",
        "response_text": text,
        "approver": "Carlos",
        "scope": ApprovedLearningScope.PROJECT,
        "exact_linkage": True,
    }
    values.update(changes)
    return ExplicitHumanLearningApprovalResponse(**values)


@pytest.mark.parametrize("text", ("Sí", "si", "de acuerdo", "aprobado"))
def test_v1_explicit_approval_produces_approved_learning_evidence(text) -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, text),
    )
    assert result.outcome is HumanLearningApprovalOutcome.APPROVED
    assert result.approved_evidence is not None
    assert result.approved_evidence.evaluation_report_id == evaluation.report_id
    assert result.approved_evidence.scope is ApprovedLearningScope.PROJECT


@pytest.mark.parametrize("text", ("No", "no lo aprendas", "rechazado"))
def test_v1_explicit_rejection_produces_no_approved_evidence(text) -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, text),
    )
    assert result.outcome is HumanLearningApprovalOutcome.REJECTED
    assert result.approved_evidence is None


@pytest.mark.parametrize("text", ("Después", "más tarde", "después vemos"))
def test_v1_explicit_deferral_produces_no_approved_evidence(text) -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, text),
    )
    assert result.outcome is HumanLearningApprovalOutcome.DEFERRED
    assert result.approved_evidence is None


@pytest.mark.parametrize("text", ("puede ser", "quizás", "creo que sí"))
def test_v1_uncertain_reply_remains_unclear(text) -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, text),
    )
    assert result.outcome is HumanLearningApprovalOutcome.UNCLEAR
    assert result.approved_evidence is None


def test_v1_wrong_evaluation_identity_abstains() -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, evaluation_report_id="wrong-evaluation"),
    )
    assert result.outcome is HumanLearningApprovalOutcome.ABSTAIN


def test_v1_missing_exact_linkage_abstains() -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, exact_linkage=False),
    )
    assert result.outcome is HumanLearningApprovalOutcome.ABSTAIN


def test_v1_unbounded_yes_like_language_does_not_auto_approve() -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, "Sí, supongo que estaría bien por ahora"),
    )
    assert result.outcome is HumanLearningApprovalOutcome.ABSTAIN
    assert result.approved_evidence is None


def test_v1_preserves_explicit_scope_without_inference() -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation, scope=ApprovedLearningScope.CONTEXT),
    )
    assert result.approved_evidence is not None
    assert result.approved_evidence.scope is ApprovedLearningScope.CONTEXT


def test_v1_is_deterministic() -> None:
    evaluation = _evaluation()
    response = _response(evaluation)
    foundation = M369ExplicitHumanLearningApprovalEvidenceFoundation()
    assert foundation.evaluate(evaluation, response) == foundation.evaluate(
        evaluation,
        response,
    )


def test_v1_remains_read_only_and_non_authoritative() -> None:
    evaluation = _evaluation()
    result = M369ExplicitHumanLearningApprovalEvidenceFoundation().evaluate(
        evaluation,
        _response(evaluation),
    )
    assert result.read_only is True
    assert result.persists_results is False
    assert result.writes_learning is False
    assert result.writes_memory is False
    assert result.modifies_knowledge is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_v1_imports_no_gateway_store_or_conversation_runtime() -> None:
    source = (
        ROOT / "app" / "m369_explicit_human_learning_approval.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "app.memory_consolidation" not in imports
    assert "core.cognitive_memory_store" not in imports
    assert "app.official_conversation_gateway" not in imports
    assert ".remember_governed_learning(" not in source
    assert ".store_governed_learning(" not in source
