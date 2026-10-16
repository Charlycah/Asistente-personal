from __future__ import annotations

import pytest

from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _request(*, owner: str = "Carlos", session_id: str = "a6-scope"):
    return GovernedConversationPipelineRequest(
        owner=owner,
        session_id=session_id,
        text=(
            "Considerá lo que recordamos de mi restricción y el clima actual "
            "para evaluar qué conviene hacer."
        ),
    )


def test_a6_advice_copies_governed_owner_and_scope() -> None:
    advice = UnifiedCognitiveCoordinator(registry=object()).compose_advisory(
        _request()
    )
    assert advice is not None
    assert advice.owner == "Carlos"
    assert advice.scope == "a6-scope"


def test_a6_advice_provenance_names_actual_derivation_sources() -> None:
    advice = UnifiedCognitiveCoordinator(registry=object()).compose_advisory(
        _request()
    )
    assert advice is not None
    assert advice.provenance == (
        "cognitive_planning:required_tools",
        "cognitive_planning:cognitive_needs",
        "decision:unified_cognitive_coordination",
    )


def test_a6_identity_is_isolated_between_callers() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    first = coordinator.compose_advisory(_request(owner="Carlos", session_id="one"))
    second = coordinator.compose_advisory(_request(owner="Cristina", session_id="two"))
    assert first is not None and second is not None
    assert (first.owner, first.scope) == ("Carlos", "one")
    assert (second.owner, second.scope) == ("Cristina", "two")


def test_a6_blank_identity_fails_closed_at_governed_boundary() -> None:
    with pytest.raises(ValueError, match="owner must not be blank"):
        _request(owner=" ")
    with pytest.raises(ValueError, match="session id must not be blank"):
        _request(session_id=" ")


def test_a6_advisory_still_executes_zero_capabilities() -> None:
    class Registry:
        def __init__(self) -> None:
            self.executions = 0

        @property
        def registrations(self):
            return ()

        def execute_registration(self, *args, **kwargs):
            self.executions += 1
            raise AssertionError("advisory path must not execute")

    registry = Registry()
    advice = UnifiedCognitiveCoordinator(registry).compose_advisory(_request())
    assert advice is not None
    assert registry.executions == 0
    assert advice.execution_authorized is False
