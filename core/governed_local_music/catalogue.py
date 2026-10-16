from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .models import (
    GovernedLocalMusicConfig,
    GovernedMusicCatalogue,
    GovernedMusicEntry,
    GovernedMusicSearchResult,
)


class GovernedLocalMusicCatalogueV1:
    """Read-only, bounded catalogue over one explicitly authorized music root."""

    def __init__(self, config: GovernedLocalMusicConfig) -> None:
        self.config = config
        self._root = self._validate_root(config.root)
        self._root_identity = self._digest(str(self._root).casefold())

    def catalogue(self) -> GovernedMusicCatalogue:
        entries, scanned_count, truncated = self._scan_entries()
        fingerprint = self._catalogue_fingerprint(entries)
        return GovernedMusicCatalogue(
            root_identity=self._root_identity,
            entries=entries,
            truncated=truncated,
            scanned_entry_count=scanned_count,
            catalogue_fingerprint=fingerprint,
        )

    def search(self, query: str, *, max_results: int = 10) -> GovernedMusicSearchResult:
        normalized_query = query.strip().casefold()
        if not normalized_query:
            raise ValueError("music query must not be blank")
        if max_results <= 0:
            raise ValueError("max results must be positive")
        catalogue = self.catalogue()
        ranked = sorted(
            (
                (self._match_rank(entry, normalized_query), entry)
                for entry in catalogue.entries
            ),
            key=lambda item: (item[0], item[1].relative_path.casefold()),
        )
        candidates = tuple(entry for rank, entry in ranked if rank < 99)
        matches = candidates[:max_results]
        return GovernedMusicSearchResult(
            query=query.strip(),
            matches=matches,
            bounded=catalogue.truncated or len(candidates) > len(matches),
            catalogue_fingerprint=catalogue.catalogue_fingerprint,
        )

    def resolve_entry(self, relative_path: Path | str) -> Path:
        candidate_path = Path(relative_path)
        if candidate_path.is_absolute():
            candidate = candidate_path.resolve(strict=False)
        else:
            candidate = (self._root / candidate_path).resolve(strict=False)
        if not self._is_within_root(candidate):
            raise PermissionError("music entry escapes authorized root")
        return candidate

    def _scan_entries(self) -> tuple[tuple[GovernedMusicEntry, ...], int, bool]:
        collected: list[GovernedMusicEntry] = []
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

    def _entry_from_path(self, candidate: Path) -> GovernedMusicEntry | None:
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
        parent = resolved.parent.relative_to(self._root)
        album_hint = None if parent == Path(".") else parent.name
        return GovernedMusicEntry(
            entry_id=entry_id,
            relative_path=relative,
            filename=resolved.name,
            title_hint=resolved.stem,
            album_hint=album_hint,
            suffix=resolved.suffix.casefold(),
            size_bytes=stat.st_size,
            modified_ns=stat.st_mtime_ns,
            source_reference=f"local-music:{self._root_identity}:{relative}",
            fingerprint=entry_id,
        )

    def _catalogue_fingerprint(
        self,
        entries: tuple[GovernedMusicEntry, ...],
    ) -> str:
        payload = "|".join((self._root_identity, *(item.entry_id for item in entries)))
        return self._digest(payload)

    @staticmethod
    def _match_rank(entry: GovernedMusicEntry, query: str) -> int:
        filename = entry.filename.casefold()
        title = entry.title_hint.casefold()
        path = entry.relative_path.casefold()
        album = (entry.album_hint or "").casefold()
        if filename == query or title == query:
            return 0
        if filename.startswith(query) or title.startswith(query):
            return 1
        tokens = tuple(item for item in query.split() if item)
        if tokens and all(item in path for item in tokens):
            return 2
        if query in album or query in path:
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
            raise ValueError("music root does not exist")
        if not resolved.is_dir():
            raise ValueError("music root must be a directory")
        return resolved

    @staticmethod
    def _digest(payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
