from __future__ import annotations

import ast
import importlib
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from app.governed_intellectual_goal_proposal import (
    GovernedIntellectualGoalProposalProjectorV1,
)
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
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

MODULE = "app.governed_intellectual_goal_investigation_admission"
ROOT = Path(__file__).resolve().parents[2]
SOURCE = "conversation:turn-intel-g4"
SNAPSHOT = "world:intel-g4:001"


def _api():
    module = importlib.import_module(MODULE)
    return (
        module.GovernedAuthorizedIntellectualGoal,
        module.GovernedIntellectualGoalAuthorizationAdmissionV1,
        module.GovernedAuthorizedIntellectualGoalRequirementAdmissionV1,
    )


def _proposal():
    report = GovernedEpistemicCuriosityFoundation().evaluate(
        MultisourceKnowledgeGapEvidence(
            subject="arquitecturas cognitivas gobernadas",
            source_kind=EpistemicCuriositySourceKind.CONVERSATION,
            source_reference=SOURCE,
            known_elements=("ROBY ya puede proponer un objetivo intelectual",),
            unknown_element="cómo admitirlo sin crear una segunda investigación",
            evidence_codes=("explicit_knowledge_gap", "intel_g4_context"),
            relevance=EpistemicCuriosityRelevance.RELEVANT,
            target_person="Carlos",
        )
    )
    question = report.question_candidate
    assert question is not None
    relevance = RelevanceEvaluator(PersonalInterestCenter())
    assembly = ProductiveConversationalCuriosityWiring(
        relevance,
        PersonalInitiativeEngine(relevance),
    ).assemble(
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
    return GovernedIntellectualGoalProposalProjectorV1().project(
        owner="Carlos y Cristina",
        report=report,
        assembly=assembly,
    )


def _requirement(*, source_reference: str = SOURCE):
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-intel-g4-r1",
        hypothesis_ids=("h1", "h2"),
        source_reference=source_reference,
        world_snapshot_id=SNAPSHOT,
        known_elements=("known",),
        missing_evidence_descriptions=("discriminating evidence",),
        evidence_codes=("comparison:indistinguishable",),
    )


class _ProductiveEntrySpy:
    def __init__(self) -> None:
        self.calls = 0
        self.requirement = None
        self.originating_reasoning_id = None
        self.result = object()

    def admit(self, requirement, *, originating_reasoning_id):
        self.calls += 1
        self.requirement = requirement
        self.originating_reasoning_id = originating_reasoning_id
        return self.result


def test_intel_g4_explicit_authorization_produces_frozen_non_executive_goal() -> None:
    authorized_type, authorization_type, _ = _api()
    proposal = _proposal()

    goal = authorization_type().admit(
        proposal,
        authorization_reference="human-approval:intel-g4:001",
        authorized_by="Carlos",
    )

    assert isinstance(goal, authorized_type)
    assert goal.proposal_id == proposal.proposal_id
    assert goal.owner == proposal.owner
    assert goal.subject == proposal.subject
    assert goal.source_reference == proposal.source_reference
    assert goal.authorization_reference == "human-approval:intel-g4:001"
    assert goal.authorized_by == "Carlos"
    assert goal.authorized is True
    assert goal.read_only is True
    assert goal.non_executive is True
    assert goal.planning_invoked is False
    assert goal.investigation_started is False
    assert goal.executes_capabilities is False
    with pytest.raises(FrozenInstanceError):
        goal.subject = "mutated"


def test_intel_g4_proposal_alone_cannot_self_authorize() -> None:
    _, authorization_type, _ = _api()
    proposal = _proposal()

    with pytest.raises(ValueError, match="authorization"):
        authorization_type().admit(
            proposal,
            authorization_reference="",
            authorized_by="Carlos",
        )

    with pytest.raises(ValueError, match="authorization"):
        authorization_type().admit(
            proposal,
            authorization_reference="human-approval:intel-g4:002",
            authorized_by="",
        )


def test_intel_g4_forwards_exact_existing_requirement_once_to_level2b_entry() -> None:
    _, authorization_type, requirement_admission_type = _api()
    proposal = _proposal()
    goal = authorization_type().admit(
        proposal,
        authorization_reference="human-approval:intel-g4:003",
        authorized_by="Carlos",
    )
    requirement = _requirement()
    spy = _ProductiveEntrySpy()

    result = requirement_admission_type(productive_entry=spy).admit(
        goal,
        requirement,
        originating_reasoning_id="reasoning:intel-g4:001",
    )

    assert spy.calls == 1
    assert spy.requirement is requirement
    assert spy.originating_reasoning_id == "reasoning:intel-g4:001"
    assert result.source_goal is goal
    assert result.source_requirement is requirement
    assert result.productive_entry_result is spy.result
    assert result.requirement_id == requirement.requirement_id
    assert result.source_reference == requirement.source_reference
    assert result.world_snapshot_id == requirement.world_snapshot_id
    assert result.requirement_admission_invocation_count == 1
    assert result.invokes_planning is False
    assert result.invokes_authorization is False
    assert result.invokes_execution is False
    assert result.invokes_reasoning is False


def test_intel_g4_rejects_requirement_with_broken_goal_source_lineage() -> None:
    _, authorization_type, requirement_admission_type = _api()
    goal = authorization_type().admit(
        _proposal(),
        authorization_reference="human-approval:intel-g4:004",
        authorized_by="Carlos",
    )
    spy = _ProductiveEntrySpy()

    with pytest.raises(ValueError, match="lineage"):
        requirement_admission_type(productive_entry=spy).admit(
            goal,
            _requirement(source_reference="conversation:other-turn"),
            originating_reasoning_id="reasoning:intel-g4:002",
        )

    assert spy.calls == 0


def test_intel_g4_adds_no_parallel_research_or_requirement_authority() -> None:
    _api()
    source = (
        ROOT / "app/governed_intellectual_goal_investigation_admission.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_symbols = (
        "IntellectualGoalManager",
        "LearningResearchAgent",
        "ResearchAgent",
        "ResearchLoop",
        "PlanningFoundation",
        "GovernedMultiStepInvestigationPlanningReentryV1",
        "GovernedMultiStepInvestigationAuthorizationReentryV1",
        "GovernedIndependenceAuthorizationBoundaryV1",
        "GovernedRobyInitiatedLibraryAccessV1",
        "OfficialMemoryGateway",
        "LearningCandidate",
    )
    assert not any(symbol in source for symbol in forbidden_symbols)
    assert "DiscriminatingEvidenceRequirement(" not in source
    assert all(
        not (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in {"plan", "execute", "investigate", "reason", "learn"}
        )
        for node in ast.walk(tree)
    )
