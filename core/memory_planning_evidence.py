from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from core.cognitive_memory_recall import CognitiveMemoryRecallItem

METADATA_KEY = "governed_memory_planning_evidence"


@dataclass(frozen=True)
class MemoryPlanningEvidence:
    """Bounded recalled-memory evidence available to canonical planning."""

    memory_id: str
    owner: str
    scope: str
    content: str
    category: str
    confidence: float
    recall_score: float
    provenance: str
    read_only: bool = True
    creates_goals: bool = False
    executes_actions: bool = False
    writes_memory: bool = False

    def __post_init__(self) -> None:
        if not self.memory_id.strip() or not self.owner.strip():
            raise ValueError("memory planning evidence identity is required")
        if not self.provenance.strip():
            raise ValueError("memory planning evidence provenance is required")
        if any((self.creates_goals, self.executes_actions, self.writes_memory)):
            raise ValueError("memory planning evidence violates governed limits")


def project_recalled_memory(
    *,
    owner: str,
    items: tuple[CognitiveMemoryRecallItem, ...],
    scoped_ids: tuple[str, ...],
) -> tuple[MemoryPlanningEvidence, ...]:
    """Project only memories already selected by the official recall path."""

    evidence = []
    for item, scoped_id in zip(items, scoped_ids, strict=False):
        scope, _, raw_id = scoped_id.partition(":")
        memory = item.memory
        provenance = memory.reason.strip()
        if not scope or not raw_id or not provenance:
            continue
        evidence.append(
            MemoryPlanningEvidence(
                memory_id=scoped_id,
                owner=owner,
                scope=scope,
                content=memory.content,
                category=memory.category.value,
                confidence=memory.confidence,
                recall_score=item.score,
                provenance=provenance,
            )
        )
    return tuple(evidence)


def encode_memory_planning_evidence(
    evidence: tuple[MemoryPlanningEvidence, ...],
) -> str:
    return json.dumps(
        [asdict(item) for item in evidence],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def decode_memory_planning_evidence(
    request_metadata: dict[str, str],
    *,
    owner: str,
) -> tuple[MemoryPlanningEvidence, ...]:
    raw = request_metadata.get(METADATA_KEY, "")
    if not raw:
        return ()
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return ()
    if not isinstance(payload, list):
        return ()
    evidence = []
    for value in payload:
        if not isinstance(value, dict):
            continue
        try:
            item = MemoryPlanningEvidence(**value)
        except (TypeError, ValueError):
            continue
        if item.owner.casefold() != owner.casefold():
            continue
        evidence.append(item)
    return tuple(evidence)
