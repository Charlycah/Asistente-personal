from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.canonical_decision_facade import (
    CanonicalDecisionFacade,
    CanonicalDecisionOperation,
    CanonicalDecisionRole,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


class RecordingCoordinator:
    def __init__(self):
        self.calls = []

    def intercept(self, request, *, now):
        self.calls.append((request, now))
        return GovernedOperationalInterception(
            response_text="decisión coordinada",
            rationale="recording_coordinator",
        )


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_decision_facade_declares_one_official_primary():
    snapshot = CanonicalDecisionFacade().snapshot
    primaries = [
        component
        for component in snapshot.components
        if component.role is CanonicalDecisionRole.PRIMARY
    ]

    assert snapshot.schema_version == "m342.7"
    assert snapshot.primary == "unified_cognitive_coordination"
    assert [component.key for component in primaries] == [
        "unified_cognitive_coordination"
    ]


def test_executive_director_remains_a_collaborator():
    component = CanonicalDecisionFacade().snapshot.component_for(
        "executive_director"
    )

    assert component.role is CanonicalDecisionRole.COLLABORATOR
    assert component.operations == (CanonicalDecisionOperation.ADVISE,)
    assert component.operational is True


def test_specialized_and_shadow_decisions_remain_subordinate():
    snapshot = CanonicalDecisionFacade().snapshot
    kernel = snapshot.component_for("cognitive_decision_kernel")
    shadow = snapshot.component_for("cognitive_planning_shadow_decision")

    assert kernel.role is CanonicalDecisionRole.SPECIALIZED
    assert kernel.operational is False
    assert shadow.role is CanonicalDecisionRole.SHADOW
    assert shadow.operational is False
    assert shadow.operations == (CanonicalDecisionOperation.OBSERVE,)


def test_unbound_facade_is_observable_but_not_operational():
    facade = CanonicalDecisionFacade()
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="session-1",
        text="organiza mi día",
    )

    assert facade.bound is False
    with pytest.raises(RuntimeError, match="not bound"):
        facade.intercept(request, now=datetime.now(timezone.utc))


def test_bound_facade_delegates_without_changing_decision_semantics():
    coordinator = RecordingCoordinator()
    facade = CanonicalDecisionFacade(coordinator=coordinator)
    now = datetime(2026, 7, 28, tzinfo=timezone.utc)
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="session-1",
        text="organiza mi día",
    )

    result = facade.intercept(request, now=now)

    assert facade.bound is True
    assert coordinator.calls == [(request, now)]
    assert result is not None
    assert result.response_text == "decisión coordinada"
    assert result.rationale == "recording_coordinator"


def test_gateway_exposes_decision_consolidation_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.canonical_decision
    result = gateway.converse("hola")
    after = gateway.canonical_decision

    assert result.response == "echo:hola"
    assert before == after
    assert before.primary == "unified_cognitive_coordination"
