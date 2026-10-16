from __future__ import annotations

import ast
from types import SimpleNamespace

from app.personal_initiative_engine import InitiativeContext
from app.personal_interest_center import InterestTopic
from app.relevance_evaluator import RelevanceCandidate
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)


class _Runtime:
    def __init__(self) -> None:
        self.bootstrap = SimpleNamespace(
            config=SimpleNamespace(owner="Carlos y Cristina")
        )
        self.calls = 0

    def converse(self, text, **kwargs):
        self.calls += 1
        return SimpleNamespace(response_text=f"runtime:{text}")


def _report():
    return GovernedEpistemicCuriosityFoundation().evaluate(
        MultisourceKnowledgeGapEvidence(
            subject="una referencia de programación",
            source_kind=EpistemicCuriositySourceKind.CONVERSATION,
            source_reference="conversation:turn-101",
            known_elements=("Carlos habló de programación",),
            unknown_element="qué significa esa referencia en este contexto",
            evidence_codes=("explicit_phrase_observed",),
            relevance=EpistemicCuriosityRelevance.RELEVANT,
            target_person="Carlos",
        )
    )


def _candidate(report, *, topics=frozenset({InterestTopic.PROGRAMMING})):
    question = report.question_candidate
    assert question is not None
    return RelevanceCandidate(
        title=question.question,
        topics=topics,
        importance=10,
        verification="confirmed",
        information_kind="guidance",
    )


def test_v1_productively_realizes_question_without_provider_or_network() -> None:
    from app.personal_initiative_engine import PersonalInitiativeEngine
    from app.personal_interest_center import PersonalInterestCenter
    from app.productive_conversational_curiosity_wiring import (
        ProductiveConversationalCuriosityWiring,
    )
    from app.relevance_evaluator import RelevanceEvaluator

    report = _report()
    relevance = RelevanceEvaluator(PersonalInterestCenter())
    wiring = ProductiveConversationalCuriosityWiring(
        relevance,
        PersonalInitiativeEngine(relevance),
    )
    assembly = wiring.assemble(report, _candidate(report))
    assert assembly is not None
    assert assembly.question == report.question_candidate.question
    assert assembly.read_only is True
    assert assembly.persists_results is False
    assert assembly.executes_actions is False


def test_v1_deferred_curiosity_produces_no_productive_assembly() -> None:
    from app.personal_initiative_engine import PersonalInitiativeEngine
    from app.personal_interest_center import PersonalInterestCenter
    from app.productive_conversational_curiosity_wiring import (
        ProductiveConversationalCuriosityWiring,
    )
    from app.relevance_evaluator import RelevanceEvaluator

    report = _report()
    relevance = RelevanceEvaluator(PersonalInterestCenter())
    wiring = ProductiveConversationalCuriosityWiring(
        relevance,
        PersonalInitiativeEngine(relevance),
    )
    assembly = wiring.assemble(
        report,
        _candidate(report),
        context=InitiativeContext(quiet_hours=True),
    )
    assert assembly is None


def test_v1_discarded_curiosity_produces_no_productive_assembly() -> None:
    from app.personal_initiative_engine import PersonalInitiativeEngine
    from app.personal_interest_center import PersonalInterestCenter
    from app.productive_conversational_curiosity_wiring import (
        ProductiveConversationalCuriosityWiring,
    )
    from app.relevance_evaluator import RelevanceEvaluator

    report = _report()
    relevance = RelevanceEvaluator(PersonalInterestCenter())
    wiring = ProductiveConversationalCuriosityWiring(
        relevance,
        PersonalInitiativeEngine(relevance),
    )
    assert wiring.assemble(
        report,
        _candidate(report, topics=frozenset()),
    ) is None


def test_v1_external_evidence_keeps_existing_precedence() -> None:
    source = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "and not external_evidence" in source


def test_v1_keeps_single_canonical_core_constructor_contract() -> None:
    source = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    constructors = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert constructors == [52]


def test_v1_wiring_adds_no_curiosity_authority() -> None:
    source = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "productive_conversational_curiosity_wiring.py"
    ).read_text(encoding="utf-8")
    assert "class CuriosityAuthority" not in source
    assert "requests." not in source
    assert "socket." not in source
    assert "subprocess." not in source
