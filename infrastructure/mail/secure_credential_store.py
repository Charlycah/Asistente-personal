from __future__ import annotations

import base64
import json
import os
import re
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Protocol

from infrastructure.system.private_file_permissions import harden_private_path


class CredentialProtector(Protocol):
    """Deployment-specific encryption boundary for credential payloads."""

    @property
    def key_id(self) -> str: ...

    def protect(self, plaintext: bytes) -> bytes: ...

    def unprotect(self, ciphertext: bytes) -> bytes: ...


class SecureCredentialStore(Protocol):
    """Provider-neutral store for encrypted OAuth credential documents."""

    def load(self, account_fingerprint: str) -> dict[str, object] | None: ...

    def save(self, account_fingerprint: str, payload: Mapping[str, object]) -> None: ...

    def delete(self, account_fingerprint: str) -> bool: ...


@dataclass(frozen=True)
class CredentialStoreStatus:
    configured: bool
    records: int
    reads: int
    writes: int
    rotations: int
    deletions: int
    failures: int
    protector_fingerprint: str

    def to_dict(self) -> dict[str, object]:
        return {
            "configured": self.configured,
            "records": self.records,
            "reads": self.reads,
            "writes": self.writes,
            "rotations": self.rotations,
            "deletions": self.deletions,
            "failures": self.failures,
            "protector_fingerprint": self.protector_fingerprint,
        }


class EncryptedFileCredentialStore:
    """Atomic encrypted credential store with restrictive local permissions."""

    _VERSION = 1
    _SAFE_KEY = re.compile(r"^[A-Za-z0-9@_.:-]{1,256}$")

    def __init__(self, root: Path, protector: CredentialProtector) -> None:
        self._root = root
        self._protector = protector
        self._reads = 0
        self._writes = 0
        self._rotations = 0
        self._deletions = 0
        self._failures = 0

    def load(self, account_fingerprint: str) -> dict[str, object] | None:
        path = self._record_path(account_fingerprint)
        self._reads += 1
        if not path.is_file():
            return None
        try:
            envelope = self._read_envelope(path)
            ciphertext = base64.b64decode(envelope["ciphertext"], validate=True)
            plaintext = self._protector.unprotect(ciphertext)
            payload = json.loads(plaintext.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("credential payload must be an object")
            return payload
        except (
            OSError,
            ValueError,
            TypeError,
            UnicodeError,
            json.JSONDecodeError,
        ) as exc:
            self._failures += 1
            raise RuntimeError("secure credential store read failed") from exc

    def save(self, account_fingerprint: str, payload: Mapping[str, object]) -> None:
        if not isinstance(payload, Mapping):
            raise TypeError("credential payload must be a mapping")
        path = self._record_path(account_fingerprint)
        try:
            self._ensure_root()
            plaintext = json.dumps(
                dict(payload), sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            ciphertext = self._protector.protect(plaintext)
            envelope = {
                "version": self._VERSION,
                "key_fingerprint": self._protector_fingerprint(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
            }
            self._atomic_write(path, envelope)
            self._writes += 1
        except (OSError, ValueError, TypeError, UnicodeError) as exc:
            self._failures += 1
            raise RuntimeError("secure credential store write failed") from exc

    def rotate(
        self, account_fingerprint: str, new_protector: CredentialProtector
    ) -> bool:
        payload = self.load(account_fingerprint)
        if payload is None:
            return False
        previous = self._protector
        self._protector = new_protector
        try:
            self.save(account_fingerprint, payload)
        except Exception:
            self._protector = previous
            raise
        self._rotations += 1
        return True

    def delete(self, account_fingerprint: str) -> bool:
        path = self._record_path(account_fingerprint)
        if not path.exists():
            return False
        try:
            path.unlink()
            self._deletions += 1
            return True
        except OSError as exc:
            self._failures += 1
            raise RuntimeError("secure credential store delete failed") from exc

    def status(self) -> dict[str, object]:
        records = 0
        if self._root.is_dir():
            records = sum(1 for path in self._root.glob("*.cred") if path.is_file())
        return CredentialStoreStatus(
            configured=True,
            records=records,
            reads=self._reads,
            writes=self._writes,
            rotations=self._rotations,
            deletions=self._deletions,
            failures=self._failures,
            protector_fingerprint=self._protector_fingerprint(),
        ).to_dict()

    def _record_path(self, account_fingerprint: str) -> Path:
        normalized = account_fingerprint.strip()
        if not normalized or not self._SAFE_KEY.fullmatch(normalized):
            raise ValueError("credential account fingerprint is invalid")
        name = sha256(normalized.encode("utf-8")).hexdigest()
        return self._root / f"{name}.cred"

    def _ensure_root(self) -> None:
        self._root.mkdir(mode=0o700, parents=True, exist_ok=True)
        harden_private_path(self._root, directory=True)

    def _read_envelope(self, path: Path) -> dict[str, object]:
        with path.open("r", encoding="utf-8") as stream:
            envelope = json.load(stream)
        if not isinstance(envelope, dict):
            raise ValueError("credential envelope must be an object")
        if envelope.get("version") != self._VERSION:
            raise ValueError("credential envelope version unsupported")
        if not isinstance(envelope.get("ciphertext"), str):
            raise ValueError("credential envelope ciphertext unavailable")
        return envelope

    def _atomic_write(self, path: Path, envelope: Mapping[str, object]) -> None:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=self._root
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(dict(envelope), stream, sort_keys=True, separators=(",", ":"))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            harden_private_path(path)
        finally:
            if temporary.exists():
                temporary.unlink()

    def _protector_fingerprint(self) -> str:
        key_id = self._protector.key_id.strip()
        if not key_id:
            raise ValueError("credential protector key id must not be blank")
        return sha256(key_id.encode("utf-8")).hexdigest()[:16]
