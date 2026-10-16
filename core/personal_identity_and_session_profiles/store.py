from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from core.platform_runtime_compatibility import apply_private_file_permissions

from .models import PersonalIdentityProfile, RuntimeSessionProfile


@runtime_checkable
class IdentityProfileStore(Protocol):
    def list_profiles(self) -> tuple[PersonalIdentityProfile, ...]: ...
    def save_profiles(self, profiles: tuple[PersonalIdentityProfile, ...]) -> None: ...


@runtime_checkable
class SessionProfileStore(Protocol):
    def list_sessions(self) -> tuple[RuntimeSessionProfile, ...]: ...
    def save_sessions(self, sessions: tuple[RuntimeSessionProfile, ...]) -> None: ...


class JsonIdentityProfileStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def list_profiles(self) -> tuple[PersonalIdentityProfile, ...]:
        if not self.path.exists():
            return ()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return tuple(PersonalIdentityProfile(**item) for item in payload["profiles"])

    def save_profiles(self, profiles: tuple[PersonalIdentityProfile, ...]) -> None:
        self._write(
            {
                "profiles": [
                    {
                        "profile_id": item.profile_id,
                        "display_name": item.display_name,
                        "owner": item.owner,
                        "scope": item.scope.value,
                        "participants": list(item.participants),
                    }
                    for item in profiles
                ]
            }
        )

    def _write(self, payload: dict) -> None:
        _atomic_private_json(self.path, payload)


class JsonSessionProfileStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def list_sessions(self) -> tuple[RuntimeSessionProfile, ...]:
        if not self.path.exists():
            return ()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return tuple(
            RuntimeSessionProfile(
                session_id=item["session_id"],
                profile_id=item["profile_id"],
                status=item["status"],
                created_at=datetime.fromisoformat(item["created_at"]),
                last_active_at=datetime.fromisoformat(item["last_active_at"]),
                archived_at=(
                    datetime.fromisoformat(item["archived_at"])
                    if item.get("archived_at")
                    else None
                ),
            )
            for item in payload["sessions"]
        )

    def save_sessions(self, sessions: tuple[RuntimeSessionProfile, ...]) -> None:
        _atomic_private_json(
            self.path,
            {
                "sessions": [
                    {
                        "session_id": item.session_id,
                        "profile_id": item.profile_id,
                        "status": item.status.value,
                        "created_at": item.created_at.isoformat(),
                        "last_active_at": item.last_active_at.isoformat(),
                        "archived_at": (
                            item.archived_at.isoformat() if item.archived_at else None
                        ),
                    }
                    for item in sessions
                ]
            },
        )


def _atomic_private_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    apply_private_file_permissions(temporary)
    temporary.replace(path)
    apply_private_file_permissions(path)
