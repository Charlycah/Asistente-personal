from __future__ import annotations

from pathlib import Path

from core.cognitive_event_bus import CognitiveEventBus
from core.executive_recovery_health import RecoveryHealthCoordinator
from core.runtime_composition_root import RuntimeCompositionRoot

ROOT = Path(__file__).resolve().parents[2]

RETIRED_PATHS = (
    "core/circuit_breaker.py",
    "core/retry.py",
    "core/event_bus.py",
    "core/logging.py",
    "core/runtime.py",
)


def test_disconnected_legacy_utilities_are_retired_and_current_surfaces_preserved(
) -> None:
    for relative in RETIRED_PATHS:
        assert not (ROOT / relative).exists(), relative

    assert CognitiveEventBus is not None
    assert RecoveryHealthCoordinator is not None
    assert RuntimeCompositionRoot is not None
