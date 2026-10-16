from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.governed_hypothesis_candidate_structured_semantics import (
    GovernedHypothesisCandidateStructuredSemanticsAdmission,
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
from core.governed_reasoning.explicit_hypothesis_source import (
    ExplicitHypothesisSourceKind,
)
from core.governed_reasoning.governed_hypothesis_formation import (
    GovernedHypothesisFormationFoundationV1,
    GovernedHypothesisFormationStatus,
)
from core.governed_reasoning.hypothesis_semantic_grounding import (
    GovernedHypothesisSemanticGroundingFoundationV1,
    GovernedHypothesisStructuredSemantics,
    HypothesisStructuredSemanticsKind,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 11, 23, 15, tzinfo=timezone.utc)
OWNER = "Carlos y Cristina"
QUESTION = "¿Qué explicaciones alternativas pueden resolver esta incógnita?"
GOAL_SOURCE = "reasoning:intellectual-evolution:semantic-grounding"


def _claim(claim_id: str, value: str) -> Claim:
    return Claim(
        subject="temperatura ambiente",
        predicate="podría explicarse por",
        object_value=value,
        claim_type=ClaimType.HYPOTHESIS,
        origin=ClaimOrigin.HUMAN,
        status=ClaimStatus.PROPOSED,
        owner=OWNER,
        created_at=NOW,
        claim_id=claim_id,
    )


def _goal() -> GovernedAuthorizedIntellectualGoal:
    return GovernedAuthorizedIntellectualGoal(
        goal_id="authorized-intellectual-goal-semantics01",
        proposal_id="intellectual-goal-proposal-semantics01",
        owner=OWNER,
        subject="temperatura ambiente",
        unknown_element="qué explicación discrimina mejor la evidencia",
        question=QUESTION,
        curiosity_report_id="curiosity-report-semantics01",
        question_id="curiosity-question-semantics01",
        source_reference=GOAL_SOURCE,
        curiosity_source_fingerprint="1" * 64,
        assembly_source_fingerprint="2" * 64,
        relevance_recipient="both",
        initiative_disposition="offer",
        authorization_reference="human-approval:semantics:001",
        authorized_by="Carlos",
    )


def _formation():
    query = ReasoningQuery(
        QUESTION,
        owner=OWNER,
        domains=(ScopeDomain.KNOWLEDGE,),
        as_of=NOW,
    )
    scope = ScopeGuardManager().observe_turn(
        QUESTION,
        proposed_domains=(ScopeDomain.KNOWLEDGE,),
        now=NOW,
    ).decision
    context = ReasoningContextBundle(
        query=query,
        status=ContextAssemblyStatus.READY,
        scope_decision=scope,
        claims=(
            _claim("candidate-source-1", "sensor descalibrado"),
            _claim("candidate-source-2", "cambio ambiental"),
        ),
        evidence=(),
        decisions=(),
        created_at=NOW,
    )
    report = GovernedHypothesisFormationFoundationV1().form(
        owner=OWNER,
        subject="temperatura ambiente",
        unknown_element="qué explicación discrimina mejor la evidencia",
        question=QUESTION,
        goal_reference=_goal().goal_id,
        context=context,
    )
    assert report.status is GovernedHypothesisFormationStatus.FORMED
    return report


def _scenario_semantics(candidate):
    return GovernedHypothesisStructuredSemantics(
        candidate_id=candidate.candidate_id,
        candidate_fingerprint=candidate.source_claim_fingerprint,
        proposition=candidate.proposition,
        kind=HypothesisStructuredSemanticsKind.SCENARIO,
        source_reference=GOAL_SOURCE,
        source_fingerprint="a" * 64,
        provenance_authority="human_explicit_structured_input",
        world_domain="environment",
        fact_key="temperature",
        assumed_value="high",
        evidence_codes=("explicit_structured_semantics",),
    )


def test_scenario_semantics_admit_existing_explicit_hypothesis_source() -> None:
    candidate = _formation().candidates[0]

    source = GovernedHypothesisSemanticGroundingFoundationV1().admit(
        candidate,
        _scenario_semantics(candidate),
    )

    assert source.kind is ExplicitHypothesisSourceKind.SCENARIO
    assert source.proposition == candidate.proposition
    assert source.world_domain == "environment"
    assert source.fact_key == "temperature"
    assert source.assumed_value == "high"
    assert source.uses_llm is False
    assert source.uses_retrieval is False
    assert source.persists is False


def test_causal_semantics_admit_existing_explicit_hypothesis_source() -> None:
    candidate = _formation().candidates[1]
    semantics = GovernedHypothesisStructuredSemantics(
        candidate_id=candidate.candidate_id,
        candidate_fingerprint=candidate.source_claim_fingerprint,
        proposition=candidate.proposition,
        kind=HypothesisStructuredSemanticsKind.CAUSAL,
        source_reference="human-structured-semantics:002",
        source_fingerprint="b" * 64,
        provenance_authority="human_explicit_structured_input",
        cause_domain="device",
        cause_key="sensor_calibration",
        cause_value="invalid",
        effect_domain="environment",
        effect_key="temperature",
        effect_value="high",
        evidence_codes=("explicit_structured_semantics",),
    )

    source = GovernedHypothesisSemanticGroundingFoundationV1().admit(
        candidate,
        semantics,
    )

    assert source.kind is ExplicitHypothesisSourceKind.CAUSAL
    assert source.cause_domain == "device"
    assert source.cause_key == "sensor_calibration"
    assert source.effect_domain == "environment"
    assert source.effect_key == "temperature"


def test_semantics_require_exact_candidate_identity_and_lineage() -> None:
    candidate = _formation().candidates[0]
    semantics = _scenario_semantics(candidate)

    with pytest.raises(ValueError, match="identity"):
        GovernedHypothesisSemanticGroundingFoundationV1().admit(
            candidate,
            GovernedHypothesisStructuredSemantics(
                **{
                    **semantics.__dict__,
                    "candidate_id": "governed-hypothesis-candidate-other",
                }
            ),
        )
    with pytest.raises(ValueError, match="lineage"):
        GovernedHypothesisSemanticGroundingFoundationV1().admit(
            candidate,
            GovernedHypothesisStructuredSemantics(
                **{
                    **semantics.__dict__,
                    "candidate_fingerprint": "c" * 64,
                }
            ),
        )


def test_semantics_require_exact_candidate_proposition() -> None:
    candidate = _formation().candidates[0]
    semantics = _scenario_semantics(candidate)

    changed = GovernedHypothesisStructuredSemantics(
        **{
            **semantics.__dict__,
            "proposition": "otra proposición",
        }
    )
    with pytest.raises(ValueError, match="proposition"):
        GovernedHypothesisSemanticGroundingFoundationV1().admit(
            candidate,
            changed,
        )


def test_incomplete_or_mixed_semantics_fail_closed() -> None:
    candidate = _formation().candidates[0]
    with pytest.raises(ValueError, match="scenario"):
        GovernedHypothesisStructuredSemantics(
            candidate_id=candidate.candidate_id,
            candidate_fingerprint=candidate.source_claim_fingerprint,
            proposition=candidate.proposition,
            kind=HypothesisStructuredSemanticsKind.SCENARIO,
            source_reference=GOAL_SOURCE,
            source_fingerprint="d" * 64,
            provenance_authority="human_explicit_structured_input",
            world_domain="environment",
            fact_key="temperature",
        )
    with pytest.raises(ValueError, match="cannot contain causal"):
        GovernedHypothesisStructuredSemantics(
            candidate_id=candidate.candidate_id,
            candidate_fingerprint=candidate.source_claim_fingerprint,
            proposition=candidate.proposition,
            kind=HypothesisStructuredSemanticsKind.SCENARIO,
            source_reference=GOAL_SOURCE,
            source_fingerprint="e" * 64,
            provenance_authority="human_explicit_structured_input",
            world_domain="environment",
            fact_key="temperature",
            assumed_value="high",
            cause_domain="device",
        )


def test_application_seam_accepts_only_candidate_from_formed_report() -> None:
    formation = _formation()
    candidate = formation.candidates[0]

    source = GovernedHypothesisCandidateStructuredSemanticsAdmission().admit(
        _goal(),
        formation,
        candidate_id=candidate.candidate_id,
        semantics=_scenario_semantics(candidate),
    )
    assert source.kind is ExplicitHypothesisSourceKind.SCENARIO

    with pytest.raises(ValueError, match="exact formed candidate"):
        GovernedHypothesisCandidateStructuredSemanticsAdmission().admit(
            _goal(),
            formation,
            candidate_id="governed-hypothesis-candidate-missing",
            semantics=_scenario_semantics(candidate),
        )


def test_runtime_wiring_and_no_parallel_semantic_authority() -> None:
    runtime_source = (ROOT / "app/official_runtime_composition.py").read_text(
        encoding="utf-8"
    )
    core_source = (
        ROOT / "core/governed_reasoning/hypothesis_semantic_grounding.py"
    ).read_text(encoding="utf-8")

    assert "hypothesis_structured_semantics" in runtime_source
    assert "GovernedHypothesisCandidateStructuredSemanticsAdmission()" in (
        runtime_source
    )
    assert 'canonical_authority: str = "governed_reasoning"' in core_source
    assert "uses_llm: bool = False" in core_source
    assert "inferred_from_text: bool = False" in core_source
    assert "SemanticBrain" not in core_source
    assert "HypothesisManager" not in core_source
    assert "ResearchAgent" not in core_source
