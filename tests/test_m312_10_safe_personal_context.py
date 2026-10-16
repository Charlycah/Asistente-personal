from __future__ import annotations

import json
from pathlib import Path

from application.brain import (
    ActiveIdentityRequest,
    ActiveIdentityResolver,
    BrainQuery,
    BrainService,
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
    repository = AtomicJsonBrainRepository(tmp_path / "brain")
    service = BrainService(repository)
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


def test_carlos_receives_only_personal_and_shared_context(tmp_path: Path) -> None:
    context = _context_service(tmp_path).build(
        identity_request=ActiveIdentityRequest(declared_name="Carlos")
    )

    assert {memory.memory_id for memory in context.memories} == {
        "carlos-pref",
        "family-pref",
    }
    assert context.allowed_subjects == ("Carlos", "Familia")
    assert context.private_context_enabled is True


def test_cristina_never_receives_carlos_private_context(tmp_path: Path) -> None:
    context = _context_service(tmp_path).build(
        identity_request=ActiveIdentityRequest(declared_name="Cristina")
    )

    assert {memory.memory_id for memory in context.memories} == {
        "cristina-pref",
        "family-pref",
    }
    assert "carlos-pref" not in {
        memory.memory_id for memory in context.memories
    }


def test_unknown_or_conflicting_identity_gets_shared_context_only(
    tmp_path: Path,
) -> None:
    service = _context_service(tmp_path)
    unknown = service.build(
        identity_request=ActiveIdentityRequest(declared_name="Visitante")
    )
    conflict = service.build(
        identity_request=ActiveIdentityRequest(
            profile_id="carlos",
            declared_name="Cristina",
        )
    )

    assert [memory.memory_id for memory in unknown.memories] == ["family-pref"]
    assert [memory.memory_id for memory in conflict.memories] == ["family-pref"]
    assert unknown.private_context_enabled is False
    assert conflict.private_context_enabled is False


def test_requested_private_subject_cannot_bypass_identity_scope(
    tmp_path: Path,
) -> None:
    context = _context_service(tmp_path).build(
        identity_request=ActiveIdentityRequest(declared_name="Cristina"),
        query=BrainQuery(subject="Carlos"),
    )

    assert context.memories == ()
