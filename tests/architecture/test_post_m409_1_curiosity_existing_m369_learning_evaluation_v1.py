from __future__ import annotations

import ast
from pathlib import Path

from app.curiosity_m369_learning_evaluation import (
    CuriosityLearningKind,
    CuriosityM369EvaluationContext,
    CuriosityM369EvaluationOutcome,
    CuriosityM369LearningEvaluationFoundation,
)
from app.learning_foundation import LearningFoundation
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
from core.learning_foundation import LearningObservation
from core.preference_learning import PreferenceEvidence

ROOT = Path(__file__).resolve().parents[2]


def _candidate(statement: str = "Prefiero que revisemos Ruff antes de pytest."):
    report = GovernedEpistemicCuriosityFoundation().evaluate(
        MultisourceKnowledgeGapEvidence(
            subject="orden de validación",
            source_kind=EpistemicCuriositySourceKind.CONVERSATION,
            source_reference="conversation:question-learning-1",
            known_elements=("Carlos habló del proceso de validación",),
            unknown_element="qué orden prefiere para validar",
            evidence_codes=("explicit_gap",),
            relevance=EpistemicCuriosityRelevance.RELEVANT,
            target_person="Carlos",
        )
    )
    question = report.question_candidate
    assert question is not None
    answer = ExplicitHumanAnswerEvidence(
        curiosity_report_id=report.report_id,
        question_id=question.question_id,
        human_answer_reference="conversation:answer-learning-1",
        answer_text=statement,
        answer_kind=HumanAnswerKind.ANSWER,
        speaker="Carlos",
        evidence_codes=("explicit_reply",),
    )
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(report, answer)
    assert result.knowledge_candidate is not None
    return result.knowledge_candidate


def _context(**changes):
    values = {
        "learning_kind": CuriosityLearningKind.PREFERENCE,
        "confidence": 0.9,
        "age_days": 0,
    }
    values.update(changes)
    return CuriosityM369EvaluationContext(**values)


def _prior_evidence(index: int, statement: str) -> PreferenceEvidence:
    observation = LearningObservation(
        observation_id=f"prior-observation-{index}",
        statement=statement,
        source="explicit_prior_evidence",
        source_reference=f"conversation:prior-{index}",
        confidence=0.9,
    )
    learning = LearningFoundation().structure_candidate(
        subject="orden de validación",
        proposed_value=statement,
        observations=(observation,),
        confidence=0.9,
    )
    return PreferenceEvidence.from_learning_candidate(learning)


def test_v1_explicit_non_learning_candidate_stays_out_of_m369() -> None:
    result = CuriosityM369LearningEvaluationFoundation().evaluate(
        _candidate("El sensor mide humedad."),
        _context(learning_kind=CuriosityLearningKind.NOT_LEARNING_RELEVANT),
    )
    assert result.outcome is CuriosityM369EvaluationOutcome.NOT_LEARNING_RELEVANT
    assert result.learning_candidate_id is None
    assert result.preference_candidate is None
    assert result.safe_learning_decision is None


def test_v1_single_preference_answer_is_insufficient_evidence() -> None:
    result = CuriosityM369LearningEvaluationFoundation().evaluate(
        _candidate(),
        _context(),
    )
    assert result.outcome is CuriosityM369EvaluationOutcome.INSUFFICIENT_EVIDENCE
    assert result.learning_candidate_id is not None
    assert result.preference_candidate is not None
    assert result.preference_candidate.evidence_count == 1
    assert result.safe_learning_decision is not None
    assert result.safe_learning_decision.acceptance_authorized is False


def test_v1_consistent_accumulated_preference_reaches_review_required() -> None:
    statement = "Prefiero que revisemos Ruff antes de pytest."
    result = CuriosityM369LearningEvaluationFoundation().evaluate(
        _candidate(statement),
        _context(),
        prior_preference_evidence=(_prior_evidence(1, statement),),
    )
    assert result.outcome is CuriosityM369EvaluationOutcome.REVIEW_REQUIRED
    assert result.preference_candidate is not None
    assert result.preference_candidate.evidence_count == 2
    assert result.safe_learning_decision is not None
    assert result.safe_learning_decision.review_authorized is True
    assert result.safe_learning_decision.persistence_authorized is False


def test_v1_sensitive_learning_without_consent_is_rejected() -> None:
    statement = "Prefiero que revisemos Ruff antes de pytest."
    result = CuriosityM369LearningEvaluationFoundation().evaluate(
        _candidate(statement),
        _context(sensitive=True, consent_present=False),
        prior_preference_evidence=(_prior_evidence(1, statement),),
    )
    assert result.outcome is CuriosityM369EvaluationOutcome.REJECTED
    assert result.safe_learning_decision is not None
    assert "sensitive_learning_requires_consent" in (
        result.safe_learning_decision.explanation_codes
    )


def test_v1_contradiction_uses_existing_safe_learning_rejection() -> None:
    statement = "Prefiero que revisemos Ruff antes de pytest."
    result = CuriosityM369LearningEvaluationFoundation().evaluate(
        _candidate(statement),
        _context(contradiction_count=1),
        prior_preference_evidence=(_prior_evidence(1, statement),),
    )
    assert result.outcome is CuriosityM369EvaluationOutcome.REJECTED
    assert result.safe_learning_decision is not None
    assert result.safe_learning_decision.explanation_codes == (
        "contradictory_evidence",
    )


def test_v1_stale_learning_uses_existing_expiration_policy() -> None:
    statement = "Prefiero que revisemos Ruff antes de pytest."
    result = CuriosityM369LearningEvaluationFoundation().evaluate(
        _candidate(statement),
        _context(age_days=91),
        prior_preference_evidence=(_prior_evidence(1, statement),),
    )
    assert result.outcome is CuriosityM369EvaluationOutcome.EXPIRED


def test_v1_is_deterministic() -> None:
    candidate = _candidate()
    context = _context()
    foundation = CuriosityM369LearningEvaluationFoundation()
    assert foundation.evaluate(candidate, context) == foundation.evaluate(
        candidate,
        context,
    )


def test_v1_remains_read_only_and_never_accepts_or_persists_learning() -> None:
    result = CuriosityM369LearningEvaluationFoundation().evaluate(
        _candidate(),
        _context(),
    )
    assert result.read_only is True
    assert result.uses_existing_m369 is True
    assert result.persists_results is False
    assert result.accepts_learning is False
    assert result.applies_adaptation is False
    assert result.writes_memory is False
    assert result.writes_knowledge is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_v1_does_not_call_habit_pattern_adaptive_or_legacy_writer() -> None:
    source = (
        ROOT / "app" / "curiosity_m369_learning_evaluation.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "app.habit_detection" not in imports
    assert "app.pattern_recognition" not in imports
    assert "app.adaptive_reasoning" not in imports
    assert "core.learning" not in imports
    assert "ExperientialLearningManager" not in source
    assert "CuriosityLearningAuthority" not in source
    assert "CanonicalCognitiveCore(" not in source
