from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from domain.brain import BrainMemory


class AtomicJsonBrainRepository:
    """Small, auditable persistence layer for M312.1.

    It is intentionally not wired into the runtime yet.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.memories_path = self.root / "memories.json"

    def load_all(self) -> tuple[BrainMemory, ...]:
        if not self.memories_path.exists():
            return ()
        payload = json.loads(self.memories_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("brain memory store must contain a JSON list")
        return tuple(BrainMemory.from_dict(item) for item in payload)

    def save_all(self, memories: tuple[BrainMemory, ...]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        serialized = [memory.to_dict() for memory in memories]
        fd, temporary_name = tempfile.mkstemp(
            prefix="memories-", suffix=".tmp", dir=self.root
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(serialized, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self.memories_path)
        finally:
            temporary_path.unlink(missing_ok=True)
