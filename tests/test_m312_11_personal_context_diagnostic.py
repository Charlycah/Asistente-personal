from __future__ import annotations

import json
from pathlib import Path

from application.brain import (
    ActiveIdentityRequest,
    ActiveIdentityResolver,
    BrainQuery,
    BrainService,
    PersonalContextDiagnostic,
    SafePersonalContextService,
)
from core.local_identity_profile import (
    LocalIdentityProfile,
    LocalIdentityProfileStore,
)
from core.personal_identity_and_session_profiles.store import JsonIdentityProfileStore
from domain.brain import BrainMemory, BrainMemoryType
from infrastructure.brain import AtomicJsonBrainRepository
from scripts.personal_context_diagnostic import main


def _profile_stores(
    root: Path,
) -> tuple[LocalIdentityProfileStore, JsonIdentityProfileStore]:
    local_store = LocalIdentityProfileStore(root / "profile.toml")
    local_store.save(
        LocalIdentityProfile(owner_name="Carlos", partner_name="Cristina")
    )
    profile_path = root / "identity" / "profiles.json"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
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
    return local_store, JsonIdentityProfileStore(profile_path)


def _diagnostic(tmp_path: Path) -> PersonalContextDiagnostic:
    local_store, profile_store = _profile_stores(tmp_path)
    service = BrainService(AtomicJsonBrainRepository(tmp_path / "brain"))
    for memory in (
        BrainMemory(
            memory_id="carlos-private",
            memory_type=BrainMemoryType.PREFERENCE,
            subject="Carlos",
            content="Carlos prefiere respuestas breves.",
        ),
        BrainMemory(
            memory_id="cristina-private",
            memory_type=BrainMemoryType.PREFERENCE,
            subject="Cristina",
            content="Cristina prefiere recordatorios suaves.",
        ),
        BrainMemory(
            memory_id="family-shared",
            memory_type=BrainMemoryType.PROFILE,
            subject="Familia",
            content="Carlos y Cristina comparten el hogar.",
        ),
    ):
        service.remember(memory)
    resolver = ActiveIdentityResolver(
        local_profile_store=local_store,
        identity_profile_store=profile_store,
    )
    context = SafePersonalContextService(
        brain_service=service,
        identity_resolver=resolver,
        identity_profile_store=profile_store,
    )
    return PersonalContextDiagnostic(context)


def test_m312_11_reports_carlos_personal_and_shared_context(tmp_path: Path) -> None:
    report = _diagnostic(tmp_path).inspect(
        identity_request=ActiveIdentityRequest(declared_name="Carlos")
    )

    assert report.identity_status == "resolved"
    assert report.allowed_subjects == ("Carlos", "Familia")
    assert report.private_context_enabled is True
    assert {entry.memory_id for entry in report.entries} == {
        "carlos-private",
        "family-shared",
    }


def test_m312_11_unknown_identity_reports_shared_context_only(tmp_path: Path) -> None:
    report = _diagnostic(tmp_path).inspect(
        identity_request=ActiveIdentityRequest(declared_name="Visitante")
    )

    assert report.identity_status == "unknown"
    assert report.private_context_enabled is False
    assert [entry.memory_id for entry in report.entries] == ["family-shared"]


def test_m312_11_conflict_is_visible_and_blocks_private_context(
    tmp_path: Path,
) -> None:
    report = _diagnostic(tmp_path).inspect(
        identity_request=ActiveIdentityRequest(
            profile_id="carlos",
            declared_name="Cristina",
        ),
        query=BrainQuery(subject="Carlos"),
    )

    payload = report.to_dict()
    assert payload["identity"]["status"] == "conflict"
    assert payload["access"]["private_context_enabled"] is False
    assert payload["summary"]["total"] == 0


def test_m312_11_cli_prints_json_without_changing_brain(
    tmp_path: Path,
    capsys,
) -> None:
    storage_root = tmp_path / ".roby"
    _profile_stores(storage_root)
    repository = AtomicJsonBrainRepository(storage_root / "brain")
    BrainService(repository).remember(
        BrainMemory(
            memory_id="carlos-cli",
            memory_type=BrainMemoryType.PREFERENCE,
            subject="Carlos",
            content="Preferencia de diagnóstico.",
        )
    )
    before = repository.memories_path.read_bytes()

    result = main(
        [
            "--owner",
            "Carlos",
            "--name",
            "Carlos",
            "--query",
            "diagnóstico",
            "--project-root",
            str(tmp_path),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["identity"]["subject"] == "Carlos"
    assert any(entry["memory_id"] == "carlos-cli" for entry in payload["entries"])
    assert repository.memories_path.read_bytes() == before
