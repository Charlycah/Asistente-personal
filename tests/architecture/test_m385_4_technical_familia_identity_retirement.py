from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.household_always_on_bootstrap import (
    COOWNER_PRINCIPAL,
    COOWNER_PROFILE_ID,
    COOWNER_SESSION_ID,
    bootstrap_household,
)
from app.roby_config import DEFAULT_CONFIG, environment_values
from core.personal_identity_and_session_profiles import (
    JsonIdentityProfileStore,
    JsonSessionProfileStore,
    PersonalIdentityProfile,
    RuntimeSessionProfile,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_PACKAGES = (
    "app",
    "application",
    "core",
    "domain",
    "infrastructure",
)
NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)


def _production_sources() -> tuple[str, ...]:
    return tuple(
        path.read_text(encoding="utf-8")
        for package in PRODUCTION_PACKAGES
        for path in (PROJECT_ROOT / package).rglob("*.py")
    )


def test_active_coowner_contract_names_both_people_without_familia() -> None:
    assert COOWNER_PRINCIPAL == "Carlos y Cristina"
    assert COOWNER_PROFILE_ID == "carlos-cristina"
    assert COOWNER_SESSION_ID == "coowners-main"


def test_fresh_bootstrap_persists_two_people_and_one_joint_scope(tmp_path) -> None:
    base = tmp_path / "identity"

    result = bootstrap_household(base_path=base, project_root=tmp_path)
    profiles = JsonIdentityProfileStore(base / "profiles.json").list_profiles()
    sessions = JsonSessionProfileStore(base / "sessions.json").list_sessions()

    assert {item.profile_id for item in profiles} == {
        "carlos",
        "cristina",
        COOWNER_PROFILE_ID,
    }
    assert result.profile.owner == COOWNER_PRINCIPAL
    assert result.profile.participants == ("Carlos", "Cristina")
    assert len(sessions) == 1
    assert sessions[0].session_id == COOWNER_SESSION_ID
    assert sessions[0].profile_id == COOWNER_PROFILE_ID


def test_legacy_identity_metadata_is_normalized_without_touching_memory(
    tmp_path,
) -> None:
    base = tmp_path / "identity"
    JsonIdentityProfileStore(base / "profiles.json").save_profiles(
        (
            PersonalIdentityProfile("carlos", "Carlos", "Carlos"),
            PersonalIdentityProfile("spouse", "Cristina", "Cristina"),
            PersonalIdentityProfile(
                "family-shared",
                "Familia",
                "Familia",
                scope="shared",
                participants=("Carlos", "Cristina"),
            ),
        )
    )
    JsonSessionProfileStore(base / "sessions.json").save_sessions(
        (
            RuntimeSessionProfile(
                "household-main",
                "family-shared",
                created_at=NOW,
                last_active_at=NOW,
            ),
        )
    )
    old_state = (
        base
        / "profiles"
        / "family-shared"
        / "sessions"
        / "household-main"
        / "runtime_state.json"
    )
    old_state.parent.mkdir(parents=True)
    old_state.write_text('{"preserved": true}', encoding="utf-8")

    result = bootstrap_household(base_path=base, project_root=tmp_path)

    profile_payload = (base / "profiles.json").read_text(encoding="utf-8")
    session_payload = (base / "sessions.json").read_text(encoding="utf-8")
    assert "Familia" not in profile_payload
    assert "family-shared" not in profile_payload
    assert "household-main" not in session_payload
    assert result.state_path.read_text(encoding="utf-8") == '{"preserved": true}'
    assert result.migrated_state_from == old_state


def test_configuration_declares_two_coowners_and_no_primary_owner() -> None:
    household = DEFAULT_CONFIG["household"]
    values = environment_values(DEFAULT_CONFIG)

    assert household["owners"] == ["Carlos", "Cristina"]
    assert "owner" not in household
    assert values["ROBY_RUNTIME_OWNER"] == COOWNER_PRINCIPAL


def test_manifest_records_coowners_without_a_familia_identity(tmp_path) -> None:
    base = tmp_path / "identity"
    bootstrap_household(base_path=base, project_root=tmp_path)

    payload = json.loads((base / "household_bootstrap.json").read_text())

    assert payload["version"] == "M385.4"
    assert payload["coowners"] == ["Carlos", "Cristina"]
    assert payload["profile_id"] == COOWNER_PROFILE_ID
    assert payload["session_id"] == COOWNER_SESSION_ID
    assert "Familia" not in json.dumps(payload)


def test_retired_identity_markers_are_absent_from_production_source() -> None:
    combined = "\n".join(_production_sources())

    assert '"Familia"' not in combined
    assert '"family-shared"' not in combined
    assert '"household-main"' not in combined


def test_m385_3_quarantine_is_promoted_to_full_absence() -> None:
    source = (
        PROJECT_ROOT
        / "tests"
        / "architecture"
        / "test_m385_3_copownership_identity_boundaries.py"
    ).read_text(encoding="utf-8")

    assert "retired_joint_identity_markers_are_absent_from_production" in source
    assert "assert observed == set()" in source

