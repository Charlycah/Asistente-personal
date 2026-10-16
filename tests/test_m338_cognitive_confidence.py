from datetime import datetime, timezone

import pytest

from core.cognitive_confidence import (
    Confidence,
    ConfidenceController,
    ConfidenceLevel,
    ConfidenceManager,
    ConfidenceResolver,
    ExplicitConfidenceResolver,
)
from core.cognitive_state_contract import CognitiveState, CognitiveStateUpdate

NOW = datetime(2026, 7, 27, 21, 0, tzinfo=timezone.utc)


class RecordingUpdater:
    def __init__(self) -> None:
        self.changes: list[CognitiveStateUpdate] = []

    def snapshot(self) -> CognitiveState:
        return CognitiveState.empty(updated_at=NOW)

    def update(self, changes: CognitiveStateUpdate) -> CognitiveState:
        self.changes.append(changes)
        confidence = changes.confidence
        assert isinstance(confidence, float)
        return CognitiveState(None, None, confidence, None, NOW)

    def reset(self) -> CognitiveState:
        return self.snapshot()


def make_confidence(
    level: ConfidenceLevel = ConfidenceLevel.HIGH,
    *,
    reason: str = "Evidencia explícita",
) -> Confidence:
    return Confidence(level=level, reason=reason, updated_at=NOW)


def test_confidence_levels_have_stable_scores():
    assert [level.score for level in ConfidenceLevel] == [0.1, 0.3, 0.5, 0.75, 0.95]


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.0, ConfidenceLevel.VERY_LOW),
        (0.3, ConfidenceLevel.LOW),
        (0.51, ConfidenceLevel.MEDIUM),
        (0.8, ConfidenceLevel.HIGH),
        (1.0, ConfidenceLevel.VERY_HIGH),
    ],
)
def test_level_from_score_is_deterministic(score, expected):
    assert ConfidenceLevel.from_score(score) is expected


def test_level_from_score_rejects_out_of_range_values():
    with pytest.raises(ValueError):
        ConfidenceLevel.from_score(1.1)


def test_confidence_normalizes_reason():
    confidence = make_confidence(reason="  Evidencia explícita  ")
    assert confidence.reason == "Evidencia explícita"


def test_confidence_rejects_blank_reason():
    with pytest.raises(ValueError):
        make_confidence(reason="   ")


def test_confidence_requires_aware_timestamp():
    with pytest.raises(ValueError):
        Confidence(ConfidenceLevel.HIGH, "razón", NOW.replace(tzinfo=None))


def test_uncertainty_is_complement_of_score():
    confidence = make_confidence(ConfidenceLevel.HIGH)
    assert confidence.score == 0.75
    assert confidence.uncertainty == 0.25


def test_resolver_protocol_is_runtime_checkable():
    assert isinstance(ExplicitConfidenceResolver(), ConfidenceResolver)


def test_resolver_keeps_current_without_candidate():
    resolver = ExplicitConfidenceResolver()
    current = make_confidence()
    assert resolver.resolve(current, None) is current


def test_resolver_selects_explicit_candidate():
    resolver = ExplicitConfidenceResolver()
    candidate = make_confidence(ConfidenceLevel.VERY_HIGH)
    assert resolver.resolve(None, candidate) is candidate


def test_manager_protocol_is_runtime_checkable():
    manager = ConfidenceManager(
        RecordingUpdater(),
        ExplicitConfidenceResolver(),
        clock=lambda: NOW,
    )
    assert isinstance(manager, ConfidenceController)


def test_manager_starts_without_explicit_confidence():
    manager = ConfidenceManager(
        RecordingUpdater(),
        ExplicitConfidenceResolver(),
        clock=lambda: NOW,
    )
    assert manager.current() is None
    assert manager.has_confidence() is False


def test_manager_sets_and_mirrors_confidence_score():
    updater = RecordingUpdater()
    manager = ConfidenceManager(
        updater,
        ExplicitConfidenceResolver(),
        clock=lambda: NOW,
    )
    confidence = make_confidence(ConfidenceLevel.VERY_HIGH)
    assert manager.set(confidence) is confidence
    assert manager.current() is confidence
    assert updater.changes == [CognitiveStateUpdate(confidence=0.95)]


def test_manager_keep_has_no_persistence_side_effect():
    updater = RecordingUpdater()
    manager = ConfidenceManager(
        updater,
        ExplicitConfidenceResolver(),
        clock=lambda: NOW,
    )
    confidence = make_confidence()
    manager.set(confidence)
    assert manager.keep() is confidence
    assert len(updater.changes) == 1


def test_manager_reset_uses_medium_by_default():
    updater = RecordingUpdater()
    manager = ConfidenceManager(
        updater,
        ExplicitConfidenceResolver(),
        clock=lambda: NOW,
    )
    reset = manager.reset(reason="Reinicio cognitivo")
    assert reset.level is ConfidenceLevel.MEDIUM
    assert reset.reason == "Reinicio cognitivo"
    assert updater.changes[-1] == CognitiveStateUpdate(confidence=0.5)


def test_manager_can_use_explicit_default_level():
    manager = ConfidenceManager(
        RecordingUpdater(),
        ExplicitConfidenceResolver(),
        clock=lambda: NOW,
        default_level=ConfidenceLevel.LOW,
    )
    assert manager.reset(reason="Política conservadora").level is ConfidenceLevel.LOW


def test_manager_keeps_local_value_when_state_update_fails():
    class FailingUpdater(RecordingUpdater):
        def update(self, changes: CognitiveStateUpdate) -> CognitiveState:
            raise OSError("write failed")

    manager = ConfidenceManager(
        FailingUpdater(),
        ExplicitConfidenceResolver(),
        clock=lambda: NOW,
    )
    with pytest.raises(OSError):
        manager.set(make_confidence())
    assert manager.current() is None
