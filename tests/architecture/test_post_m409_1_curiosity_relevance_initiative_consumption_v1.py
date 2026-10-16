from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from app.governed_epistemic_curiosity_consumption import (
    GovernedEpistemicCuriosityConsumptionFoundation,
)
from app.personal_initiative_engine import (
    InitiativeContext,
    InitiativeDisposition,
    PersonalInitiativeEngine,
)
from app.personal_interest_center import InterestTopic, PersonalInterestCenter
from app.relevance_evaluator import RelevanceCandidate, RelevanceEvaluator
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)

ROOT = Path(__file__).resolve().parents[2]


def _curiosity_report():
    evidence = MultisourceKnowledgeGapEvidence(
        subject="una referencia de programación",
        source_kind=EpistemicCuriositySourceKind.CONVERSATION,
        source_reference="conversation:turn-91",
        known_elements=("Carlos habló de programación",),
        unknown_element="qué significa esa referencia en este contexto",
        evidence_codes=("explicit_phrase_observed",),
        relevance=EpistemicCuriosityRelevance.RELEVANT,
        target_person="Carlos",
    )
    return GovernedEpistemicCuriosityFoundation().evaluate(evidence)


def _services():
    center = PersonalInterestCenter()
    relevance = RelevanceEvaluator(center)
    initiative = PersonalInitiativeEngine(relevance)
    return relevance, initiative


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


def test_v1_consumes_existing_relevance_and_initiative() -> None:
    report = _curiosity_report()
    relevance, initiative = _services()
    result = GovernedEpistemicCuriosityConsumptionFoundation().consume(
        report,
        _candidate(report),
        relevance_evaluator=relevance,
        initiative_engine=initiative,
    )
    assert result.uses_existing_relevance is True
    assert result.uses_existing_initiative is True
    assert result.relevance.should_share is True
    assert result.initiative.disposition is InitiativeDisposition.INITIATE
    assert result.should_ask is True


def test_v1_irrelevant_existing_interest_decision_discards_question() -> None:
    report = _curiosity_report()
    relevance, initiative = _services()
    result = GovernedEpistemicCuriosityConsumptionFoundation().consume(
        report,
        _candidate(report, topics=frozenset()),
        relevance_evaluator=relevance,
        initiative_engine=initiative,
    )
    assert result.relevance.should_share is False
    assert result.initiative.disposition is InitiativeDisposition.DISCARD
    assert result.should_ask is False


@pytest.mark.parametrize(
    ("context", "expected"),
    (
        (InitiativeContext(quiet_hours=True), InitiativeDisposition.DEFER),
        (InitiativeContext(recently_intervened=True), InitiativeDisposition.DEFER),
        (InitiativeContext(conversation_active=True), InitiativeDisposition.DEFER),
    ),
)
def test_v1_existing_initiative_context_can_defer_question(
    context,
    expected,
) -> None:
    report = _curiosity_report()
    relevance, initiative = _services()
    result = GovernedEpistemicCuriosityConsumptionFoundation().consume(
        report,
        _candidate(report),
        relevance_evaluator=relevance,
        initiative_engine=initiative,
        context=context,
    )
    assert result.initiative.disposition is expected
    assert result.should_ask is False


def test_v1_rejects_non_question_curiosity_outcome() -> None:
    evidence = MultisourceKnowledgeGapEvidence(
        subject="known",
        source_kind=EpistemicCuriositySourceKind.MEMORY,
        source_reference="memory:item-1",
        known_elements=("complete",),
        unknown_element=None,
        evidence_codes=("knowledge_complete",),
        relevance=EpistemicCuriosityRelevance.RELEVANT,
    )
    report = GovernedEpistemicCuriosityFoundation().evaluate(evidence)
    relevance, initiative = _services()
    with pytest.raises(ValueError, match="QUESTION_CANDIDATE"):
        GovernedEpistemicCuriosityConsumptionFoundation().consume(
            report,
            RelevanceCandidate(title="unused", topics=frozenset()),
            relevance_evaluator=relevance,
            initiative_engine=initiative,
        )


def test_v1_requires_exact_question_identity_for_relevance_candidate() -> None:
    report = _curiosity_report()
    relevance, initiative = _services()
    with pytest.raises(ValueError, match="exact curiosity question"):
        GovernedEpistemicCuriosityConsumptionFoundation().consume(
            report,
            RelevanceCandidate(
                title="semantic rewrite",
                topics=frozenset({InterestTopic.PROGRAMMING}),
            ),
            relevance_evaluator=relevance,
            initiative_engine=initiative,
        )


def test_v1_is_deterministic_for_same_existing_service_state() -> None:
    report = _curiosity_report()
    relevance, initiative = _services()
    candidate = _candidate(report)
    foundation = GovernedEpistemicCuriosityConsumptionFoundation()
    first = foundation.consume(
        report,
        candidate,
        relevance_evaluator=relevance,
        initiative_engine=initiative,
    )
    second = foundation.consume(
        report,
        candidate,
        relevance_evaluator=relevance,
        initiative_engine=initiative,
    )
    assert first == second


def test_v1_remains_read_only_non_persistent_and_non_operational() -> None:
    report = _curiosity_report()
    relevance, initiative = _services()
    result = GovernedEpistemicCuriosityConsumptionFoundation().consume(
        report,
        _candidate(report),
        relevance_evaluator=relevance,
        initiative_engine=initiative,
    )
    assert result.read_only is True
    assert result.persists_results is False
    assert result.creates_proposal is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_knowledge is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_v1_does_not_wire_gateway_or_governed_proposal_engine() -> None:
    path = Path(inspect.getfile(GovernedEpistemicCuriosityConsumptionFoundation))
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "app.official_conversation_gateway" not in imports
    assert "app.governed_initiative_engine" not in imports
    assert "domain.governed_proposal" not in imports
    assert "domain.governed_proposal_inbox" not in imports
    assert "CuriosityAuthority" not in source
    assert "CanonicalCognitiveCore(" not in source


def test_v1_does_not_modify_canonical_gateway() -> None:
    source = (ROOT / "app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "GovernedEpistemicCuriosityConsumptionFoundation" not in source
    tree = ast.parse(source)
    constructors = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert constructors == [52]
