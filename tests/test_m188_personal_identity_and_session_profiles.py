from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.personal_profile_factory import select_runtime_identity_from_environment
from core.personal_identity_and_session_profiles import (
    IdentityScope,
    JsonIdentityProfileStore,
    JsonSessionProfileStore,
    PersonalIdentityProfile,
    PersonalIdentityRegistry,
    SessionStatus,
)
from core.platform_runtime_compatibility import private_file_is_protected

NOW = datetime(2026, 7, 12, 20, 0, tzinfo=timezone.utc)


def registry(tmp_path):
    return PersonalIdentityRegistry(
        profile_store=JsonIdentityProfileStore(tmp_path / "profiles.json"),
        session_store=JsonSessionProfileStore(tmp_path / "sessions.json"),
        defaults=(
            PersonalIdentityProfile("carlos", "Carlos", "Carlos"),
            PersonalIdentityProfile("spouse", "Esposa", "Esposa"),
            PersonalIdentityProfile(
                "family-shared",
                "Familia",
                "Familia",
                scope=IdentityScope.SHARED,
                participants=("Carlos", "Esposa"),
            ),
        ),
    )


def test_registry_persists_default_profiles(tmp_path):
    item = registry(tmp_path)
    assert [profile.profile_id for profile in item.profiles] == [
        "carlos",
        "spouse",
        "family-shared",
    ]
    assert (tmp_path / "profiles.json").exists()


def test_profile_lookup_is_case_insensitive(tmp_path):
    assert registry(tmp_path).profile("CARLOS").owner == "Carlos"


def test_unknown_profile_is_rejected(tmp_path):
    with pytest.raises(KeyError, match="unknown"):
        registry(tmp_path).profile("missing")


def test_private_profile_has_no_shared_participants():
    with pytest.raises(ValueError, match="private"):
        PersonalIdentityProfile(
            "carlos", "Carlos", "Carlos", participants=("Carlos", "Ana")
        )


def test_shared_profile_requires_two_participants():
    with pytest.raises(ValueError, match="two"):
        PersonalIdentityProfile(
            "family", "Familia", "Familia", scope="shared", participants=("Carlos",)
        )


def test_profile_identifier_is_filesystem_safe():
    with pytest.raises(ValueError, match="unsupported"):
        PersonalIdentityProfile("../carlos", "Carlos", "Carlos")


def test_open_session_binds_session_to_profile(tmp_path):
    profile, session = registry(tmp_path).open_session(
        profile_id="carlos", session_id="desktop-main", now=NOW
    )
    assert profile.owner == "Carlos"
    assert session.profile_id == "carlos"
    assert session.status is SessionStatus.ACTIVE


def test_open_session_resumes_and_updates_activity(tmp_path):
    item = registry(tmp_path)
    first = item.open_session(profile_id="carlos", session_id="desktop-main", now=NOW)[
        1
    ]
    later = NOW + timedelta(hours=1)
    second = item.open_session(
        profile_id="carlos", session_id="desktop-main", now=later
    )[1]
    assert second.created_at == first.created_at
    assert second.last_active_at == later


def test_session_cannot_move_between_private_profiles(tmp_path):
    item = registry(tmp_path)
    item.open_session(profile_id="carlos", session_id="desktop-main", now=NOW)
    with pytest.raises(ValueError, match="another identity"):
        item.open_session(profile_id="spouse", session_id="desktop-main", now=NOW)


def test_archived_session_cannot_be_resumed(tmp_path):
    item = registry(tmp_path)
    item.open_session(profile_id="carlos", session_id="old", now=NOW)
    archived = item.archive_session(profile_id="carlos", session_id="old", now=NOW)
    assert archived.status is SessionStatus.ARCHIVED
    with pytest.raises(ValueError, match="archived"):
        item.open_session(profile_id="carlos", session_id="old", now=NOW)


def test_session_store_survives_registry_recreation(tmp_path):
    registry(tmp_path).open_session(profile_id="spouse", session_id="private", now=NOW)
    recreated = registry(tmp_path)
    _, session = recreated.open_session(
        profile_id="spouse", session_id="private", now=NOW + timedelta(minutes=1)
    )
    assert session.profile_id == "spouse"


def test_profile_and_session_files_are_private(tmp_path):
    item = registry(tmp_path)
    item.open_session(profile_id="carlos", session_id="main", now=NOW)
    assert private_file_is_protected(tmp_path / "profiles.json")
    assert private_file_is_protected(tmp_path / "sessions.json")


def test_duplicate_profile_ids_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="unique"):
        PersonalIdentityRegistry(
            profile_store=JsonIdentityProfileStore(tmp_path / "profiles.json"),
            session_store=JsonSessionProfileStore(tmp_path / "sessions.json"),
            defaults=(
                PersonalIdentityProfile("same", "One", "One"),
                PersonalIdentityProfile("SAME", "Two", "Two"),
            ),
        )


def test_factory_uses_shared_household_by_default(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path))
    monkeypatch.delenv("ROBY_PROFILE_ID", raising=False)
    selected = select_runtime_identity_from_environment()
    assert selected.profile.profile_id == "carlos-cristina"
    assert selected.profile.owner == "Carlos y Cristina"
    assert selected.profile.participants == ("Carlos", "Cristina")


def test_factory_ignores_manual_profile_selection(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path))
    monkeypatch.setenv("ROBY_PROFILE_ID", "spouse")
    monkeypatch.setenv("ROBY_PROFILE_SPOUSE_NAME", "Ana")
    selected = select_runtime_identity_from_environment()
    assert selected.profile.profile_id == "carlos-cristina"
    assert selected.profile.owner == "Carlos y Cristina"


def test_factory_uses_invisible_household_runtime_state(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path))
    monkeypatch.setenv("ROBY_RUNTIME_SESSION_ID", "evening")
    selected = select_runtime_identity_from_environment()
    assert selected.state_path == (
        tmp_path
        / "profiles"
        / "carlos-cristina"
        / "sessions"
        / "coowners-main"
        / "runtime_state.json"
    )


def test_explicit_runtime_state_path_is_not_user_visible(tmp_path, monkeypatch):
    override = tmp_path / "custom" / "runtime.json"
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path / "identity"))
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(override))
    selected = select_runtime_identity_from_environment()
    assert selected.state_path != override
    assert selected.state_path.parts[-5:-3] == ("profiles", "carlos-cristina")


def test_persisted_household_definition_wins_over_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path))
    first = select_runtime_identity_from_environment()
    monkeypatch.setenv("ROBY_PROFILE_CARLOS_NAME", "Changed")
    second = select_runtime_identity_from_environment()
    assert first.profile.owner == second.profile.owner == "Carlos y Cristina"
