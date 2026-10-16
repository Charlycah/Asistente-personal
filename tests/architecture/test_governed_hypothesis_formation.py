from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.authorized_intellectual_goal_hypothesis_formation import (
    GovernedAuthorizedIntellectualGoalHypothesisFormation,
)
from app.governed_intellectual_goal_investigation_admission import (
    GovernedAuthorizedIntellectualGoal,
)
from core.governed_reasoning.claims import (
    Claim,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
)
from core.governed_reasoning.context import (
    ContextAssemblyStatus,
    ReasoningContextBundle,
    ReasoningQuery,
)
from core.governed_reasoning.governed_hypothesis_formation import (
    GovernedHypothesisFormationFoundationV1,
    GovernedHypothesisFormationStatus,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 11, 22, 0, tzinfo=timezone.utc)
OWNER = "Carlos y Cristina"
QUESTION = "¿Qué explicaciones alternativas pueden resolver esta incógnita?"
SOURCE = "reasoning:intellectual-evolution:001"


def _claim(
    claim_id: str,
    value: str,
    *,
    claim_type: ClaimType = ClaimType.HYPOTHESIS,
) -> Claim:
    origin = (
        ClaimOrigin.RULE if claim_type is ClaimType.RULE_RESULT else ClaimOrigin.HUMAN
    )
    return Claim(
        subject="fenómeno X",
        predicate="podría explicarse por",
        object_value=value,
        claim_type=claim_type,
        origin=origin,
        status=ClaimStatus.PROPOSED,
        owner=OWNER,
        rule_reference=(
            "rule-hypothesis@1" if claim_type is ClaimType.RULE_RESULT else None
        ),
        created_at=NOW,
        claim_id=claim_id,
    )


def _context(
    *claims: Claim,
    status: ContextAssemblyStatus = ContextAssemblyStatus.READY,
    question: str = QUESTION,
    owner: str = OWNER,
) -> ReasoningContextBundle:
    query = ReasoningQuery(
        question,
        owner=owner,
        domains=(ScopeDomain.KNOWLEDGE,),
        as_of=NOW,
    )
    scope = ScopeGuardManager().observe_turn(
        question,
        proposed_domains=(ScopeDomain.KNOWLEDGE,),
        now=NOW,
    ).decision
    return ReasoningContextBundle(
        query=query,
        status=status,
        scope_decision=scope,
        claims=tuple(claims),
        evidence=(),
        decisions=(),
        created_at=NOW,
    )


def _goal() -> GovernedAuthorizedIntellectualGoal:
    return GovernedAuthorizedIntellectualGoal(
        goal_id="authorized-intellectual-goal-hypothesisformation01",
        proposal_id="intellectual-goal-proposal-hypothesisformation01",
        owner=OWNER,
        subject="fenómeno X",
        unknown_element="qué explicación discrimina mejor la evidencia",
        question=QUESTION,
        curiosity_report_id="curiosity-report-hypothesisformation01",
        question_id="curiosity-question-hypothesisformation01",
        source_reference=SOURCE,
        curiosity_source_fingerprint="a" * 64,
        assembly_source_fingerprint="b" * 64,
        relevance_recipient="both",
        initiative_disposition="offer",
        authorization_reference="human-approval:hypothesis-formation:001",
        authorized_by="Carlos",
    )


def test_forms_multiple_candidates_only_from_governed_tentative_claims() -> None:
    context = _context(
        _claim("h1", "mecanismo A"),
        _claim("h2", "mecanismo B", claim_type=ClaimType.ASSUMPTION),
        _claim("other1", "señal no candidata", claim_type=ClaimType.CONFLICT_STATEMENT),
    )

    report = GovernedHypothesisFormationFoundationV1().form(
        owner=OWNER,
        subject="fenómeno X",
        unknown_element="explicación discriminante",
        question=QUESTION,
        goal_reference=_goal().goal_id,
        context=context,
    )

    assert report.status is GovernedHypothesisFormationStatus.FORMED
    assert len(report.candidates) == 2
    assert {item.source_claim_id for item in report.candidates} == {"h1", "h2"}
    assert all(
        item.canonical_authority == "governed_reasoning"
        for item in report.candidates
    )
    assert all(item.creates_facts is False for item in report.candidates)


def test_derived_rule_result_can_supply_a_second_governed_alternative() -> None:
    context = _context(_claim("h1", "mecanismo A"))
    derived = _claim("r1", "mecanismo B", claim_type=ClaimType.RULE_RESULT)

    report = GovernedHypothesisFormationFoundationV1().form(
        owner=OWNER,
        subject="fenómeno X",
        unknown_element="explicación discriminante",
        question=QUESTION,
        goal_reference=_goal().goal_id,
        context=context,
        derived_claims=(derived,),
    )

    assert report.status is GovernedHypothesisFormationStatus.FORMED
    assert {item.source_claim_type for item in report.candidates} == {
        "hypothesis",
        "rule_result",
    }


def test_fails_closed_when_governed_alternatives_are_insufficient() -> None:
    report = GovernedHypothesisFormationFoundationV1().form(
        owner=OWNER,
        subject="fenómeno X",
        unknown_element="explicación discriminante",
        question=QUESTION,
        goal_reference=_goal().goal_id,
        context=_context(_claim("h1", "mecanismo A")),
    )

    assert (
        report.status
        is GovernedHypothesisFormationStatus.INSUFFICIENT_ALTERNATIVES
    )
    assert len(report.candidates) == 1
    assert report.executes_actions is False
    assert report.persists_results is False


def test_review_required_context_exposes_no_hypothesis_candidates() -> None:
    report = GovernedHypothesisFormationFoundationV1().form(
        owner=OWNER,
        subject="fenómeno X",
        unknown_element="explicación discriminante",
        question=QUESTION,
        goal_reference=_goal().goal_id,
        context=_context(
            _claim("h1", "mecanismo A"),
            _claim("h2", "mecanismo B"),
            status=ContextAssemblyStatus.REVIEW_REQUIRED,
        ),
    )

    assert report.status is GovernedHypothesisFormationStatus.REVIEW_REQUIRED
    assert report.candidates == ()


def test_exact_goal_to_reasoning_lineage_is_required() -> None:
    foundation = GovernedHypothesisFormationFoundationV1()
    with pytest.raises(ValueError, match="owner lineage"):
        foundation.form(
            owner=OWNER,
            subject="fenómeno X",
            unknown_element="explicación discriminante",
            question=QUESTION,
            goal_reference=_goal().goal_id,
            context=_context(
                _claim("h1", "mecanismo A"),
                _claim("h2", "mecanismo B"),
                owner="Otra persona",
            ),
        )
    with pytest.raises(ValueError, match="question lineage"):
        foundation.form(
            owner=OWNER,
            subject="fenómeno X",
            unknown_element="explicación discriminante",
            question=QUESTION,
            goal_reference=_goal().goal_id,
            context=_context(
                _claim("h1", "mecanismo A"),
                _claim("h2", "mecanismo B"),
                question="otra pregunta",
            ),
        )


def test_authorized_goal_seam_reuses_reasoning_context_and_inference() -> None:
    context = _context(_claim("h1", "mecanismo A"))
    reasoning = SimpleNamespace(
        context=context,
        inference_run=SimpleNamespace(
            applied_claims=(
                _claim("r1", "mecanismo B", claim_type=ClaimType.RULE_RESULT),
            )
        ),
    )

    report = GovernedAuthorizedIntellectualGoalHypothesisFormation().form(
        _goal(),
        reasoning,
    )

    assert report.status is GovernedHypothesisFormationStatus.FORMED
    assert report.goal_reference == _goal().goal_id
    assert report.reasoning_context_id == context.context_id


def test_official_runtime_exposes_hypothesis_formation_without_parallel_owner() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(encoding="utf-8")
    core_source = (
        ROOT / "core/governed_reasoning/governed_hypothesis_formation.py"
    ).read_text(encoding="utf-8")

    assert "intellectual_hypothesis_formation" in source
    assert "GovernedAuthorizedIntellectualGoalHypothesisFormation()" in source
    assert 'canonical_authority: str = "governed_reasoning"' in core_source
    assert "ResearchAgent" not in core_source
    assert "HypothesisManager" not in core_source
    assert "uses_llm" not in core_source
    assert "GovernedExplicitHypothesisSource(" not in core_source
    assert "ScenarioHypothesis(" not in core_source
    assert "CausalHypothesis(" not in core_source
