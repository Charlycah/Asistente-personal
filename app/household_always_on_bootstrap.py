from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from core.personal_identity_and_session_profiles import (
    IdentityScope,
    JsonIdentityProfileStore,
    JsonSessionProfileStore,
    PersonalIdentityProfile,
    RuntimeSessionProfile,
    SessionStatus,
)

COOWNER_PROFILE_ID = "carlos-cristina"
COOWNER_SESSION_ID = "coowners-main"
COOWNER_PRINCIPAL = "Carlos y Cristina"


@dataclass(frozen=True)
class HouseholdBootstrapResult:
    profile: PersonalIdentityProfile
    session: RuntimeSessionProfile
    state_path: Path
    migrated_sessions: int = 0
    migrated_state_from: Path | None = None


def bootstrap_household(
    *, base_path: Path, project_root: Path
) -> HouseholdBootstrapResult:
    """Create and open ROBY's single invisible household conversation boundary."""
    profile_store = JsonIdentityProfileStore(base_path / "profiles.json")
    session_store = JsonSessionProfileStore(base_path / "sessions.json")
    profiles = _household_profiles(profile_store.list_profiles())
    profile_store.save_profiles(profiles)
    profile = next(item for item in profiles if item.profile_id == COOWNER_PROFILE_ID)

    now = datetime.now(timezone.utc)
    sessions = list(session_store.list_sessions())
    migrated = 0
    if sessions:
        canonical = RuntimeSessionProfile(
            session_id=COOWNER_SESSION_ID,
            profile_id=COOWNER_PROFILE_ID,
            created_at=min(item.created_at for item in sessions),
            last_active_at=max(now, *(item.last_active_at for item in sessions)),
        )
        migrated = sum(
            item.session_id != COOWNER_SESSION_ID
            or item.profile_id != COOWNER_PROFILE_ID
            or item.status is not SessionStatus.ACTIVE
            for item in sessions
        )
    else:
        canonical = RuntimeSessionProfile(
            session_id=COOWNER_SESSION_ID,
            profile_id=COOWNER_PROFILE_ID,
            created_at=now,
            last_active_at=now,
        )
    session_store.save_sessions((canonical,))

    state_path = (
        base_path
        / "profiles"
        / COOWNER_PROFILE_ID
        / "sessions"
        / COOWNER_SESSION_ID
        / "runtime_state.json"
    )
    migrated_from = _migrate_runtime_state(
        target=state_path,
        base_path=base_path,
        project_root=project_root,
    )
    _write_manifest(base_path, profile, canonical, migrated, migrated_from)
    return HouseholdBootstrapResult(
        profile=profile,
        session=canonical,
        state_path=state_path,
        migrated_sessions=migrated,
        migrated_state_from=migrated_from,
    )


def _household_profiles(
    existing: tuple[PersonalIdentityProfile, ...],
) -> tuple[PersonalIdentityProfile, ...]:
    by_id = {item.profile_id.casefold(): item for item in existing}
    carlos = by_id.get("carlos") or PersonalIdentityProfile(
        "carlos", "Carlos", "Carlos"
    )
    spouse = by_id.get("cristina") or by_id.get("spouse")
    cristina_name = "Cristina"
    if spouse is not None and spouse.owner.strip().casefold() not in {
        "esposa",
        "spouse",
    }:
        cristina_name = spouse.owner.strip()
    cristina = PersonalIdentityProfile("cristina", cristina_name, cristina_name)
    coowners = PersonalIdentityProfile(
        COOWNER_PROFILE_ID,
        COOWNER_PRINCIPAL,
        COOWNER_PRINCIPAL,
        scope=IdentityScope.SHARED,
        participants=(carlos.owner, cristina.owner),
    )
    extras = tuple(
        item
        for item in existing
        if item.scope is IdentityScope.PRIVATE
        and item.profile_id.casefold() not in {"carlos", "spouse", "cristina"}
    )
    return (carlos, cristina, coowners, *extras)


def _migrate_runtime_state(
    *, target: Path, base_path: Path, project_root: Path
) -> Path | None:
    if target.exists():
        return None
    candidates = [project_root / ".roby" / "runtime_state.json"]
    profiles_root = base_path / "profiles"
    if profiles_root.exists():
        candidates.extend(profiles_root.glob("*/sessions/*/runtime_state.json"))
    existing = [item for item in candidates if item.exists() and item != target]
    if not existing:
        return None
    source = max(existing, key=lambda item: item.stat().st_mtime_ns)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return source


def _write_manifest(
    base_path: Path,
    profile: PersonalIdentityProfile,
    session: RuntimeSessionProfile,
    migrated: int,
    migrated_from: Path | None,
) -> None:
    path = base_path / "household_bootstrap.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "M385.4",
        "profile_id": profile.profile_id,
        "session_id": session.session_id,
        "coowners": list(profile.participants),
        "participants": list(profile.participants),
        "migrated_sessions": migrated,
        "migrated_state_from": str(migrated_from) if migrated_from else None,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
