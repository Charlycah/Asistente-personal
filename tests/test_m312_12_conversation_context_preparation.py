from __future__ import annotations

import json
from pathlib import Path

from application.brain import (
    ActiveIdentityRequest,
    ActiveIdentityResolver,
    BrainService,
    ConversationContextPreparer,
    SafePersonalContextService,
)
from core.local_identity_profile import (
    LocalIdentityProfile,
    LocalIdentityProfileStore,
)
from core.personal_identity_and_session_profiles.store import JsonIdentityProfileStore
from domain.brain import BrainMemory, BrainMemoryType
from infrastructure.brain import AtomicJsonBrainRepository


def _context_service(tmp_path: Path) -> SafePersonalContextService:
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
    profile_store = JsonIdentityProfileStore(profile_path)
    service = BrainService(AtomicJsonBrainRepository(tmp_path / "brain"))
    for memory in (
        BrainMemory(
            memory_id="carlos-pref",
            memory_type=BrainMemoryType.PREFERENCE,
            subject="Carlos",
            content="Carlos prefiere respuestas breves.",
        ),
        BrainMemory(
            memory_id="cristina-pref",
            memory_type=BrainMemoryType.PREFERENCE,
            subject="Cristina",
            content="Cristina prefiere recordatorios suaves.",
        ),
        BrainMemory(
            memory_id="family-pref",
            memory_type=BrainMemoryType.PREFERENCE,
            subject="Familia",
            content="Carlos y Cristina comparten el calendario doméstico.",
        ),
    ):
        service.remember(memory)
    resolver = ActiveIdentityResolver(
        local_profile_store=local_store,
        identity_profile_store=profile_store,
    )
    return SafePersonalContextService(
        brain_service=service,
        identity_resolver=resolver,
        identity_profile_store=profile_store,
    )


def test_m312_12_prepares_carlos_and_shared_context(tmp_path: Path) -> None:
    package = ConversationContextPreparer(_context_service(tmp_path)).prepare(
        identity_request=ActiveIdentityRequest(declared_name="Carlos")
    )

    assert package.identity_status == "resolved"
    assert package.allowed_subjects == ("Carlos", "Familia")
    assert package.private_context_enabled is True
    assert {item.memory_id for item in package.items} == {
        "carlos-pref",
        "family-pref",
    }


def test_m312_12_unknown_identity_never_receives_private_items(
    tmp_path: Path,
) -> None:
    package = ConversationContextPreparer(_context_service(tmp_path)).prepare(
        identity_request=ActiveIdentityRequest(declared_name="Visitante")
    )

    assert package.private_context_enabled is False
    assert [item.memory_id for item in package.items] == ["family-pref"]


def test_m312_12_applies_item_and_character_limits(tmp_path: Path) -> None:
    service = _context_service(tmp_path)
    service.brain_service.remember(
        BrainMemory(
            memory_id="carlos-long",
            memory_type=BrainMemoryType.PROFILE,
            subject="Carlos",
            content="x" * 200,
            importance=1.0,
        )
    )
    package = ConversationContextPreparer(service).prepare(
        identity_request=ActiveIdentityRequest(declared_name="Carlos"),
        max_items=1,
        max_characters=40,
    )

    assert len(package.items) == 1
    assert package.character_count <= 40
    assert len(package.items[0].text) <= 40
    assert package.omitted_count >= 1


def test_m312_12_payload_is_minimal_and_serializable(tmp_path: Path) -> None:
    package = ConversationContextPreparer(_context_service(tmp_path)).prepare(
        identity_request=ActiveIdentityRequest(declared_name="Cristina")
    )

    payload = package.to_dict()
    assert payload["identity"]["subject"] == "Cristina"
    assert "metadata" not in payload["items"][0]
    assert set(payload["items"][0]) == {
        "memory_id",
        "subject",
        "memory_type",
        "text",
        "source",
    }
