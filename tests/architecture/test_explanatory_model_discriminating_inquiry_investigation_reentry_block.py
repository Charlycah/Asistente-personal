from __future__ import annotations

from app.governed_explanatory_model_investigation_reentry import (
    GovernedExplanatoryModelInvestigationReentryStatus,
)
from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from tests.architecture import (
    test_ordinary_multi_hypothesis_reachability_block as ordinary,
)


def _causal_model_with_requirement():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    ordinary._bind(
        gateway,
        ordinary._causal(
            1, effect_key="humidity:state", proposition="Aumenta humedad."
        ),
        0,
    )
    turn_id, _, _ = ordinary._bind(
        gateway,
        ordinary._causal(2, effect_key="energy:use", proposition="Aumenta consumo."),
        1,
    )
    model = gateway.productive_explanatory_model_consumption(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    assert model is not None
    assert len(model.discrimination.discrimination_requirements) == 1
    return gateway, turn_id, model


def test_ordinary_explanatory_model_enters_existing_investigation_boundary() -> None:
    gateway, turn_id, model = _causal_model_with_requirement()
    reentry = gateway.productive_explanatory_investigation_reentry(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    assert reentry is not None
    assert reentry.status is GovernedExplanatoryModelInvestigationReentryStatus.ADMITTED
    assert reentry.explanatory_model_id == model.model.model_id
    assert reentry.investigation_entry is not None
    assert reentry.investigation_entry.eligible_for_existing_planning


def test_exact_discrimination_requirement_identity_and_lineage_are_preserved() -> None:
    gateway, turn_id, model = _causal_model_with_requirement()
    requirement = model.discrimination.discrimination_requirements[0]
    reentry = gateway.productive_explanatory_investigation_reentry(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    assert reentry is not None
    assert reentry.requirement is requirement
    assert reentry.source_reference == requirement.source_reference
    assert reentry.world_snapshot_id == requirement.world_snapshot_id
    assert reentry.investigation_entry is not None
    assert reentry.investigation_entry.requirement_id == requirement.requirement_id


def test_investigation_reentry_is_exposed_as_same_turn_reference_only() -> None:
    gateway, turn_id, _ = _causal_model_with_requirement()
    refs = gateway.productive_explanatory_investigation_reference_ids(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    reentry = gateway.productive_explanatory_investigation_reentry(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    assert reentry is not None and reentry.investigation_entry is not None
    assert reentry.reentry_id in refs
    assert reentry.requirement.requirement_id in refs
    assert reentry.investigation_entry.episode_id in refs
    assert gateway.productive_explanatory_investigation_reference_ids(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id="other-turn",
    ) == ()


def test_model_without_discriminating_requirement_does_not_start_investigation(
) -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    ordinary._bind(
        gateway,
        ordinary._scenario(1, value="on", proposition="Está encendida."),
        0,
    )
    turn_id, _, _ = ordinary._bind(
        gateway,
        ordinary._scenario(2, value="off", proposition="Está apagada."),
        1,
    )
    reentry = gateway.productive_explanatory_investigation_reentry(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    assert reentry is not None
    assert reentry.status is (
        GovernedExplanatoryModelInvestigationReentryStatus.NO_DISCRIMINATING_INQUIRY
    )
    assert reentry.requirement is None
    assert reentry.investigation_entry is None


def test_reentry_does_not_plan_authorize_execute_or_acquire_evidence() -> None:
    gateway, turn_id, _ = _causal_model_with_requirement()
    reentry = gateway.productive_explanatory_investigation_reentry(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    assert reentry is not None
    assert reentry.read_only
    assert not reentry.planning_execution_authorized
    assert not reentry.invokes_planning
    assert not reentry.invokes_authorization
    assert not reentry.invokes_execution
    assert not reentry.invokes_capabilities
    assert not reentry.acquires_evidence
    assert not reentry.creates_questions
    assert not reentry.modifies_memory
    assert not reentry.modifies_world_model
    assert not reentry.creates_learning
    assert not reentry.starts_background_process
    assert not reentry.grants_authority


def test_existing_episode_authority_and_bounded_budget_are_preserved() -> None:
    gateway, turn_id, _ = _causal_model_with_requirement()
    reentry = gateway.productive_explanatory_investigation_reentry(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    assert reentry is not None and reentry.investigation_entry is not None
    state = reentry.investigation_entry.episode_state
    assert state is not None
    assert reentry.canonical_episode_authority == (
        "multistep_investigation_episode_boundary"
    )
    assert state.max_acquisitions == 2
    assert state.consumed_acquisitions == 0
    assert state.remaining_acquisitions == 2
    assert not state.planning_execution_authorized
