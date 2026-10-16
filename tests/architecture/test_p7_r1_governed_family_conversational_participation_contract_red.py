from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timezone

import pytest

from app.ambient_proactive_coordination import (
    AmbientAction,
    AmbientObservation,
    AmbientProactiveCoordinator,
    AmbientProactivePolicy,
    AmbientSignalKind,
)
from core.unified_companion_integration import UnifiedCompanionIntegrationResult

SEAM_MODULE = "app.governed_family_conversational_participation"
SEAM_TYPE = "GovernedFamilyConversationalParticipationAdapter"


def _seam_type():
    try:
        module = importlib.import_module(SEAM_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: no bounded adapter composes consented ambient conversation "
            "with existing governed conversational participation"
        )
    seam = getattr(module, SEAM_TYPE, None)
    if seam is None:
        pytest.fail(
            "RED: family conversational participation has no bounded adapter"
        )
    return seam


def test_red_bounded_adapter_exists_without_new_brain() -> None:
    seam = _seam_type()
    source = inspect.getsource(seam)

    assert "living_conversation" in source
    assert "initiative" in source
    assert "social" in source
    assert "brain" not in source.casefold()


def test_red_adapter_consumes_ready_evidence_without_mutating_it() -> None:
    seam = _seam_type()
    source = inspect.getsource(seam)

    assert "UnifiedCompanionIntegrationResult" in source
    assert "conversation_start_allowed =" not in source
    assert "response_realization_allowed =" not in source
    assert "provider_call_allowed =" not in source


def test_contract_ready_never_authorizes_delivery() -> None:
    fields = (
        "activation_allowed",
        "conversation_start_allowed",
        "response_realization_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    )
    annotations = UnifiedCompanionIntegrationResult.__annotations__

    assert all(field in annotations for field in fields)


def test_contract_private_household_speech_remains_restrained() -> None:
    coordinator = AmbientProactiveCoordinator(
        AmbientProactivePolicy(standing_audio_consent=True)
    )
    observation = AmbientObservation(
        kind=AmbientSignalKind.CONVERSATION,
        confidence=0.99,
        summary="private household conversation",
        occurred_at=datetime.now(timezone.utc),
        involves_private_speech=True,
    )

    decision = coordinator.evaluate(observation)

    assert decision.action is AmbientAction.WAIT
    assert decision.rationale == "private_household_speech_requires_restraint"


def test_red_adapter_requires_consent_and_can_defer_or_discard() -> None:
    seam = _seam_type()
    source = inspect.getsource(seam).casefold()

    assert "consent" in source
    assert "defer" in source or "wait" in source
    assert "discard" in source or "suppress" in source


def test_red_adapter_has_no_memory_learning_or_execution_authority() -> None:
    seam = _seam_type()
    source = inspect.getsource(seam)

    forbidden_calls = (
        "remember_governed_learning(",
        "execute_authorized_governed_memory_write(",
        "execute_certified_write_request(",
        "create_learning_candidate(",
    )
    assert not any(call in source for call in forbidden_calls)


def test_red_adapter_reuses_existing_conversational_delivery() -> None:
    seam = _seam_type()
    source = inspect.getsource(seam)

    assert "publish_text" in source or "conversation" in source
    assert "requests." not in source
    assert "subprocess." not in source
