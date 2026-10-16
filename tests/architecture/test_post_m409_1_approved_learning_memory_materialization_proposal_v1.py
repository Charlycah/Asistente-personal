from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.approved_learning_memory_materialization import (
    ApprovedLearningEvidence,
    ApprovedLearningMemoryMaterializationProposalFoundation,
    ApprovedLearningScope,
    LearningMemoryMaterializationOutcome,
)
from app.curiosity_m369_learning_evaluation import (
    CuriosityLearningKind,
    CuriosityM369EvaluationContext,
    CuriosityM369LearningEvaluationFoundation,
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


def _knowledge_candidate():
    report = GovernedEpistemicCuriosityFoundation().evaluate(
        MultisourceKnowledgeGapEvidence(
            subject="Carlos",
            source_kind=EpistemicCuriositySourceKind.CONVERSATION,
            source_reference="conversation:turn-301",
            known_elements=("Carlos indicó una forma de trabajo",),
            unknown_element="si prefiere Ruff antes de pytest",
            evidence_codes=("explicit_preference_question",),
            relevance=EpistemicCuriosityRelevance.RELEVANT,
            target_person="Carlos",
        )
    )
    question = report.question_candidate
    assert question is not None
    answer = ExplicitHumanAnswerEvidence(
        curiosity_report_id=report.report_id,
        question_id=question.question_id,
        human_answer_reference="conversation:turn-302",
        answer_text="Prefiero ejecutar Ruff antes de pytest.",
        answer_kind=HumanAnswerKind.ANSWER,
        speaker="Carlos",
        evidence_codes=("explicit_reply", "preference_statement"),
    )
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(report, answer)
    assert result.knowledge_candidate is not None
    return result.knowledge_candidate


def _review_required_evaluation():
    candidate = _knowledge_candidate()
    prior = (
        PreferenceEvidence(
            candidate_id="prior-pref-1",
            subject="Carlos",
            proposed_value=candidate.statement,
            observation_ids=("prior-observation-1",),
            confidence=0.9,
        ),
    )
    evaluation = CuriosityM369LearningEvaluationFoundation().evaluate(
        candidate,
        CuriosityM369EvaluationContext(
            learning_kind=CuriosityLearningKind.PREFERENCE,
            confidence=0.9,
            age_days=0,
            consent_present=True,
        ),
        prior_preference_evidence=prior,
    )
    assert evaluation.preference_candidate is not None
    assert evaluation.learning_candidate_id is not None
    return evaluation


def _approval(evaluation, scope=ApprovedLearningScope.PERSONAL):
    preference = evaluation.preference_candidate
    assert preference is not None
    return ApprovedLearningEvidence(
        approval_id="learning-approval-1",
        evaluation_report_id=evaluation.report_id,
        learning_candidate_id=evaluation.learning_candidate_id,
        preference_candidate_id=preference.preference_id,
        human_response_reference="conversation:turn-303",
        approver="Carlos",
        scope=scope,
        source_fingerprint="approval-fingerprint-1",
    )


@pytest.mark.parametrize(
    "scope",
    (
        ApprovedLearningScope.PROJECT,
        ApprovedLearningScope.CONTEXT,
        ApprovedLearningScope.PERSONAL,
        ApprovedLearningScope.HOUSEHOLD,
        ApprovedLearningScope.GENERAL,
    ),
)
def test_v1_approved_durable_preference_produces_proposal(scope) -> None:
    evaluation = _review_required_evaluation()
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation,
        _approval(evaluation, scope),
    )
    assert result.outcome is LearningMemoryMaterializationOutcome.PROPOSAL_READY
    proposal = result.proposal
    assert proposal is not None
    assert proposal.approval_scope is scope
    assert proposal.requires_official_memory_gateway is True
    assert proposal.persists_results is False
    assert proposal.writes_memory is False
    assert proposal.consolidation.persistence_performed is False


@pytest.mark.parametrize(
    "scope",
    (ApprovedLearningScope.SESSION, ApprovedLearningScope.UNSPECIFIED),
)
def test_v1_non_durable_or_unspecified_scope_requires_review(scope) -> None:
    evaluation = _review_required_evaluation()
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation,
        _approval(evaluation, scope),
    )
    assert result.outcome is LearningMemoryMaterializationOutcome.REVIEW_REQUIRED
    assert result.proposal is None


def test_v1_rejects_approval_for_different_evaluation() -> None:
    evaluation = _review_required_evaluation()
    approval = _approval(evaluation)
    wrong = ApprovedLearningEvidence(
        approval_id=approval.approval_id,
        evaluation_report_id="curiosity-m369-evaluation-other",
        learning_candidate_id=approval.learning_candidate_id,
        preference_candidate_id=approval.preference_candidate_id,
        human_response_reference=approval.human_response_reference,
        approver=approval.approver,
        scope=approval.scope,
        source_fingerprint=approval.source_fingerprint,
    )
    with pytest.raises(ValueError, match="exactly reference"):
        ApprovedLearningMemoryMaterializationProposalFoundation().propose(
            evaluation,
            wrong,
        )


def test_v1_rejects_non_approved_input_contract() -> None:
    evaluation = _review_required_evaluation()
    preference = evaluation.preference_candidate
    assert preference is not None
    with pytest.raises(ValueError, match="explicitly approved"):
        ApprovedLearningEvidence(
            approval_id="approval-rejected",
            evaluation_report_id=evaluation.report_id,
            learning_candidate_id=evaluation.learning_candidate_id,
            preference_candidate_id=preference.preference_id,
            human_response_reference="conversation:turn-303",
            approver="Carlos",
            scope=ApprovedLearningScope.PERSONAL,
            source_fingerprint="approval-fingerprint-rejected",
            approved=False,
        )


def test_v1_is_deterministic_and_preserves_provenance() -> None:
    evaluation = _review_required_evaluation()
    approval = _approval(evaluation)
    foundation = ApprovedLearningMemoryMaterializationProposalFoundation()
    first = foundation.propose(evaluation, approval)
    second = foundation.propose(evaluation, approval)
    assert first == second
    assert first.proposal is not None
    assert first.proposal.learning_candidate_id == approval.learning_candidate_id
    assert first.proposal.preference_candidate_id == approval.preference_candidate_id
    assert first.proposal.human_response_reference == approval.human_response_reference


def test_v1_does_not_call_official_memory_gateway_or_learning_writer() -> None:
    source = (
        ROOT / "app" / "approved_learning_memory_materialization.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "app.memory_consolidation" not in imports
    assert "core.learning" not in imports
    assert "app.official_conversation_gateway" not in imports
    assert "OfficialMemoryGateway(" not in source
    assert "ExperientialLearningManager(" not in source
    assert ".remember(" not in source
    assert ".store_explicit(" not in source


def test_v1_report_declares_no_persistence_or_writer_call() -> None:
    evaluation = _review_required_evaluation()
    result = ApprovedLearningMemoryMaterializationProposalFoundation().propose(
        evaluation,
        _approval(evaluation),
    )
    assert result.read_only is True
    assert result.persistence_performed is False
    assert result.official_memory_gateway_called is False
