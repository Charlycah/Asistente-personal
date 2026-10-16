from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityOutcome,
    EpistemicCuriosityQuestionKind,
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)

ROOT = Path(__file__).resolve().parents[2]
FOUNDATION = GovernedEpistemicCuriosityFoundation()


def _evidence(**overrides):
    values = {
        "subject": "objeto observado",
        "source_kind": EpistemicCuriositySourceKind.VISUAL,
        "source_reference": "visual:frame-17:object-x",
        "known_elements": ("objeto presente en contexto doméstico",),
        "unknown_element": "para qué lo usan ustedes",
        "evidence_codes": ("object_observed", "household_function_unknown"),
        "relevance": EpistemicCuriosityRelevance.RELEVANT,
        "target_person": "Carlos",
    }
    values.update(overrides)
    return MultisourceKnowledgeGapEvidence(**values)


@pytest.mark.parametrize(
    "source_kind",
    tuple(EpistemicCuriositySourceKind),
)
def test_v1_accepts_multisource_structured_evidence(source_kind) -> None:
    report = FOUNDATION.evaluate(_evidence(source_kind=source_kind))
    assert report.outcome is EpistemicCuriosityOutcome.QUESTION_CANDIDATE
    assert report.source_kind is source_kind
    assert report.multisource is True


def test_v1_visual_example_can_ask_about_household_specific_function() -> None:
    candidate = FOUNDATION.evaluate(_evidence()).question_candidate
    assert candidate is not None
    assert candidate.question_kind is EpistemicCuriosityQuestionKind.LEARNING
    assert candidate.question.startswith("Carlos, ")
    assert "para qué lo usan ustedes" in candidate.question


def test_v1_conversation_example_can_ask_about_something_heard_from_users() -> None:
    evidence = _evidence(
        subject="la expresión 'lo de siempre'",
        source_kind=EpistemicCuriositySourceKind.CONVERSATION,
        source_reference="conversation:turn-88",
        known_elements=("la expresión fue dicha explícitamente",),
        unknown_element="qué significa 'lo de siempre' en este contexto",
        evidence_codes=("explicit_phrase_observed",),
        target_person="Cristina",
    )
    candidate = FOUNDATION.evaluate(evidence).question_candidate
    assert candidate is not None
    assert candidate.target_person == "Cristina"
    assert "qué significa 'lo de siempre'" in candidate.question


def test_v1_audio_source_does_not_gain_curiosity_authority() -> None:
    report = FOUNDATION.evaluate(
        _evidence(
            source_kind=EpistemicCuriositySourceKind.AUDIO,
            source_reference="audio:observation-4",
        )
    )
    candidate = report.question_candidate
    assert candidate is not None
    assert candidate.source_kind is EpistemicCuriositySourceKind.AUDIO
    assert candidate.grants_authority is False


def test_v1_no_explicit_gap_emits_no_question() -> None:
    report = FOUNDATION.evaluate(_evidence(unknown_element=None))
    assert report.outcome is EpistemicCuriosityOutcome.NO_GAP
    assert report.question_candidate is None


def test_v1_explicitly_irrelevant_gap_does_not_bother_user() -> None:
    report = FOUNDATION.evaluate(
        _evidence(relevance=EpistemicCuriosityRelevance.NOT_RELEVANT)
    )
    assert report.outcome is EpistemicCuriosityOutcome.GAP_NOT_RELEVANT
    assert report.question_candidate is None


def test_v1_unknown_relevance_fails_closed() -> None:
    report = FOUNDATION.evaluate(
        _evidence(relevance=EpistemicCuriosityRelevance.UNKNOWN)
    )
    assert report.outcome is EpistemicCuriosityOutcome.ABSTAIN
    assert report.rationale_codes == ("relevance_not_yet_governed",)


def test_v1_prior_question_reference_suppresses_repeat() -> None:
    report = FOUNDATION.evaluate(
        _evidence(prior_question_reference="conversation:question-previous")
    )
    assert report.outcome is EpistemicCuriosityOutcome.ABSTAIN
    assert report.rationale_codes == ("repeat_question_suppressed",)


def test_v1_hypothesis_check_remains_explicit() -> None:
    report = FOUNDATION.evaluate(
        _evidence(
            hypothesis="el objeto podría formar parte de una rutina",
            unknown_element="si realmente forma parte de una rutina",
        )
    )
    candidate = report.question_candidate
    assert candidate is not None
    assert candidate.question_kind is EpistemicCuriosityQuestionKind.HYPOTHESIS_CHECK
    assert "hipótesis" in candidate.question


def test_v1_missing_known_elements_produces_clarification_not_invention() -> None:
    report = FOUNDATION.evaluate(
        _evidence(
            known_elements=(),
            unknown_element="qué significa esta referencia",
        )
    )
    candidate = report.question_candidate
    assert candidate is not None
    assert candidate.question_kind is EpistemicCuriosityQuestionKind.CLARIFICATION


def test_v1_is_deterministic() -> None:
    evidence = _evidence()
    assert FOUNDATION.evaluate(evidence) == FOUNDATION.evaluate(evidence)


def test_v1_is_read_only_non_persistent_and_non_operational() -> None:
    report = FOUNDATION.evaluate(_evidence())
    candidate = report.question_candidate
    assert candidate is not None
    assert report.read_only is True
    assert report.persists_results is False
    assert report.creates_memory is False
    assert report.creates_learning_candidate is False
    assert report.modifies_knowledge is False
    assert report.starts_background_process is False
    assert report.executes_actions is False
    assert report.grants_authority is False
    assert candidate.read_only is True
    assert candidate.persists_results is False
    assert candidate.creates_memory is False
    assert candidate.creates_learning_candidate is False
    assert candidate.executes_actions is False
    assert candidate.grants_authority is False


def test_v1_requires_explicit_provenance() -> None:
    with pytest.raises(ValueError, match="source provenance"):
        _evidence(source_reference="")


def test_v1_module_creates_no_parallel_authority_or_runtime_dependency() -> None:
    path = Path(inspect.getfile(GovernedEpistemicCuriosityFoundation))
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert imports.isdisjoint(
        {
            "app.official_conversation_gateway",
            "app.relevance_evaluator",
            "app.governed_initiative_engine",
            "domain.governed_cognitive_judgment",
            "core.llm_provider",
            "core.semantic_memory_foundation",
            "core.learning_foundation",
        }
    )
    assert "class CuriosityAuthority" not in source
    assert "CanonicalCognitiveCore(" not in source
    assert "requests." not in source
    assert "socket." not in source
    assert "subprocess." not in source


def test_v1_does_not_modify_canonical_gateway() -> None:
    gateway = ROOT / "app" / "official_conversation_gateway.py"
    source = gateway.read_text(encoding="utf-8")
    assert "GovernedEpistemicCuriosityFoundation" not in source
    tree = ast.parse(source)
    constructors = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert constructors == [52]
