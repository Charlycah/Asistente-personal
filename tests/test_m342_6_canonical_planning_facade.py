from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.canonical_planning_facade import (
    CanonicalPlanningFacade,
    CanonicalPlanningOperation,
    CanonicalPlanningRole,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


class RecordingPlanner:
    def __init__(self):
        self.calls = []

    def intercept(self, request, *, now):
        self.calls.append((request, now))
        return GovernedOperationalInterception(
            response_text="plan ejecutado",
            rationale="recording_planner",
        )


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_planning_facade_declares_one_official_primary():
    snapshot = CanonicalPlanningFacade().snapshot
    primaries = [
        component
        for component in snapshot.components
        if component.role is CanonicalPlanningRole.PRIMARY
    ]

    assert snapshot.schema_version == "m342.6"
    assert snapshot.primary == "executive_planning"
    assert [component.key for component in primaries] == ["executive_planning"]


def test_specialized_planners_remain_subordinate():
    snapshot = CanonicalPlanningFacade().snapshot

    assert snapshot.component_for("adaptive_executive_planning").role is (
        CanonicalPlanningRole.SPECIALIZED
    )
    assert snapshot.component_for("autonomous_action_planning").role is (
        CanonicalPlanningRole.SPECIALIZED
    )
    assert snapshot.component_for("legacy_planning").role is (
        CanonicalPlanningRole.LEGACY
    )


def test_cognitive_planner_remains_shadow_and_observational():
    component = CanonicalPlanningFacade().snapshot.component_for(
        "cognitive_planner_shadow"
    )

    assert component.role is CanonicalPlanningRole.SHADOW
    assert component.operational is False
    assert component.operations == (CanonicalPlanningOperation.OBSERVE,)


def test_unbound_facade_is_observable_but_not_operational():
    facade = CanonicalPlanningFacade()
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="session-1",
        text="si llueve, avisame",
    )

    assert facade.bound is False
    with pytest.raises(RuntimeError, match="not bound"):
        facade.intercept(request, now=datetime.now(timezone.utc))


def test_bound_facade_delegates_without_changing_planning_semantics():
    planner = RecordingPlanner()
    facade = CanonicalPlanningFacade(planner=planner)
    now = datetime(2026, 7, 28, tzinfo=timezone.utc)
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="session-1",
        text="si llueve, avisame",
    )

    result = facade.intercept(request, now=now)

    assert facade.bound is True
    assert planner.calls == [(request, now)]
    assert result is not None
    assert result.response_text == "plan ejecutado"
    assert result.rationale == "recording_planner"


def test_gateway_exposes_planning_consolidation_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.canonical_planning
    result = gateway.converse("hola")
    after = gateway.canonical_planning

    assert result.response == "echo:hola"
    assert before == after
    assert before.primary == "executive_planning"
