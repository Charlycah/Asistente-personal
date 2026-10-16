from __future__ import annotations

import ast
import importlib
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from app.personal_initiative_engine import PersonalInitiativeEngine
from app.personal_interest_center import InterestTopic, PersonalInterestCenter
from app.productive_conversational_curiosity_wiring import (
    ProductiveConversationalCuriosityWiring,
)
from app.relevance_evaluator import RelevanceCandidate, RelevanceEvaluator
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)

MODULE = "app.governed_intellectual_goal_proposal"
ROOT = Path(__file__).resolve().parents[2]


def _api():
    module = importlib.import_module(MODULE)
    return (
        module.GovernedIntellectualGoalProposal,
        module.GovernedIntellectualGoalProposalProjectorV1,
    )


def _report(*, source_reference: str = "conversation:turn-intel-g3"):
    return GovernedEpistemicCuriosityFoundation().evaluate(
        MultisourceKnowledgeGapEvidence(
            subject="arquitecturas cognitivas gobernadas",
            source_kind=EpistemicCuriositySourceKind.CONVERSATION,
            source_reference=source_reference,
            known_elements=("ROBY ya posee curiosidad gobernada",),
            unknown_element="cómo formalizar una propuesta intelectual no ejecutiva",
            evidence_codes=("explicit_knowledge_gap", "governed_curiosity_context"),
            relevance=EpistemicCuriosityRelevance.RELEVANT,
            target_person="Carlos",
        )
    )


def _assembly(report):
    question = report.question_candidate
    assert question is not None
    relevance = RelevanceEvaluator(PersonalInterestCenter())
    wiring = ProductiveConversationalCuriosityWiring(
        relevance,
        PersonalInitiativeEngine(relevance),
    )
    assembly = wiring.assemble(
        report,
        RelevanceCandidate(
            title=question.question,
            topics=frozenset({InterestTopic.PROGRAMMING}),
            importance=10,
            verification="confirmed",
            information_kind="guidance",
        ),
    )
    assert assembly is not None
    return assembly


def test_intel_g3_exposes_frozen_non_executive_proposal_contract() -> None:
    proposal_type, projector_type = _api()
    report = _report()
    assembly = _assembly(report)

    proposal = projector_type().project(
        owner="Carlos y Cristina",
        report=report,
        assembly=assembly,
    )

    assert isinstance(proposal, proposal_type)
    assert proposal.proposal_id.startswith("intellectual-goal-proposal-")
    assert proposal.read_only is True
    assert proposal.non_executive is True
    assert proposal.authorization_required is True
    with pytest.raises(FrozenInstanceError):
        proposal.subject = "mutated"


def test_intel_g3_preserves_exact_curiosity_relevance_initiative_lineage() -> None:
    _, projector_type = _api()
    report = _report()
    assembly = _assembly(report)
    question = report.question_candidate
    assert question is not None

    proposal = projector_type().project(
        owner="Carlos y Cristina",
        report=report,
        assembly=assembly,
    )

    assert proposal.owner == "Carlos y Cristina"
    assert proposal.subject == question.subject
    assert proposal.unknown_element == question.unknown_element
    assert proposal.question == assembly.question
    assert proposal.curiosity_report_id == report.report_id
    assert proposal.question_id == assembly.question_id
    assert proposal.source_reference == question.source_reference
    assert proposal.curiosity_source_fingerprint == report.source_fingerprint
    assert proposal.assembly_source_fingerprint == assembly.source_fingerprint
    assert (
        proposal.relevance_recipient
        == assembly.consumption.relevance.recipient.value
    )
    assert (
        proposal.initiative_disposition
        == assembly.consumption.initiative.disposition.value
    )


def test_intel_g3_rejects_mismatched_curiosity_and_productive_assembly() -> None:
    _, projector_type = _api()
    report = _report(source_reference="conversation:turn-a")
    other = _report(source_reference="conversation:turn-b")
    assembly = _assembly(other)

    with pytest.raises(ValueError, match="lineage"):
        projector_type().project(
            owner="Carlos y Cristina",
            report=report,
            assembly=assembly,
        )


def test_intel_g3_stops_before_operational_authorities() -> None:
    _, projector_type = _api()
    report = _report()
    proposal = projector_type().project(
        owner="Carlos y Cristina",
        report=report,
        assembly=_assembly(report),
    )

    assert proposal.authorized is False
    assert proposal.planning_invoked is False
    assert proposal.investigation_started is False
    assert proposal.executes_capabilities is False
    assert proposal.persists_results is False
    assert proposal.creates_memory is False
    assert proposal.creates_learning_candidate is False
    assert proposal.modifies_knowledge is False
    assert proposal.starts_background_process is False


def test_intel_g3_adds_no_parallel_authority_or_lateral_execution_path() -> None:
    _api()
    source = (ROOT / "app/governed_intellectual_goal_proposal.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    forbidden_symbols = (
        "CuriosityManager",
        "IntellectualGoalManager",
        "LearningAgendaManager",
        "PlanningFoundation",
        "OfficialMemoryGateway",
        "GovernedMultiStepInvestigationEpisodeBoundaryV1",
        "GovernedRobyInitiatedLibraryAccessV1",
        "LearningCandidate",
    )
    assert not any(symbol in source for symbol in forbidden_symbols)
    assert all(
        not (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in {"execute", "plan", "authorize", "investigate", "learn"}
        )
        for node in ast.walk(tree)
    )
