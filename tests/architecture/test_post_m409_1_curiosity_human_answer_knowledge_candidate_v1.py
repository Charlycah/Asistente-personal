from __future__ import annotations

import ast
from pathlib import Path

from core.cognitive_maturity.curiosity_human_answer_evidence import (
    CuriosityHumanAnswerEvidenceFoundation,
    ExplicitHumanAnswerEvidence,
    HumanAnswerKind,
    HumanAnswerOutcome,
)
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)

ROOT = Path(__file__).resolve().parents[2]


def _question_report():
    return GovernedEpistemicCuriosityFoundation().evaluate(
        MultisourceKnowledgeGapEvidence(
            subject="el sensor X",
            source_kind=EpistemicCuriositySourceKind.VISUAL,
            source_reference="visual:item-x",
            known_elements=("Carlos y Cristina usan el sensor X",),
            unknown_element="para qué usan el sensor X",
            evidence_codes=("object_observed",),
            relevance=EpistemicCuriosityRelevance.RELEVANT,
            target_person="Carlos",
        )
    )


def _evidence(report, kind=HumanAnswerKind.ANSWER, **changes):
    question = report.question_candidate
    assert question is not None
    values = {
        "curiosity_report_id": report.report_id,
        "question_id": question.question_id,
        "human_answer_reference": "conversation:turn-202",
        "answer_text": "Lo usamos para medir la humedad.",
        "answer_kind": kind,
        "speaker": "Carlos",
        "evidence_codes": ("explicit_reply", "speaker_attributed"),
        "exact_linkage": True,
    }
    values.update(changes)
    return ExplicitHumanAnswerEvidence(**values)


def test_v1_explicit_answer_produces_pending_knowledge_candidate() -> None:
    report = _question_report()
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        report,
        _evidence(report),
    )
    assert result.outcome is HumanAnswerOutcome.KNOWLEDGE_CANDIDATE
    candidate = result.knowledge_candidate
    assert candidate is not None
    assert candidate.statement == "Lo usamos para medir la humedad."
    assert candidate.speaker == "Carlos"
    assert candidate.epistemic_level is EpistemicLevel.FACT
    assert candidate.requires_admission is True
    assert candidate.modifies_knowledge is False


def test_v1_partial_answer_preserves_unresolved_epistemic_status() -> None:
    report = _question_report()
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        report,
        _evidence(report, HumanAnswerKind.PARTIAL_ANSWER),
    )
    assert result.outcome is HumanAnswerOutcome.PARTIAL_KNOWLEDGE_CANDIDATE
    assert result.knowledge_candidate is not None
    assert result.knowledge_candidate.epistemic_level is EpistemicLevel.UNKNOWN


def test_v1_uncertain_answer_is_not_promoted_to_fact() -> None:
    report = _question_report()
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        report,
        _evidence(
            report,
            HumanAnswerKind.UNCERTAIN_ANSWER,
            answer_text="Creo que sirve para medir humedad, no estoy seguro.",
        ),
    )
    assert result.outcome is HumanAnswerOutcome.UNCERTAIN_KNOWLEDGE_CANDIDATE
    assert result.knowledge_candidate is not None
    assert result.knowledge_candidate.epistemic_level is EpistemicLevel.HYPOTHESIS


def test_v1_correction_requires_later_knowledge_review() -> None:
    report = _question_report()
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        report,
        _evidence(
            report,
            HumanAnswerKind.CORRECTION,
            answer_text="No, no mide temperatura; mide humedad.",
        ),
    )
    assert result.outcome is HumanAnswerOutcome.CORRECTION_CANDIDATE
    assert result.knowledge_candidate is not None
    assert result.knowledge_candidate.epistemic_level is EpistemicLevel.UNKNOWN


def test_v1_not_an_answer_creates_no_candidate() -> None:
    report = _question_report()
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        report,
        _evidence(report, HumanAnswerKind.NOT_AN_ANSWER),
    )
    assert result.outcome is HumanAnswerOutcome.NOT_AN_ANSWER
    assert result.knowledge_candidate is None


def test_v1_missing_exact_linkage_abstains() -> None:
    report = _question_report()
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        report,
        _evidence(report, exact_linkage=False),
    )
    assert result.outcome is HumanAnswerOutcome.ABSTAIN
    assert result.knowledge_candidate is None


def test_v1_wrong_question_identity_abstains() -> None:
    report = _question_report()
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        report,
        _evidence(report, question_id="epistemic-question-other"),
    )
    assert result.outcome is HumanAnswerOutcome.ABSTAIN
    assert result.knowledge_candidate is None


def test_v1_is_deterministic() -> None:
    report = _question_report()
    evidence = _evidence(report)
    foundation = CuriosityHumanAnswerEvidenceFoundation()
    assert foundation.evaluate(report, evidence) == foundation.evaluate(
        report,
        evidence,
    )


def test_v1_remains_read_only_and_does_not_write_domains() -> None:
    report = _question_report()
    result = CuriosityHumanAnswerEvidenceFoundation().evaluate(
        report,
        _evidence(report),
    )
    assert result.read_only is True
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_knowledge is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_v1_imports_no_memory_learning_knowledge_runtime_or_gateway() -> None:
    source = (
        ROOT
        / "core"
        / "cognitive_maturity"
        / "curiosity_human_answer_evidence.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "core.learning_foundation" not in imports
    assert "core.semantic_memory_foundation" not in imports
    assert "app.knowledge_runtime" not in imports
    assert "app.official_conversation_gateway" not in imports
    assert "CuriosityLearningAuthority" not in source
    assert "CuriosityKnowledgeAuthority" not in source
    assert "CanonicalCognitiveCore(" not in source
