from datetime import datetime, timedelta, timezone

import pytest

from core.cognitive_focus import (
    Focus,
    FocusController,
    FocusManager,
    FocusResolver,
    FocusType,
    PriorityFocusResolver,
)
from core.cognitive_state_contract import CognitiveState, CognitiveStateUpdate

NOW = datetime(2026, 7, 27, 20, 0, tzinfo=timezone.utc)


class RecordingUpdater:
    def __init__(self) -> None:
        self.changes: list[CognitiveStateUpdate] = []

    def snapshot(self) -> CognitiveState:
        return CognitiveState.empty(updated_at=NOW)

    def update(self, changes: CognitiveStateUpdate) -> CognitiveState:
        self.changes.append(changes)
        return CognitiveState(
            active_objective=None,
            current_focus=changes.current_focus,
            confidence=0.0,
            last_decision=None,
            updated_at=NOW,
        )

    def reset(self) -> CognitiveState:
        return self.snapshot()


def make_focus(
    *,
    identifier: str = "focus-1",
    title: str = "Implementar M337",
    priority: int = 1,
    kind: FocusType = FocusType.TASK,
) -> Focus:
    return Focus(
        identifier=identifier,
        type=kind,
        title=title,
        description="Foco de prueba",
        priority=priority,
        created_at=NOW,
        updated_at=NOW,
    )


def test_focus_normalizes_text_fields():
    focus = Focus(
        identifier="  focus-1 ",
        type=FocusType.TASK,
        title="  Implementar M337 ",
        description="  Foco de prueba ",
        priority=1,
        created_at=NOW,
        updated_at=NOW,
    )
    assert focus.identifier == "focus-1"
    assert focus.title == "Implementar M337"
    assert focus.description == "Foco de prueba"


@pytest.mark.parametrize("field", ["identifier", "title"])
def test_focus_rejects_blank_required_text(field):
    values = {"identifier": "focus-1", "title": "M337"}
    values[field] = "   "
    with pytest.raises(ValueError):
        make_focus(**values)


def test_focus_rejects_blank_description():
    with pytest.raises(ValueError):
        Focus("id", FocusType.TASK, "title", " ", 1, NOW, NOW)


def test_focus_rejects_invalid_priority():
    with pytest.raises(ValueError):
        make_focus(priority=-1)


def test_focus_requires_aware_timestamps():
    with pytest.raises(ValueError):
        Focus("id", FocusType.TASK, "title", None, 1, NOW.replace(tzinfo=None), NOW)


def test_focus_rejects_update_before_creation():
    with pytest.raises(ValueError):
        Focus("id", FocusType.TASK, "title", None, 1, NOW, NOW - timedelta(seconds=1))


def test_resolver_protocol_is_runtime_checkable():
    assert isinstance(PriorityFocusResolver(), FocusResolver)


def test_resolver_selects_first_focus():
    focus = make_focus()
    assert PriorityFocusResolver().resolve(None, focus) is focus


def test_resolver_replaces_only_with_higher_priority():
    resolver = PriorityFocusResolver()
    current = make_focus(priority=2)
    higher = make_focus(identifier="higher", priority=3)
    equal = make_focus(identifier="equal", priority=2)
    assert resolver.resolve(current, higher) is higher
    assert resolver.resolve(current, equal) is current


def test_manager_protocol_is_runtime_checkable():
    manager = FocusManager(RecordingUpdater(), PriorityFocusResolver())
    assert isinstance(manager, FocusController)


def test_manager_starts_without_focus():
    manager = FocusManager(RecordingUpdater(), PriorityFocusResolver())
    assert manager.current_focus() is None
    assert manager.has_focus() is False


def test_manager_sets_and_mirrors_selected_focus():
    updater = RecordingUpdater()
    manager = FocusManager(updater, PriorityFocusResolver())
    focus = make_focus()
    assert manager.set_focus(focus) is focus
    assert manager.current_focus() is focus
    assert updater.changes == [CognitiveStateUpdate(current_focus=focus.title)]


def test_manager_does_not_write_when_candidate_is_rejected():
    updater = RecordingUpdater()
    manager = FocusManager(updater, PriorityFocusResolver())
    current = make_focus(priority=3)
    manager.set_focus(current)
    rejected = make_focus(identifier="low", priority=1)
    assert manager.set_focus(rejected) is current
    assert len(updater.changes) == 1


def test_manager_can_force_replace_focus():
    updater = RecordingUpdater()
    manager = FocusManager(updater, PriorityFocusResolver())
    manager.set_focus(make_focus(priority=3))
    replacement = make_focus(identifier="new", title="Esperar respuesta", priority=0)
    assert manager.replace_focus(replacement) is replacement
    assert updater.changes[-1] == CognitiveStateUpdate(
        current_focus="Esperar respuesta"
    )


def test_manager_clears_focus_and_cognitive_state():
    updater = RecordingUpdater()
    manager = FocusManager(updater, PriorityFocusResolver())
    manager.set_focus(make_focus())
    manager.clear_focus()
    assert manager.current_focus() is None
    assert manager.has_focus() is False
    assert updater.changes[-1] == CognitiveStateUpdate(current_focus=None)


def test_clearing_empty_manager_has_no_side_effect():
    updater = RecordingUpdater()
    FocusManager(updater, PriorityFocusResolver()).clear_focus()
    assert updater.changes == []


def test_manager_keeps_local_focus_when_state_update_fails():
    class FailingUpdater(RecordingUpdater):
        def update(self, changes: CognitiveStateUpdate) -> CognitiveState:
            raise OSError("write failed")

    manager = FocusManager(FailingUpdater(), PriorityFocusResolver())
    with pytest.raises(OSError):
        manager.set_focus(make_focus())
    assert manager.current_focus() is None
