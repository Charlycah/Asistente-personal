from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Protocol, runtime_checkable
from uuid import uuid4

from .capability_model import CapabilityAssessment
from .next_step_proposal import NextStepProposal


class ContextSignalKind(str, Enum):
    NEXT_STEP_READY = "next_step_ready"
    GOAL_BLOCKED = "goal_blocked"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    AUTHORIZATION_REQUIRED = "authorization_required"
    NO_ACTIONABLE_STEP = "no_actionable_step"


@dataclass(frozen=True, slots=True)
class ContextSignal:
    kind: ContextSignalKind
    summary: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise ValueError("context signal summary must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("context signal confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class ContextualInitiative:
    initiative_id: str
    proposal_id: str
    observed_at: datetime
    should_propose: bool
    confidence: float
    signals: tuple[ContextSignal, ...]
    summary: str

    def __post_init__(self) -> None:
        if not self.initiative_id.strip() or not self.proposal_id.strip():
            raise ValueError("contextual initiative identifiers must not be blank")
        if self.observed_at.tzinfo is None:
            raise ValueError("contextual initiative timestamp must be timezone-aware")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("initiative confidence must be between 0 and 1")
        if not self.signals or not self.summary.strip():
            raise ValueError("contextual initiative evidence must not be blank")


@dataclass(frozen=True, slots=True)
class ContextualInitiativeSnapshot:
    initiatives: tuple[ContextualInitiative, ...]

    @property
    def proposal_candidate_count(self) -> int:
        return sum(item.should_propose for item in self.initiatives)


@runtime_checkable
class ContextualInitiativeEvaluator(Protocol):
    def evaluate(
        self,
        *,
        proposal: NextStepProposal,
        capability: CapabilityAssessment | None,
        observed_at: datetime,
    ) -> ContextualInitiative: ...


class DeterministicContextualInitiativeEvaluator:
    """Evaluates whether context justifies a proposal, never its execution."""

    def evaluate(
        self,
        *,
        proposal: NextStepProposal,
        capability: CapabilityAssessment | None,
        observed_at: datetime,
    ) -> ContextualInitiative:
        if observed_at.tzinfo is None:
            raise ValueError("initiative timestamp must be timezone-aware")
        signals: list[ContextSignal] = []
        if proposal.step_id is None:
            signals.append(
                ContextSignal(
                    ContextSignalKind.NO_ACTIONABLE_STEP,
                    proposal.summary,
                    1.0,
                )
            )
        elif proposal.blockers:
            signals.append(
                ContextSignal(
                    ContextSignalKind.GOAL_BLOCKED,
                    "; ".join(proposal.blockers),
                    1.0,
                )
            )
        elif capability is not None and not capability.available:
            signals.append(
                ContextSignal(
                    ContextSignalKind.CAPABILITY_UNAVAILABLE,
                    "; ".join(capability.reasons),
                    1.0,
                )
            )
        else:
            signals.append(
                ContextSignal(
                    ContextSignalKind.NEXT_STEP_READY,
                    f"Step {proposal.step_id} is ready for user consideration.",
                    0.95,
                )
            )
            if proposal.authorization_required:
                signals.append(
                    ContextSignal(
                        ContextSignalKind.AUTHORIZATION_REQUIRED,
                        "Authorization remains required before execution.",
                        1.0,
                    )
                )
        should_propose = signals[0].kind is ContextSignalKind.NEXT_STEP_READY
        confidence = min(item.confidence for item in signals)
        summary = (
            "Context supports presenting the next step; execution remains separate."
            if should_propose
            else "Context does not support presenting an actionable next step."
        )
        return ContextualInitiative(
            initiative_id=uuid4().hex,
            proposal_id=proposal.proposal_id,
            observed_at=observed_at,
            should_propose=should_propose,
            confidence=confidence,
            signals=tuple(signals),
            summary=summary,
        )


@runtime_checkable
class ContextualInitiativeStore(Protocol):
    def append(self, initiative: ContextualInitiative) -> None: ...

    def snapshot(self) -> ContextualInitiativeSnapshot: ...


class JsonContextualInitiativeStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._initiatives = self._load()

    def append(self, initiative: ContextualInitiative) -> None:
        with self._lock:
            if initiative.initiative_id in self._initiatives:
                raise ValueError(
                    f"duplicate contextual initiative id: {initiative.initiative_id}"
                )
            updated = dict(self._initiatives)
            updated[initiative.initiative_id] = initiative
            self._persist(updated)
            self._initiatives = updated

    def snapshot(self) -> ContextualInitiativeSnapshot:
        with self._lock:
            values = tuple(
                sorted(
                    self._initiatives.values(),
                    key=lambda item: (item.observed_at, item.initiative_id),
                )
            )
        return ContextualInitiativeSnapshot(values)

    def _persist(self, initiatives: dict[str, ContextualInitiative]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "initiatives": [_to_payload(item) for item in initiatives.values()],
        }
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    def _load(self) -> dict[str, ContextualInitiative]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != 1:
                raise ValueError("unsupported schema")
            items = [_from_payload(item) for item in payload["initiatives"]]
            result = {item.initiative_id: item for item in items}
            if len(result) != len(items):
                raise ValueError("duplicate ids")
            return result
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError(
                f"invalid contextual initiative file: {self.path}"
            ) from error


def _to_payload(initiative: ContextualInitiative) -> dict[str, object]:
    return {
        "initiative_id": initiative.initiative_id,
        "proposal_id": initiative.proposal_id,
        "observed_at": initiative.observed_at.isoformat(),
        "should_propose": initiative.should_propose,
        "confidence": initiative.confidence,
        "signals": [
            {
                "kind": signal.kind.value,
                "summary": signal.summary,
                "confidence": signal.confidence,
            }
            for signal in initiative.signals
        ],
        "summary": initiative.summary,
    }


def _from_payload(payload: dict[str, object]) -> ContextualInitiative:
    return ContextualInitiative(
        initiative_id=str(payload["initiative_id"]),
        proposal_id=str(payload["proposal_id"]),
        observed_at=datetime.fromisoformat(str(payload["observed_at"])),
        should_propose=bool(payload["should_propose"]),
        confidence=float(payload["confidence"]),
        signals=tuple(
            ContextSignal(
                kind=ContextSignalKind(str(item["kind"])),
                summary=str(item["summary"]),
                confidence=float(item["confidence"]),
            )
            for item in payload["signals"]
        ),
        summary=str(payload["summary"]),
    )
