from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from app.document_reading import DocumentReadingService
from core.document_inbox import DocumentInboxManager, DocumentRecord

_SUPPORTED_SUFFIXES = frozenset(
    {
        ".txt",
        ".md",
        ".csv",
        ".json",
        ".html",
        ".htm",
        ".docx",
        ".pdf",
        ".epub",
    }
)


@dataclass(frozen=True)
class PersonalDocumentSourceCandidate:
    candidate_id: str
    relative_path: str
    source_reference: str
    suffix: str
    size_bytes: int
    modified_ns: int


@dataclass(frozen=True)
class PersonalDocumentDiscovery:
    candidates: tuple[PersonalDocumentSourceCandidate, ...]
    truncated: bool


class PersonalDocumentRootDiscoveryAdapter:
    """Discover governed Personal Document sources for explicit Inbox ingestion."""

    def __init__(
        self,
        *,
        root: Path,
        max_candidates: int = 100,
        reader: DocumentReadingService,
        document_inbox: DocumentInboxManager,
    ) -> None:
        if max_candidates <= 0:
            raise ValueError("personal document candidate limit must be positive")
        self.root = Path(root).expanduser().resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("personal documents root must be a directory")
        self.max_candidates = max_candidates
        self.reader = reader
        self.document_inbox = document_inbox
        self._last_discovery: dict[str, PersonalDocumentSourceCandidate] = {}

    def discover(self) -> PersonalDocumentDiscovery:
        candidates = [
            candidate
            for path in self.root.rglob("*")
            if (candidate := self._candidate_for(path)) is not None
        ]
        candidates.sort(key=lambda item: item.relative_path)
        truncated = len(candidates) > self.max_candidates
        visible = tuple(candidates[: self.max_candidates])
        self._last_discovery = {
            item.candidate_id: item
            for item in visible
        }
        return PersonalDocumentDiscovery(
            candidates=visible,
            truncated=truncated,
        )

    def ingest_selected(self, candidate_id: str) -> DocumentRecord:
        candidate = self._last_discovery.get(candidate_id)
        if candidate is None:
            raise KeyError(candidate_id)
        source = self._validated_source(candidate.relative_path)
        refreshed = self._candidate_for(source)
        if refreshed is None or refreshed.candidate_id != candidate.candidate_id:
            raise ValueError("selected personal document source changed")
        content = self.reader.read_text(source)
        media_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
        return self.document_inbox.ingest_text(
            content,
            title=source.stem,
            source_name=candidate.source_reference,
            media_type=media_type,
        )

    def _candidate_for(
        self,
        path: Path,
    ) -> PersonalDocumentSourceCandidate | None:
        if path.is_symlink() or not path.is_file():
            return None
        try:
            resolved = path.resolve(strict=True)
            relative = resolved.relative_to(self.root)
        except (OSError, ValueError):
            return None
        suffix = resolved.suffix.casefold()
        if suffix not in _SUPPORTED_SUFFIXES:
            return None
        stat = resolved.stat()
        relative_path = relative.as_posix()
        identity = self._candidate_identity(
            relative_path,
            stat.st_size,
            stat.st_mtime_ns,
        )
        return PersonalDocumentSourceCandidate(
            candidate_id=identity,
            relative_path=relative_path,
            source_reference=f"personal-document:{identity}:{relative_path}",
            suffix=suffix,
            size_bytes=stat.st_size,
            modified_ns=stat.st_mtime_ns,
        )

    def _validated_source(self, relative_path: str) -> Path:
        candidate = self.root / Path(relative_path)
        if candidate.is_symlink():
            raise ValueError(
                "personal document source symlinks are not allowed"
            )
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(
                "personal document source escapes authorized root"
            ) from exc
        if not resolved.is_file():
            raise ValueError("personal document source must be a file")
        if resolved.suffix.casefold() not in _SUPPORTED_SUFFIXES:
            raise ValueError("unsupported personal document source format")
        return resolved

    def _candidate_identity(
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


def build_personal_document_source_from_environment(
    *,
    document_inbox: DocumentInboxManager,
    reader: DocumentReadingService,
    max_candidates: int = 100,
) -> PersonalDocumentRootDiscoveryAdapter | None:
    raw_root = os.getenv("ROBY_PERSONAL_DOCUMENTS_ROOT", "").strip()
    if not raw_root:
        return None
    return PersonalDocumentRootDiscoveryAdapter(
        root=Path(raw_root),
        max_candidates=max_candidates,
        reader=reader,
        document_inbox=document_inbox,
    )
