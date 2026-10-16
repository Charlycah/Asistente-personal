from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from core.llm_provider import LLMRequest


class MemoryRuntimeScope(str, Enum):
    PRIVATE = "private"
    SHARED = "shared"


@dataclass(frozen=True)
class MemoryRuntimeConfig:
    root_path: Path | str = Path(".roby/memory")
    recall_limit: int = 5
    enable_recall: bool = True
    enable_learning: bool = True
    include_shared: bool = False
    canonical_joint_owner: bool = False
    canonical_owner: str = "Carlos y Cristina"
    canonical_store_filename: str = "coowners.sqlite3"
    accepted_owner_aliases: tuple[str, ...] = (
        "Carlos",
        "Cristina",
        "Carlos y Cristina",
    )
    legacy_store_owners: tuple[str, ...] = ("Carlos", "Cristina")

    def __post_init__(self) -> None:
        object.__setattr__(self, "root_path", Path(self.root_path))
        if self.recall_limit < 1 or self.recall_limit > 20:
            raise ValueError("memory recall limit must be between 1 and 20")
        if not self.canonical_owner.strip():
            raise ValueError("canonical memory owner must not be blank")
        if not self.canonical_store_filename.strip():
            raise ValueError("canonical memory filename must not be blank")
        if Path(self.canonical_store_filename).name != self.canonical_store_filename:
            raise ValueError("canonical memory filename must be a plain filename")
        aliases = tuple(
            dict.fromkeys(item.strip() for item in self.accepted_owner_aliases)
        )
        if not aliases or any(not item for item in aliases):
            raise ValueError("accepted memory owner aliases must not be blank")
        object.__setattr__(self, "accepted_owner_aliases", aliases)
        legacy = tuple(dict.fromkeys(item.strip() for item in self.legacy_store_owners))
        if any(not item for item in legacy):
            raise ValueError("legacy memory owners must not be blank")
        object.__setattr__(self, "legacy_store_owners", legacy)


@dataclass(frozen=True)
class MemoryRuntimeRecalledAntecedentCandidate:
    """Neutral carrier for one item selected by official memory recall."""

    scoped_memory_reference: str
    content_fingerprint: str
    recall_score: float

    def __post_init__(self) -> None:
        if not self.scoped_memory_reference.strip():
            raise ValueError("recalled antecedent reference must not be blank")
        if len(self.content_fingerprint) != 64:
            raise ValueError("recalled antecedent fingerprint must be SHA-256")


@dataclass(frozen=True)
class MemoryRuntimeContext:
    owner: str
    scopes: tuple[MemoryRuntimeScope, ...]
    request: LLMRequest
    recalled_memory_ids: tuple[str, ...] = field(default_factory=tuple)
    recalled_antecedent_candidates: tuple[
        MemoryRuntimeRecalledAntecedentCandidate, ...
    ] = field(default_factory=tuple)
    recalled_count: int = 0
    context_included: bool = False
    rationale: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MemoryRuntimeWriteResult:
    owner: str
    stored_memory_ids: tuple[str, ...]
    stored_count: int
    learning_enabled: bool
    rationale: tuple[str, ...]
