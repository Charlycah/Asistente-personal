from __future__ import annotations

import hashlib
import os
from pathlib import Path
from time import perf_counter

from .models import (
    GovernedLibraryCatalogue,
    GovernedLibraryEntry,
    GovernedLibrarySearchResult,
    GovernedLocalLibraryConfig,
)


class GovernedLocalLibraryCatalogueV1:
    """Read-only, bounded catalogue over one explicitly authorized local root."""

    def __init__(self, config: GovernedLocalLibraryConfig) -> None:
        self.config = config
        self._root = self._validate_root(config.root)
        self._root_identity = self._digest(str(self._root).casefold())

    def catalogue(self) -> GovernedLibraryCatalogue:
        entries, scanned_count, truncated = self._scan_entries()
        fingerprint = self._catalogue_fingerprint(entries)
        return GovernedLibraryCatalogue(
            root_identity=self._root_identity,
            entries=entries,
            truncated=truncated,
            scanned_entry_count=scanned_count,
            catalogue_fingerprint=fingerprint,
        )

    def search(self, query: str, *, max_results: int) -> GovernedLibrarySearchResult:
        normalized_query = query.strip().casefold()
        if not normalized_query:
            raise ValueError("library query must not be blank")
        if max_results <= 0:
            raise ValueError("max results must be positive")
        scan_started = perf_counter()
        catalogue = self.catalogue()
        catalogue_scan_elapsed_ms = max(0.0, (perf_counter() - scan_started) * 1000)
        matching_started = perf_counter()
        ranked = sorted(
            (
                (self._match_rank(entry, normalized_query), entry)
                for entry in catalogue.entries
            ),
            key=lambda item: (item[0], item[1].relative_path.casefold()),
        )
        candidates = tuple(entry for rank, entry in ranked if rank < 99)
        matches = candidates[:max_results]
        matching_elapsed_ms = max(0.0, (perf_counter() - matching_started) * 1000)
        return GovernedLibrarySearchResult(
            query=query.strip(),
            matches=matches,
            bounded=catalogue.truncated or len(candidates) > len(matches),
            catalogue_fingerprint=catalogue.catalogue_fingerprint,
            catalogue_scan_elapsed_ms=catalogue_scan_elapsed_ms,
            matching_elapsed_ms=matching_elapsed_ms,
        )

    def lookup_explicit_relative_path(self, relative_path: str) -> GovernedLibraryEntry:
        """Resolve an explicit nested library path without enumerating the catalogue."""
        if not isinstance(relative_path, str):
            raise ValueError("explicit library path must be a string")
        raw = relative_path.strip()
        if not raw or "\\" in raw:
            raise ValueError("explicit library path must use relative POSIX separators")
        parts = raw.split("/")
        if len(parts) < 2 or any(part in ("", ".", "..") for part in parts):
            raise ValueError("explicit library path must be nested and unambiguous")
        candidate_path = Path(raw)
        if candidate_path.is_absolute() or candidate_path.drive:
            raise ValueError("explicit library path must be relative")
        if candidate_path.suffix.casefold() not in self.config.allowed_suffixes:
            raise ValueError("library entry suffix is not allowed")

        candidate = self._root
        for part in parts:
            candidate = candidate / part
            if not self.config.follow_symlinks and candidate.is_symlink():
                raise PermissionError("library entry symlink is not allowed")

        resolved = self.resolve_entry(raw)
        entry = self._entry_from_path(resolved)
        if entry is None:
            raise FileNotFoundError("library entry is unavailable")
        if entry.relative_path != raw:
            raise ValueError("explicit library path is not canonical")
        return entry

    def validate_selected_entry(
        self,
        *,
        entry_id: str,
        source_reference: str,
    ) -> GovernedLibraryEntry:
        prefix = f"local-library:{self._root_identity}:"
        if not source_reference.startswith(prefix):
            raise ValueError("library selection provenance does not match catalogue")
        relative_path = source_reference[len(prefix) :]
        if not relative_path:
            raise ValueError("library selection provenance does not match catalogue")
        candidate = self.resolve_entry(relative_path)
        entry = self._entry_from_path(candidate)
        if entry is None or entry.entry_id != entry_id:
            raise ValueError("library selection entry is stale or unavailable")
        if entry.source_reference != source_reference:
            raise ValueError("library selection provenance does not match catalogue")
        return entry

    def resolve_entry(self, relative_path: Path | str) -> Path:
        candidate_path = Path(relative_path)
        if candidate_path.is_absolute():
            candidate = candidate_path.resolve(strict=False)
        else:
            candidate = (self._root / candidate_path).resolve(strict=False)
        if not self._is_within_root(candidate):
            raise PermissionError("library entry escapes authorized root")
        return candidate

    def _scan_entries(self) -> tuple[tuple[GovernedLibraryEntry, ...], int, bool]:
        collected: list[GovernedLibraryEntry] = []
        scanned_count = 0
        truncated = False
        limit = self.config.max_catalogue_entries

        for directory, dirnames, filenames in os.walk(
            self._root,
            followlinks=self.config.follow_symlinks,
        ):
            directory_path = Path(directory)
            dirnames[:] = self._allowed_directories(directory_path, dirnames)
            for filename in sorted(filenames, key=str.casefold):
                candidate = directory_path / filename
                if candidate.suffix.casefold() not in self.config.allowed_suffixes:
                    continue
                scanned_count += 1
                entry = self._entry_from_path(candidate)
                if entry is None:
                    continue
                if len(collected) >= limit:
                    truncated = True
                    break
                collected.append(entry)
            if truncated:
                break

        entries = tuple(
            sorted(collected, key=lambda item: item.relative_path.casefold())
        )
        return entries, scanned_count, truncated

    def _allowed_directories(self, parent: Path, names: list[str]) -> list[str]:
        allowed: list[str] = []
        for name in sorted(names, key=str.casefold):
            candidate = parent / name
            if candidate.is_symlink() and not self.config.follow_symlinks:
                continue
            resolved = candidate.resolve(strict=False)
            if self._is_within_root(resolved):
                allowed.append(name)
        return allowed

    def _entry_from_path(self, candidate: Path) -> GovernedLibraryEntry | None:
        if candidate.is_symlink() and not self.config.follow_symlinks:
            return None
        try:
            resolved = candidate.resolve(strict=True)
            if not self._is_within_root(resolved) or not resolved.is_file():
                return None
            stat = resolved.stat()
        except (FileNotFoundError, OSError, PermissionError):
            return None
        relative = resolved.relative_to(self._root).as_posix()
        identity_payload = "|".join(
            (
                self._root_identity,
                relative.casefold(),
                str(stat.st_size),
                str(stat.st_mtime_ns),
            )
        )
        entry_id = self._digest(identity_payload)
        return GovernedLibraryEntry(
            entry_id=entry_id,
            relative_path=relative,
            filename=resolved.name,
            suffix=resolved.suffix.casefold(),
            size_bytes=stat.st_size,
            modified_ns=stat.st_mtime_ns,
            source_reference=f"local-library:{self._root_identity}:{relative}",
            fingerprint=entry_id,
        )

    def _catalogue_fingerprint(
        self,
        entries: tuple[GovernedLibraryEntry, ...],
    ) -> str:
        payload = "|".join((self._root_identity, *(item.entry_id for item in entries)))
        return self._digest(payload)

    @staticmethod
    def _match_rank(entry: GovernedLibraryEntry, query: str) -> int:
        filename = entry.filename.casefold()
        path = entry.relative_path.casefold()
        stem = Path(entry.filename).stem.casefold()
        if filename == query or stem == query:
            return 0
        if filename.startswith(query) or stem.startswith(query):
            return 1
        tokens = tuple(item for item in query.split() if item)
        if tokens and all(item in path for item in tokens):
            return 2
        if query in path:
            return 3
        return 99

    def _is_within_root(self, candidate: Path) -> bool:
        try:
            candidate.relative_to(self._root)
        except ValueError:
            return False
        return True

    @staticmethod
    def _validate_root(root: Path) -> Path:
        resolved = Path(root).resolve(strict=False)
        if not resolved.exists():
            raise ValueError("library root does not exist")
        if not resolved.is_dir():
            raise ValueError("library root must be a directory")
        return resolved

    @staticmethod
    def _digest(payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
