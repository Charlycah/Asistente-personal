from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path

from app.document_reading import DocumentReadingService
from core.document_inbox import DocumentInboxManager, DocumentRecord

HISTORICAL_TRUST = "HISTORICAL_DEVELOPMENT_MATERIAL"
_DIRECT_SUFFIXES = frozenset({
    ".py", ".pyi", ".md", ".txt", ".json", ".toml", ".yaml", ".yml",
    ".ini", ".cfg", ".csv", ".html", ".htm",
})
_OPAQUE_SUFFIXES = frozenset({".zip"})
_EXCLUDED_PARTS = frozenset({
    ".git", ".pytest_cache", ".ruff_cache", "__pycache__", ".venv", "venv",
})
_SENSITIVE_NAMES = frozenset(
    {".env", "credentials.json", "api_token.txt", "secret.json"}
)


class HistoricalSourceKind(str, Enum):
    DIRECT_READABLE = "direct_readable"
    OPAQUE = "opaque"


class HistoricalCandidateKind(str, Enum):
    DIRECT = "direct"
    OPAQUE_ARCHIVE = "opaque_archive"


@dataclass(frozen=True)
class DevelopmentHistorySourceCandidate:
    candidate_id: str
    relative_path: str
    source_reference: str
    suffix: str
    size_bytes: int
    modified_ns: int
    source_kind: HistoricalSourceKind
    trust_classification: str = HISTORICAL_TRUST
    current_truth: bool = False

    @property
    def kind(self) -> HistoricalCandidateKind:
        if self.source_kind is HistoricalSourceKind.OPAQUE:
            return HistoricalCandidateKind.OPAQUE_ARCHIVE
        return HistoricalCandidateKind.DIRECT

    @property
    def snapshot_segment(self) -> str:
        return self.relative_path.split("/", 1)[0]


@dataclass(frozen=True)
class DevelopmentHistoryDiscovery:
    candidates: tuple[DevelopmentHistorySourceCandidate, ...]
    truncated: bool


@dataclass(frozen=True)
class DevelopmentHistoryObservation:
    candidate: DevelopmentHistorySourceCandidate
    candidate_id: str
    relative_path: str
    text: str
    trust_class: str = "historical"
    current_truth: bool = False


class DevelopmentHistorySourceAdapter:
    """Single read-only authority for governed ROBY development history."""

    def __init__(
        self,
        *,
        root: Path,
        max_candidates: int = 100,
        max_read_bytes: int = 262_144,
        max_read_chars: int = 262_144,
        reader: DocumentReadingService | None = None,
        document_inbox: DocumentInboxManager | None = None,
    ) -> None:
        if min(max_candidates, max_read_bytes, max_read_chars) <= 0:
            raise ValueError("development history limits must be positive")
        self.root = Path(root).expanduser().resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("development history root must be a directory")
        self.max_candidates = max_candidates
        self.max_read_bytes = max_read_bytes
        self.max_read_chars = max_read_chars
        self.reader = reader
        self.document_inbox = document_inbox
        self._last_discovery: dict[str, DevelopmentHistorySourceCandidate] = {}

    def discover(self) -> DevelopmentHistoryDiscovery:
        candidates = [
            item for path in self.root.rglob("*")
            if (item := self._candidate_for(path)) is not None
        ]
        candidates.sort(
            key=lambda item: (
                item.source_kind is HistoricalSourceKind.OPAQUE,
                item.relative_path,
            )
        )
        truncated = len(candidates) > self.max_candidates
        visible = tuple(candidates[: self.max_candidates])
        self._last_discovery = {item.candidate_id: item for item in visible}
        return DevelopmentHistoryDiscovery(visible, truncated)

    def read_selected(self, candidate_id: str) -> DevelopmentHistoryObservation:
        candidate = self._selected(candidate_id)
        if candidate.source_kind is HistoricalSourceKind.OPAQUE:
            raise ValueError("opaque development history source cannot be read")
        source = self._validated_source(candidate.relative_path)
        if source.stat().st_size > self.max_read_bytes:
            raise ValueError("development history source exceeds read limit")
        text = source.read_text(encoding="utf-8")
        if len(text) > self.max_read_chars:
            raise ValueError("development history source exceeds character limit")
        return DevelopmentHistoryObservation(
            candidate,
            candidate.candidate_id,
            candidate.relative_path,
            text,
        )

    def ingest_selected(self, candidate_id: str) -> DocumentRecord:
        if self.reader is None or self.document_inbox is None:
            raise RuntimeError("document ingestion dependencies are not configured")
        candidate = self._selected(candidate_id)
        if candidate.source_kind is HistoricalSourceKind.OPAQUE:
            raise ValueError("opaque development history source cannot be read")
        source = self._validated_source(candidate.relative_path)
        refreshed = self._candidate_for(source)
        if refreshed is None or refreshed.candidate_id != candidate.candidate_id:
            raise ValueError("selected development history source changed")
        content = self.reader.read_text(source)
        media_type = mimetypes.guess_type(source.name)[0] or "text/plain"
        return self.document_inbox.ingest_text(
            content,
            title=source.stem,
            source_name=candidate.source_reference,
            media_type=media_type,
        )

    def _selected(self, candidate_id: str) -> DevelopmentHistorySourceCandidate:
        candidate = self._last_discovery.get(candidate_id)
        if candidate is None:
            raise KeyError(candidate_id)
        refreshed = self._candidate_for(self.root / candidate.relative_path)
        if refreshed is None or refreshed.candidate_id != candidate.candidate_id:
            raise ValueError("selected development history source changed")
        return candidate

    def _candidate_for(self, path: Path) -> DevelopmentHistorySourceCandidate | None:
        if path.is_symlink() or not path.is_file():
            return None
        try:
            resolved = path.resolve(strict=True)
            relative = resolved.relative_to(self.root)
        except (OSError, ValueError):
            return None
        if any(part.casefold() in _EXCLUDED_PARTS for part in relative.parts):
            return None
        if resolved.name.casefold() in _SENSITIVE_NAMES:
            return None
        suffix = resolved.suffix.casefold()
        if suffix in _DIRECT_SUFFIXES:
            kind = HistoricalSourceKind.DIRECT_READABLE
        elif suffix in _OPAQUE_SUFFIXES:
            kind = HistoricalSourceKind.OPAQUE
        else:
            return None
        stat = resolved.stat()
        relative_path = relative.as_posix()
        identity = self._identity(relative_path, stat.st_size, stat.st_mtime_ns)
        return DevelopmentHistorySourceCandidate(
            identity,
            relative_path,
            f"development-history:{identity}:{relative_path}",
            suffix,
            stat.st_size,
            stat.st_mtime_ns,
            kind,
        )

    def _validated_source(self, relative_path: str) -> Path:
        candidate = self.root / Path(relative_path)
        if candidate.is_symlink():
            raise ValueError("development history source symlinks are not allowed")
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(
                "development history source escapes authorized root"
            ) from exc
        if (
            not resolved.is_file()
            or resolved.suffix.casefold() not in _DIRECT_SUFFIXES
        ):
            raise ValueError("unsupported development history source format")
        return resolved

    def _identity(
        self,
        relative_path: str,
        size_bytes: int,
        modified_ns: int,
    ) -> str:
        payload = (
            f"{self.root.as_posix()}\0{relative_path}\0"
            f"{size_bytes}\0{modified_ns}"
        )
        return sha256(payload.encode("utf-8")).hexdigest()


DevelopmentHistoryRootDiscoveryAdapter = DevelopmentHistorySourceAdapter


def build_development_history_source_from_environment(
    *,
    document_inbox: DocumentInboxManager | None = None,
    reader: DocumentReadingService | None = None,
    max_candidates: int = 100,
    max_read_bytes: int = 262_144,
    max_read_chars: int = 262_144,
) -> DevelopmentHistorySourceAdapter | None:
    raw_root = os.getenv("ROBY_DEVELOPMENT_HISTORY_ROOT", "").strip()
    if not raw_root:
        return None
    return DevelopmentHistorySourceAdapter(
        root=Path(raw_root),
        max_candidates=max_candidates,
        max_read_bytes=max_read_bytes,
        max_read_chars=max_read_chars,
        reader=reader,
        document_inbox=document_inbox,
    )
