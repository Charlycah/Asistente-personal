from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GovernedLocalLibraryConfig:
    root: Path
    max_catalogue_entries: int = 10_000
    allowed_suffixes: tuple[str, ...] = (".txt", ".md", ".pdf", ".docx", ".epub")
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
class GovernedLibraryEntry:
    entry_id: str
    relative_path: str
    filename: str
    suffix: str
    size_bytes: int
    modified_ns: int
    source_reference: str
    fingerprint: str


@dataclass(frozen=True)
class GovernedLibraryCatalogue:
    root_identity: str
    entries: tuple[GovernedLibraryEntry, ...]
    truncated: bool
    scanned_entry_count: int
    catalogue_fingerprint: str


@dataclass(frozen=True)
class GovernedLibrarySearchResult:
    query: str
    matches: tuple[GovernedLibraryEntry, ...]
    bounded: bool
    catalogue_fingerprint: str
    catalogue_scan_elapsed_ms: float = 0.0
    matching_elapsed_ms: float = 0.0
