from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GovernedLocalMusicConfig:
    root: Path
    max_catalogue_entries: int = 20_000
    allowed_suffixes: tuple[str, ...] = (
        ".aac",
        ".aiff",
        ".flac",
        ".m4a",
        ".mp3",
        ".ogg",
        ".opus",
        ".wav",
        ".wma",
    )
    follow_symlinks: bool = False

    def __post_init__(self) -> None:
        root = Path(self.root)
        if self.max_catalogue_entries <= 0:
            raise ValueError("max catalogue entries must be positive")
        suffixes = tuple(self._normalize_suffix(item) for item in self.allowed_suffixes)
        if not suffixes:
            raise ValueError("allowed suffixes must not be empty")
        if len(suffixes) != len(set(suffixes)):
            raise ValueError("allowed suffixes must be unique")
        object.__setattr__(self, "root", root)
        object.__setattr__(self, "allowed_suffixes", suffixes)

    @staticmethod
    def _normalize_suffix(value: str) -> str:
        suffix = value.strip().casefold()
        if not suffix:
            raise ValueError("allowed suffix must not be blank")
        if not suffix.startswith("."):
            suffix = f".{suffix}"
        return suffix


@dataclass(frozen=True)
class GovernedMusicEntry:
    entry_id: str
    relative_path: str
    filename: str
    title_hint: str
    album_hint: str | None
    suffix: str
    size_bytes: int
    modified_ns: int
    source_reference: str
    fingerprint: str


@dataclass(frozen=True)
class GovernedMusicCatalogue:
    root_identity: str
    entries: tuple[GovernedMusicEntry, ...]
    truncated: bool
    scanned_entry_count: int
    catalogue_fingerprint: str


@dataclass(frozen=True)
class GovernedMusicSearchResult:
    query: str
    matches: tuple[GovernedMusicEntry, ...]
    bounded: bool
    catalogue_fingerprint: str
