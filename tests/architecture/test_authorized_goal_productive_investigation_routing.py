from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from app.authorized_goal_productive_investigation_routing import (
    AuthorizedGoalInvestigationRoutingStatus,
    AuthorizedGoalProductiveInvestigationRoutingV1,
)
from app.governed_intellectual_goal_investigation_admission import (
    GovernedAuthorizedIntellectualGoal,
)
from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from core.governed_reasoning.explicit_hypothesis_source import (
    ExplicitHypothesisSourceKind,
    GovernedExplicitHypothesisSource,
)
from core.persistent_world_model import PersistentWorldModelView

ROOT = Path(__file__).resolve().parents[2]
GOAL_SOURCE = "intellectual-goal-source:routing:001"


def _goal() -> GovernedAuthorizedIntellectualGoal:
    return GovernedAuthorizedIntellectualGoal(
        goal_id="authorized-intellectual-goal-routing001",
        proposal_id="intellectual-goal-proposal-routing001",
        owner="Carlos y Cristina",
        subject="fenómeno X",
        unknown_element="qué evidencia discrimina las hipótesis",
        question="¿Qué explica el fenómeno X?",
        curiosity_report_id="curiosity-report-routing001",
        question_id="curiosity-question-routing001",
        source_reference=GOAL_SOURCE,
        curiosity_source_fingerprint="1" * 64,
        assembly_source_fingerprint="2" * 64,
        relevance_recipient="both",
        initiative_disposition="offer",
        authorization_reference="human-approval:routing001",
        authorized_by="Carlos",
    )


def _scenario(number: int, value: str) -> GovernedExplicitHypothesisSource:
    return GovernedExplicitHypothesisSource(
        source_id=f"explicit-hypothesis-source-routing-{number}",
        kind=ExplicitHypothesisSourceKind.SCENARIO,
        proposition=f"Hipótesis {number}",
        world_domain="household",
        fact_key="phenomenon:x",
        assumed_value=value,
        temporal_scope="current",
        source_reference=GOAL_SOURCE,
        source_fingerprint=f"{number:x}" * 64,
        evidence_codes=(f"source:routing:{number}",),
    )


def _router() -> AuthorizedGoalProductiveInvestigationRoutingV1:
    return AuthorizedGoalProductiveInvestigationRoutingV1(
        OfficialGovernedReasoningRuntimeGateway()
    )


def test_authorized_goal_routes_one_requirement_once_through_g4() -> None:
    result = _router().route(
        _goal(),
        (_scenario(1, "a"), _scenario(2, "b")),
        world=PersistentWorldModelView().build(()),
        originating_reasoning_id="reasoning-routing-001",
    )

    assert result.status is AuthorizedGoalInvestigationRoutingStatus.ADMITTED
    assert result.cap11_admission_invocation_count == 1
    assert result.admission is not None
    assert result.admission.requirement_admission_invocation_count == 1
    assert result.admission.source_reference == GOAL_SOURCE
    assert result.admission.productive_entry_result.episode_start_invocation_count == 1


def test_routing_preserves_goal_lineage_into_discriminating_requirement() -> None:
    result = _router().route(
        _goal(),
        (_scenario(1, "a"), _scenario(2, "b")),
        world=PersistentWorldModelView().build(()),
        originating_reasoning_id="reasoning-routing-002",
    )

    assert result.deepening.source_reference == GOAL_SOURCE
    assert result.discrimination.source_reference == GOAL_SOURCE
    assert len(result.discrimination.discrimination_requirements) == 1
    assert (
        result.discrimination.discrimination_requirements[0].source_reference
        == GOAL_SOURCE
    )


def test_mixed_goal_lineage_fails_closed_before_reasoning() -> None:
    other = GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-other",
        kind=ExplicitHypothesisSourceKind.SCENARIO,
        proposition="Hipótesis ajena",
        world_domain="household",
        fact_key="phenomenon:x",
        assumed_value="c",
        temporal_scope="current",
        source_reference="different-goal-source",
        source_fingerprint="f" * 64,
    )

    with pytest.raises(ValueError, match="lineage does not match goal"):
        _router().route(
            _goal(),
            (_scenario(1, "a"), other),
            world=PersistentWorldModelView().build(()),
            originating_reasoning_id="reasoning-routing-003",
        )


def test_mixed_semantic_kinds_fail_closed() -> None:
    causal = GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-causal",
        kind=ExplicitHypothesisSourceKind.CAUSAL,
        proposition="Hipótesis causal",
        cause_domain="household",
        cause_key="phenomenon:x",
        cause_value="a",
        effect_domain="household",
        effect_key="phenomenon:y",
        effect_value="b",
        temporal_scope="future",
        source_reference=GOAL_SOURCE,
        source_fingerprint="e" * 64,
    )

    with pytest.raises(ValueError, match="one structured kind"):
        _router().route(
            _goal(),
            (_scenario(1, "a"), causal),
            world=PersistentWorldModelView().build(()),
            originating_reasoning_id="reasoning-routing-004",
        )


def test_routing_does_not_use_generic_explanatory_reentry() -> None:
    source = (
        ROOT / "app/authorized_goal_productive_investigation_routing.py"
    ).read_text(encoding="utf-8")

    assert "GovernedExplanatoryModelInvestigationReentryV1" not in source
    assert "bind_productive_epistemic_assessment" not in source
    assert "GovernedAuthorizedIntellectualGoalRequirementAdmissionV1" in source
    assert "GovernedMultiHypothesisProductiveConsumptionV1" in source


def test_reasoning_runtime_remains_certified_byte_identical() -> None:
    digest = hashlib.sha256(
        (ROOT / "app/governed_reasoning_runtime.py").read_bytes()
    ).hexdigest()

    assert digest == (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    )


def test_official_composition_exposes_routing_without_gateway_surgery() -> None:
    composition = (ROOT / "app/official_runtime_composition.py").read_text(
        encoding="utf-8"
    )

    assert "AuthorizedGoalProductiveInvestigationRoutingV1" in composition
    assert "intellectual_investigation_routing" in composition
    assert "root.dependencies" in composition
