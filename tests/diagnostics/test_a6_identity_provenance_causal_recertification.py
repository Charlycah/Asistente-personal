from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

TEXT = (
    "Considerá lo que recordamos de mi restricción y el clima actual "
    "para evaluar qué conviene hacer."
)
EXPECTED_PROVENANCE = (
    "cognitive_planning:required_tools",
    "cognitive_planning:cognitive_needs",
    "decision:unified_cognitive_coordination",
)


def _request(
    *,
    owner: str = "Carlos",
    session_id: str = "causal-cert",
    text: str = TEXT,
) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner=owner,
        session_id=session_id,
        text=text,
    )


def test_a6_owner_is_causally_copied_from_governed_request() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    first = coordinator.compose_advisory(_request(owner="Carlos"))
    second = coordinator.compose_advisory(_request(owner="Cristina"))

    assert first is not None and second is not None
    assert first.needs == second.needs
    assert first.owner == "Carlos"
    assert second.owner == "Cristina"
    assert first.owner != second.owner


def test_a6_scope_is_causally_copied_from_session_boundary() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    first = coordinator.compose_advisory(_request(session_id="scope-a"))
    second = coordinator.compose_advisory(_request(session_id="scope-b"))

    assert first is not None and second is not None
    assert first.needs == second.needs
    assert first.scope == "scope-a"
    assert second.scope == "scope-b"
    assert first.scope != second.scope


def test_a6_same_text_cannot_cross_contaminate_identity() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    carlos = coordinator.compose_advisory(
        _request(owner="Carlos", session_id="carlos-main")
    )
    cristina = coordinator.compose_advisory(
        _request(owner="Cristina", session_id="cristina-main")
    )

    assert carlos is not None and cristina is not None
    assert (carlos.owner, carlos.scope) == ("Carlos", "carlos-main")
    assert (cristina.owner, cristina.scope) == ("Cristina", "cristina-main")
    assert "Cristina" not in (carlos.owner, carlos.scope)
    assert "Carlos" not in (cristina.owner, cristina.scope)


def test_a6_provenance_names_only_actual_derivation_sources() -> None:
    advice = UnifiedCognitiveCoordinator(registry=object()).compose_advisory(
        _request()
    )
    assert advice is not None
    assert advice.provenance == EXPECTED_PROVENANCE
    assert all("memory_id" not in item for item in advice.provenance)
    assert all("weather_id" not in item for item in advice.provenance)
    assert all("external_evidence" not in item for item in advice.provenance)


def test_a6_provenance_is_stable_across_identity_changes() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    first = coordinator.compose_advisory(
        _request(owner="Carlos", session_id="scope-a")
    )
    second = coordinator.compose_advisory(
        _request(owner="Cristina", session_id="scope-b")
    )

    assert first is not None and second is not None
    assert first.provenance == EXPECTED_PROVENANCE
    assert second.provenance == EXPECTED_PROVENANCE


def test_a6_blank_identity_fails_closed_before_composition() -> None:
    with pytest.raises(ValueError, match="owner must not be blank"):
        _request(owner="   ")

    with pytest.raises(ValueError, match="session id must not be blank"):
        _request(session_id="   ")


def test_a6_advice_is_immutable_identity_evidence() -> None:
    advice = UnifiedCognitiveCoordinator(registry=object()).compose_advisory(
        _request()
    )
    assert advice is not None

    with pytest.raises(FrozenInstanceError):
        advice.owner = "Other"


def test_a6_identity_provenance_path_never_executes_capabilities() -> None:
    class Registry:
        registrations = ()

        def __init__(self) -> None:
            self.executions = 0

        def execute_registration(self, *args, **kwargs):
            self.executions += 1
            raise AssertionError("advisory identity path must not execute")

    registry = Registry()
    advice = UnifiedCognitiveCoordinator(registry).compose_advisory(_request())

    assert advice is not None
    assert advice.execution_authorized is False
    assert registry.executions == 0


def test_a6_changed_conditions_preserve_identity_and_provenance() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    first = coordinator.compose_advisory(_request())
    second = coordinator.compose_advisory(
        _request(
            text=(
                "Considerá lo que recordamos de mi restricción; el clima ya no "
                "es relevante para esta decisión."
            )
        )
    )

    assert first is not None and second is not None
    assert "weather" in first.needs
    assert "weather" not in second.needs
    assert first.owner == second.owner == "Carlos"
    assert first.scope == second.scope == "causal-cert"
    assert first.provenance == second.provenance == EXPECTED_PROVENANCE
