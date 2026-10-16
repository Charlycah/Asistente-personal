from __future__ import annotations

import os
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LocalIdentityProfile:
    """Perfil humano local, separado de credenciales y lógica cognitiva."""

    owner_name: str
    partner_name: str
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("unsupported local identity profile schema")
        if not self.owner_name.strip():
            raise ValueError("owner name must not be empty")
        if not self.partner_name.strip():
            raise ValueError("partner name must not be empty")

    @property
    def recognized_names(self) -> tuple[str, str]:
        return (self.owner_name, self.partner_name)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "people": {
                "owner_name": self.owner_name,
                "partner_name": self.partner_name,
            },
        }


class LocalIdentityProfileStore:
    """Persistencia TOML atómica para identidad local no secreta."""

    ENV_PATH = "ROBY_PROFILE_PATH"

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or self.default_path()

    @classmethod
    def default_path(cls) -> Path:
        configured = os.getenv(cls.ENV_PATH)
        if configured:
            return Path(configured).expanduser()
        project_profile = Path.cwd() / ".roby" / "profile.toml"
        if project_profile.exists():
            return project_profile
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "ROBY" / "profile.toml"
        return Path.home() / ".config" / "roby" / "profile.toml"

    def load(self) -> LocalIdentityProfile | None:
        if not self.path.exists():
            return None
        with self.path.open("rb") as stream:
            payload = tomllib.load(stream)
        people = payload.get("people", {})
        return LocalIdentityProfile(
            schema_version=int(payload.get("schema_version", 1)),
            owner_name=str(people.get("owner_name", "")),
            partner_name=str(people.get("partner_name", "")),
        )

    def save(self, profile: LocalIdentityProfile) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        content = self._serialize(profile)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="profile-",
            suffix=".toml.tmp",
            dir=self.path.parent,
            text=True,
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, self.path)
        finally:
            temporary_path.unlink(missing_ok=True)
        return self.path

    def delete(self) -> bool:
        if not self.path.exists():
            return False
        self.path.unlink()
        return True

    @staticmethod
    def _serialize(profile: LocalIdentityProfile) -> str:
        owner = LocalIdentityProfileStore._quote(profile.owner_name)
        partner = LocalIdentityProfileStore._quote(profile.partner_name)
        return (
            f"schema_version = {profile.schema_version}\n\n"
            "[people]\n"
            f'owner_name = "{owner}"\n'
            f'partner_name = "{partner}"\n'
        )

    @staticmethod
    def _quote(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')
