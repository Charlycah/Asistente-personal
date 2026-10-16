from __future__ import annotations

import json
from datetime import datetime, timezone

from app.household_always_on_bootstrap import (
    COOWNER_PROFILE_ID,
    COOWNER_SESSION_ID,
    bootstrap_household,
)
from app.personal_profile_factory import select_runtime_identity_from_environment
from core.personal_identity_and_session_profiles import (
    JsonIdentityProfileStore,
    JsonSessionProfileStore,
    PersonalIdentityProfile,
    RuntimeSessionProfile,
)

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


def test_bootstrap_creates_permanent_shared_household(tmp_path):
    result = bootstrap_household(base_path=tmp_path / "identity", project_root=tmp_path)
    assert result.profile.profile_id == COOWNER_PROFILE_ID
    assert result.profile.owner == "Carlos y Cristina"
    assert result.profile.participants == ("Carlos", "Cristina")
    assert result.session.session_id == COOWNER_SESSION_ID
    assert result.session.profile_id == COOWNER_PROFILE_ID


def test_bootstrap_rebinds_historical_session_without_conflict(tmp_path):
    base = tmp_path / "identity"
    JsonIdentityProfileStore(base / "profiles.json").save_profiles(
        (PersonalIdentityProfile("carlos", "Carlos", "Carlos"),)
    )
    JsonSessionProfileStore(base / "sessions.json").save_sessions(
        (
            RuntimeSessionProfile(
                "desktop-main", "carlos", created_at=NOW, last_active_at=NOW
            ),
        )
    )
    result = bootstrap_household(base_path=base, project_root=tmp_path)
    sessions = JsonSessionProfileStore(base / "sessions.json").list_sessions()
    assert result.migrated_sessions == 1
    assert {item.profile_id for item in sessions} == {COOWNER_PROFILE_ID}
    assert {item.session_id for item in sessions} == {COOWNER_SESSION_ID}


def test_bootstrap_copies_latest_compatible_runtime_state(tmp_path):
    source = (
        tmp_path
        / "identity"
        / "profiles"
        / "carlos"
        / "sessions"
        / "desktop-main"
        / "runtime_state.json"
    )
    source.parent.mkdir(parents=True)
    source.write_text('{"memory": "preserved"}', encoding="utf-8")
    result = bootstrap_household(base_path=tmp_path / "identity", project_root=tmp_path)
    assert result.state_path.read_text(encoding="utf-8") == source.read_text(
        encoding="utf-8"
    )
    assert result.migrated_state_from == source


def test_environment_cannot_select_visible_profile_or_session(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path / "identity"))
    monkeypatch.setenv("ROBY_PROFILE_ID", "carlos")
    monkeypatch.setenv("ROBY_RUNTIME_SESSION_ID", "manual-session")
    selected = select_runtime_identity_from_environment()
    assert selected.profile.profile_id == COOWNER_PROFILE_ID
    assert selected.session.session_id == COOWNER_SESSION_ID


def test_bootstrap_is_idempotent_and_writes_manifest(tmp_path):
    base = tmp_path / "identity"
    first = bootstrap_household(base_path=base, project_root=tmp_path)
    second = bootstrap_household(base_path=base, project_root=tmp_path)
    assert first.session.session_id == second.session.session_id
    payload = json.loads((base / "household_bootstrap.json").read_text())
    assert payload["version"] == "M385.4"
    assert payload["coowners"] == ["Carlos", "Cristina"]
    assert payload["participants"] == ["Carlos", "Cristina"]
