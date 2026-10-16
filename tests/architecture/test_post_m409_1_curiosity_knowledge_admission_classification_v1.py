from __future__ import annotations

import ast
from pathlib import Path

from core.cognitive_maturity.curiosity_human_answer_evidence import (
    CuriosityHumanAnswerEvidenceFoundation,
    ExplicitHumanAnswerEvidence,
    HumanAnswerKind,
)
from core.cognitive_maturity.curiosity_knowledge_admission_classification import (
    CuriosityAdmissionContext,
    CuriosityAdmissionTarget,
    CuriosityKnowledgeCandidateAdmissionClassificationFoundation,
)
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)

ROOT = Path(__file__).resolve().parents[2]


def _candidate(kind=HumanAnswerKind.ANSWER):
    report = GovernedEpistemicCuriosityFoundation().evaluate(
        MultisourceKnowledgeGapEvidence(
            subject="el sensor X",
            source_kind=EpistemicCuriositySourceKind.CONVERSATION,
            source_reference="conversation:question-1",
            known_elements=("sensor X existe",),
            unknown_element="para qué lo usan",
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
        human_answer_reference="conversation:answer-1",
        answer_text="Lo usamos para medir la humedad.",
        answer_kind=kind,
        speaker="Carlos",
        evidence_codes=("explicit_reply",),
    )
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(report, answer)
    assert result.knowledge_candidate is not None
    return result.knowledge_candidate


def _classify(candidate, **context):
    return CuriosityKnowledgeCandidateAdmissionClassificationFoundation().classify(
        candidate,
        CuriosityAdmissionContext(**context),
    )


def test_v1_routes_durable_fact_to_knowledge() -> None:
    result = _classify(
        _candidate(),
        durable_generalizable=True,
        contextual_provenance_worth_remembering=False,
    )
    assert result.target is CuriosityAdmissionTarget.KNOWLEDGE


def test_v1_routes_contextual_fact_to_memory() -> None:
    result = _classify(
        _candidate(),
        durable_generalizable=False,
        contextual_provenance_worth_remembering=True,
    )
    assert result.target is CuriosityAdmissionTarget.MEMORY


def test_v1_can_route_fact_to_knowledge_and_memory() -> None:
    result = _classify(
        _candidate(),
        durable_generalizable=True,
        contextual_provenance_worth_remembering=True,
    )
    assert result.target is CuriosityAdmissionTarget.KNOWLEDGE_AND_MEMORY


def test_v1_uncertain_candidate_requires_review() -> None:
    result = _classify(
        _candidate(HumanAnswerKind.UNCERTAIN_ANSWER),
        durable_generalizable=False,
        contextual_provenance_worth_remembering=False,
    )
    assert result.target is CuriosityAdmissionTarget.REVIEW_REQUIRED


def test_v1_correction_requires_review() -> None:
    result = _classify(
        _candidate(HumanAnswerKind.CORRECTION),
        durable_generalizable=False,
        contextual_provenance_worth_remembering=False,
    )
    assert result.target is CuriosityAdmissionTarget.REVIEW_REQUIRED


def test_v1_conflict_requires_review() -> None:
    result = _classify(
        _candidate(),
        durable_generalizable=True,
        contextual_provenance_worth_remembering=False,
        conflicts_with_existing_knowledge=True,
    )
    assert result.target is CuriosityAdmissionTarget.REVIEW_REQUIRED


def test_v1_personal_or_sensitive_does_not_route_to_general_knowledge() -> None:
    result = _classify(
        _candidate(),
        durable_generalizable=False,
        contextual_provenance_worth_remembering=True,
        sensitive_or_personal=True,
    )
    assert result.target is CuriosityAdmissionTarget.MEMORY


def test_v1_rejects_fact_with_no_admission_value() -> None:
    result = _classify(
        _candidate(),
        durable_generalizable=False,
        contextual_provenance_worth_remembering=False,
    )
    assert result.target is CuriosityAdmissionTarget.REJECT


def test_v1_is_deterministic_and_preserves_provenance() -> None:
    candidate = _candidate()
    context = CuriosityAdmissionContext(
        durable_generalizable=True,
        contextual_provenance_worth_remembering=False,
    )
    foundation = CuriosityKnowledgeCandidateAdmissionClassificationFoundation()
    first = foundation.classify(candidate, context)
    second = foundation.classify(candidate, context)
    assert first == second
    assert first.question_id == candidate.question_id
    assert first.human_answer_reference == candidate.human_answer_reference
    assert first.speaker == candidate.speaker


def test_v1_is_read_only_and_does_not_consume_learning_or_writers() -> None:
    result = _classify(
        _candidate(),
        durable_generalizable=True,
        contextual_provenance_worth_remembering=False,
    )
    assert result.read_only is True
    assert result.persists_results is False
    assert result.writes_memory is False
    assert result.writes_knowledge is False
    assert result.creates_learning_candidate is False
    assert result.invokes_learning is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_v1_imports_no_gateway_memory_writer_knowledge_runtime_or_learning() -> None:
    source = (
        ROOT
        / "core"
        / "cognitive_maturity"
        / "curiosity_knowledge_admission_classification.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "app.official_conversation_gateway" not in imports
    assert "app.memory_consolidation" not in imports
    assert "app.knowledge_runtime" not in imports
    assert "core.learning_foundation" not in imports
    assert "CuriosityKnowledgeAuthority" not in source
    assert "CuriosityLearningAuthority" not in source
