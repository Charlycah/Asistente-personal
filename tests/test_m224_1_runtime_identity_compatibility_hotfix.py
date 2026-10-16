from pathlib import Path

from app.personal_profile_factory import select_runtime_identity_from_environment


def test_legacy_global_state_placeholder_moves_to_household_scope(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path))
    monkeypatch.setenv("ROBY_PROFILE_ID", "spouse")
    monkeypatch.setenv("ROBY_RUNTIME_SESSION_ID", "desktop-main")
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", ".roby/runtime_state.json")
    selected = select_runtime_identity_from_environment()
    assert selected.state_path == (
        tmp_path
        / "profiles"
        / "carlos-cristina"
        / "sessions"
        / "coowners-main"
        / "runtime_state.json"
    )


def test_custom_runtime_state_override_is_replaced_by_household_path(
    tmp_path, monkeypatch
):
    override = tmp_path / "custom" / "runtime.json"
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path / "identity"))
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(override))
    assert select_runtime_identity_from_environment().state_path != override


def test_household_contract_names_carlos_and_cristina(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path))
    selected = select_runtime_identity_from_environment()
    assert selected.profile.participants == ("Carlos", "Cristina")
    assert Path(selected.state_path).parts[-5:-3] == (
        "profiles",
        "carlos-cristina",
    )
