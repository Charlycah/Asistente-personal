from pathlib import Path

import pytest

from core.identity import ROBYIdentityRegistry
from core.local_identity_profile import (
    LocalIdentityProfile,
    LocalIdentityProfileStore,
)


def test_profile_exposes_carlos_and_cristi() -> None:
    profile = LocalIdentityProfile(owner_name="CARLOS", partner_name="CRISTI")

    assert profile.recognized_names == ("CARLOS", "CRISTI")
    assert profile.to_dict()["people"] == {
        "owner_name": "CARLOS",
        "partner_name": "CRISTI",
    }


def test_profile_rejects_blank_names() -> None:
    with pytest.raises(ValueError):
        LocalIdentityProfile(owner_name="", partner_name="CRISTI")


def test_store_round_trip(tmp_path: Path) -> None:
    store = LocalIdentityProfileStore(tmp_path / "profile.toml")
    expected = LocalIdentityProfile(owner_name="CARLOS", partner_name="CRISTI")

    saved_path = store.save(expected)

    assert saved_path == store.path
    assert store.load() == expected


def test_store_replaces_existing_profile(tmp_path: Path) -> None:
    store = LocalIdentityProfileStore(tmp_path / "profile.toml")
    store.save(LocalIdentityProfile(owner_name="Carlos", partner_name="Cristina"))

    store.save(LocalIdentityProfile(owner_name="CARLOS", partner_name="CRISTI"))

    assert store.load() == LocalIdentityProfile(
        owner_name="CARLOS",
        partner_name="CRISTI",
    )


def test_store_delete_is_idempotent(tmp_path: Path) -> None:
    store = LocalIdentityProfileStore(tmp_path / "profile.toml")
    store.save(LocalIdentityProfile(owner_name="CARLOS", partner_name="CRISTI"))

    assert store.delete() is True
    assert store.delete() is False


def test_default_path_accepts_environment_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = tmp_path / "custom-profile.toml"
    monkeypatch.setenv(LocalIdentityProfileStore.ENV_PATH, str(expected))

    assert LocalIdentityProfileStore.default_path() == expected


def test_identity_registry_loads_profile_names(tmp_path: Path) -> None:
    store = LocalIdentityProfileStore(tmp_path / "profile.toml")
    store.save(LocalIdentityProfile(owner_name="CARLOS", partner_name="CRISTI"))

    identity = ROBYIdentityRegistry.from_local_profile(
        profile_store=store
    ).identity

    assert identity.member_names == ("CARLOS", "CRISTI")
    assert identity.family_name == "Hogar de CARLOS y CRISTI"


def test_identity_registry_keeps_defaults_without_profile(tmp_path: Path) -> None:
    store = LocalIdentityProfileStore(tmp_path / "missing.toml")

    identity = ROBYIdentityRegistry(profile_store=store).identity

    assert identity.member_names == ("Carlos", "Cristina")
