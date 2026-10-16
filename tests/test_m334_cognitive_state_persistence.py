import json
from datetime import datetime, timezone

import pytest

from core.cognitive_state_contract import (
    CognitiveState,
    CognitiveStateStore,
    JsonCognitiveStateStore,
)

NOW = datetime(2026, 7, 28, 15, 30, tzinfo=timezone.utc)


def make_state() -> CognitiveState:
    return CognitiveState(
        active_objective="Help the user",
        current_focus="Persist cognitive state",
        confidence=0.75,
        last_decision="Keep runtime integration out of M334",
        updated_at=NOW,
    )


def test_missing_file_loads_as_absent(tmp_path):
    store = JsonCognitiveStateStore(tmp_path / "state.json")

    assert store.load() is None


def test_save_and_load_round_trip(tmp_path):
    store = JsonCognitiveStateStore(tmp_path / "state.json")
    state = make_state()

    saved_path = store.save(state)

    assert saved_path == tmp_path / "state.json"
    assert store.load() == state


def test_save_creates_parent_directories(tmp_path):
    path = tmp_path / ".roby" / "nested" / "cognitive_state.json"

    JsonCognitiveStateStore(path).save(make_state())

    assert path.is_file()


def test_saved_document_has_versioned_stable_shape(tmp_path):
    path = tmp_path / "state.json"
    JsonCognitiveStateStore(path).save(make_state())

    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload == {
        "schema_version": 1,
        "state": {
            "active_objective": "Help the user",
            "confidence": 0.75,
            "current_focus": "Persist cognitive state",
            "last_decision": "Keep runtime integration out of M334",
            "updated_at": NOW.isoformat(),
        },
    }


def test_save_replaces_previous_snapshot(tmp_path):
    store = JsonCognitiveStateStore(tmp_path / "state.json")
    store.save(make_state())
    replacement = CognitiveState.empty(updated_at=NOW)

    store.save(replacement)

    assert store.load() == replacement


def test_save_leaves_no_temporary_file(tmp_path):
    path = tmp_path / "state.json"

    JsonCognitiveStateStore(path).save(make_state())

    assert list(tmp_path.glob("*.tmp")) == []


def test_delete_reports_whether_a_snapshot_existed(tmp_path):
    store = JsonCognitiveStateStore(tmp_path / "state.json")

    assert not store.delete()
    store.save(make_state())
    assert store.delete()
    assert not store.path.exists()
    assert not store.delete()


def test_default_path_is_project_local(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    assert JsonCognitiveStateStore.default_path() == (
        tmp_path / ".roby" / "cognitive_state.json"
    )


def test_store_protocol_is_runtime_checkable(tmp_path):
    assert isinstance(
        JsonCognitiveStateStore(tmp_path / "state.json"),
        CognitiveStateStore,
    )


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"schema_version": 2, "state": {}},
        {"schema_version": 1},
        {"schema_version": 1, "state": []},
        {
            "schema_version": 1,
            "state": {
                "active_objective": None,
                "current_focus": None,
                "confidence": True,
                "last_decision": None,
                "updated_at": NOW.isoformat(),
            },
        },
        {
            "schema_version": 1,
            "state": {
                "active_objective": None,
                "current_focus": None,
                "confidence": 0.5,
                "last_decision": None,
                "updated_at": "not-a-date",
            },
        },
    ],
)
def test_load_rejects_invalid_documents(tmp_path, payload):
    path = tmp_path / "state.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid cognitive state file"):
        JsonCognitiveStateStore(path).load()


def test_load_rejects_blank_text_through_contract_validation(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "state": {
                    "active_objective": " ",
                    "current_focus": None,
                    "confidence": 0.5,
                    "last_decision": None,
                    "updated_at": NOW.isoformat(),
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid cognitive state file"):
        JsonCognitiveStateStore(path).load()


def test_save_rejects_non_contract_values(tmp_path):
    store = JsonCognitiveStateStore(tmp_path / "state.json")

    with pytest.raises(TypeError, match="CognitiveState"):
        store.save(object())
