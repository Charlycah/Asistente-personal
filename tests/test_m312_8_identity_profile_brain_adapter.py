from __future__ import annotations

import json
from pathlib import Path

from application.brain import BrainQuery, IdentityProfileBrainAdapter
from core.local_identity_profile import (
    LocalIdentityProfile,
    LocalIdentityProfileStore,
)
from core.personal_identity_and_session_profiles.store import JsonIdentityProfileStore
from domain.brain import BrainMemoryType


def _adapter(tmp_path: Path) -> IdentityProfileBrainAdapter:
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
                        "profile_id": "spouse",
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
    return IdentityProfileBrainAdapter(
        local_profile_store=local_store,
        identity_profile_store=JsonIdentityProfileStore(profile_path),
    )


def test_adapter_recognizes_carlos_and_cristina(tmp_path: Path) -> None:
    memories = _adapter(tmp_path).recall(BrainQuery())

    subjects = {memory.subject for memory in memories}
    assert {"Carlos", "Cristina", "Familia"} <= subjects
    assert all(
        memory.normalized_type is BrainMemoryType.PROFILE
        for memory in memories
    )


def test_adapter_preserves_shared_household_profile(tmp_path: Path) -> None:
    memories = _adapter(tmp_path).recall(BrainQuery())

    shared = next(
        memory
        for memory in memories
        if memory.memory_id == "identity-profile:family-shared"
    )
    assert shared.metadata["participants"] == ["Carlos", "Cristina"]
    assert shared.metadata["scope"] == "shared"
    assert shared.metadata["read_only"] is True


def test_adapter_does_not_modify_identity_files(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    local_path = tmp_path / "profile.toml"
    profiles_path = tmp_path / "identity" / "profiles.json"
    before = (local_path.read_bytes(), profiles_path.read_bytes())

    adapter.recall(BrainQuery(text="Cristina"))

    assert (local_path.read_bytes(), profiles_path.read_bytes()) == before


def test_project_profile_names_are_carlos_and_cristina() -> None:
    profile = LocalIdentityProfileStore(Path(".roby/profile.toml")).load()

    assert profile is not None
    assert profile.recognized_names == ("Carlos", "Cristina")
