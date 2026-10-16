from __future__ import annotations

import json
from pathlib import Path

from application.brain import (
    ActiveIdentityRequest,
    ActiveIdentityResolver,
    ActiveIdentitySource,
    ActiveIdentityStatus,
)
from core.local_identity_profile import (
    LocalIdentityProfile,
    LocalIdentityProfileStore,
)
from core.personal_identity_and_session_profiles.store import JsonIdentityProfileStore


def _resolver(tmp_path: Path) -> ActiveIdentityResolver:
    local_store = LocalIdentityProfileStore(tmp_path / "profile.toml")
    local_store.save(
        LocalIdentityProfile(owner_name="Carlos", partner_name="Cristina")
    )
    profile_path = tmp_path / "identity" / "profiles.json"
    profile_path.parent.mkdir(parents=True)
    profile_path.write_text(
        json.dumps(
            {
                "profiles": [
                    {
                        "profile_id": "carlos",
                        "display_name": "Carlos",
                        "owner": "Carlos",
                        "scope": "private",
                        "participants": [],
                    },
                    {
                        "profile_id": "cristina",
                        "display_name": "Cristina",
                        "owner": "Cristina",
                        "scope": "private",
                        "participants": [],
                    },
                    {
                        "profile_id": "family-shared",
                        "display_name": "Familia",
                        "owner": "Familia",
                        "scope": "shared",
                        "participants": ["Carlos", "Cristina"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    return ActiveIdentityResolver(
        local_profile_store=local_store,
        identity_profile_store=JsonIdentityProfileStore(profile_path),
    )


def test_declared_name_resolves_carlos_without_biometrics(tmp_path: Path) -> None:
    result = _resolver(tmp_path).resolve(
        ActiveIdentityRequest(declared_name="Carlos")
    )

    assert result.status is ActiveIdentityStatus.RESOLVED
    assert result.source is ActiveIdentitySource.DECLARED_NAME
    assert result.subject == "Carlos"
    assert result.may_use_private_preferences is True


def test_explicit_shared_profile_never_unlocks_private_preferences(
    tmp_path: Path,
) -> None:
    result = _resolver(tmp_path).resolve(
        ActiveIdentityRequest(profile_id="family-shared")
    )

    assert result.status is ActiveIdentityStatus.SHARED
    assert result.participants == ("Carlos", "Cristina")
    assert result.may_use_private_preferences is False


def test_unknown_speaker_stays_unknown(tmp_path: Path) -> None:
    result = _resolver(tmp_path).resolve(
        ActiveIdentityRequest(declared_name="Visitante")
    )

    assert result.status is ActiveIdentityStatus.UNKNOWN
    assert result.profile_id is None
    assert result.confidence == 0.0


def test_conflicting_evidence_is_not_guessed(tmp_path: Path) -> None:
    result = _resolver(tmp_path).resolve(
        ActiveIdentityRequest(
            profile_id="carlos",
            declared_name="Cristina",
        )
    )

    assert result.status is ActiveIdentityStatus.CONFLICT
    assert result.may_use_private_preferences is False
