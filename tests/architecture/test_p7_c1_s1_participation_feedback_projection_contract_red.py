from __future__ import annotations

import importlib
import inspect

import pytest

from core.living_conversation import (
    ConversationalFeedbackOrigin,
    ConversationalFeedbackSignal,
    ConversationalFeedbackSignalKind,
)

SEAM_MODULE = "app.governed_participation_feedback_projection"
SEAM_TYPE = "GovernedParticipationFeedbackProjection"


def _seam_type():
    try:
        module = importlib.import_module(SEAM_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: ordinary human participation feedback has no bounded "
            "projection into the existing M101 feedback contract"
        )
    seam = getattr(module, SEAM_TYPE, None)
    if seam is None:
        pytest.fail(
            "RED: participation feedback has no bounded M101 projection"
        )
    return seam


def test_red_projection_exists_and_reuses_m101_contract() -> None:
    seam = _seam_type()
    source = inspect.getsource(seam)

    assert "ConversationalFeedbackSignal" in source
    assert "ConversationalFeedbackSignalKind" in source
    assert "ConversationalFeedbackOrigin" in source


def test_red_projection_has_no_parallel_feedback_authority() -> None:
    seam = _seam_type()
    source = inspect.getsource(seam).casefold()

    forbidden = (
        "feedbackbrain",
        "socialbrain",
        "participationfeedbackstore",
        "participationfeedbackrepository",
    )
    assert not any(token in source for token in forbidden)


def test_red_projection_preserves_existing_m101_signal_taxonomy() -> None:
    expected = {
        "acceptance",
        "correction",
        "confusion",
        "rejection",
        "deepening",
        "disengagement",
        "no_signal",
    }

    assert {item.value for item in ConversationalFeedbackSignalKind} == expected


def test_red_projection_returns_typed_signal_with_explicit_origin() -> None:
    seam = _seam_type()
    projector = seam()

    signal = projector.project(
        text="Necesito que participes menos por ahora.",
        confidence=0.95,
    )

    assert isinstance(signal, ConversationalFeedbackSignal)
    assert signal.origin is ConversationalFeedbackOrigin.EXPLICIT
    assert signal.kind in {
        ConversationalFeedbackSignalKind.REJECTION,
        ConversationalFeedbackSignalKind.DISENGAGEMENT,
    }
    assert signal.evidence


def test_red_projection_supports_encouragement_without_forcing_speech() -> None:
    seam = _seam_type()
    projector = seam()

    signal = projector.project(
        text="Podés participar más en esta conversación.",
        confidence=0.95,
    )
    source = inspect.getsource(seam).casefold()

    assert signal.kind is ConversationalFeedbackSignalKind.DEEPENING
    assert "publish_text(" not in source
    assert "should_speak = true" not in source
    assert "conversation_start_allowed = true" not in source


def test_red_projection_fails_closed_for_ambiguous_feedback() -> None:
    seam = _seam_type()
    projector = seam()

    signal = projector.project(
        text="Bueno, Roby.",
        confidence=0.30,
    )

    assert signal.kind is ConversationalFeedbackSignalKind.NO_SIGNAL
    assert signal.evidence == ""


def test_red_projection_has_no_memory_execution_or_network_authority() -> None:
    seam = _seam_type()
    source = inspect.getsource(seam)

    forbidden_calls = (
        "remember_governed_learning(",
        "execute_authorized_governed_memory_write(",
        "execute_certified_write_request(",
        "requests.",
        "subprocess.",
        "publish_text(",
    )
    assert not any(call in source for call in forbidden_calls)
