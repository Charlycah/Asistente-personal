from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock
from typing import Any

from .contracts import (
    ActionCandidate,
    AutonomyDecision,
    DecisionJournalEntry,
    DecisionOutcome,
    DecisionSituation,
    RiskAssessment,
)
from .decision_journal import InMemoryDecisionJournal, JournalSnapshot


class JsonlDecisionJournal:
    """Durable append-only decision journal backed by validated JSON Lines."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._memory = InMemoryDecisionJournal(self._load())

    def append(self, entry: DecisionJournalEntry) -> None:
        """Persist one validated entry before exposing it in memory."""

        with self._lock:
            current = self._memory.entries()
            InMemoryDecisionJournal((*current, entry))
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(
                _entry_to_payload(entry),
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(payload)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            self._memory.append(entry)

    def entries(self) -> tuple[DecisionJournalEntry, ...]:
        with self._lock:
            return self._memory.entries()

    def snapshot(self) -> JournalSnapshot:
        return JournalSnapshot(entries=self.entries())

    def _load(self) -> tuple[DecisionJournalEntry, ...]:
        if not self.path.exists():
            return ()
        entries: list[DecisionJournalEntry] = []
        with self.path.open("r", encoding="utf-8") as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    entries.append(_entry_from_payload(payload))
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise ValueError(
                        f"invalid decision journal record at line {line_number}"
                    ) from exc
        return tuple(entries)


def _entry_to_payload(entry: DecisionJournalEntry) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "journal_id": entry.journal_id,
        "situation": {
            "kind": entry.situation.kind,
            "description": entry.situation.description,
            "evidence": list(entry.situation.evidence),
            "observed_at": entry.situation.observed_at.isoformat(),
            "source": entry.situation.source,
            "urgency": entry.situation.urgency,
            "situation_id": entry.situation.situation_id,
        },
        "candidates": [
            {
                "action": candidate.action,
                "description": candidate.description,
                "rationale": list(candidate.rationale),
                "reversible": candidate.reversible.value,
                "estimated_cost": candidate.estimated_cost,
                "candidate_id": candidate.candidate_id,
            }
            for candidate in entry.candidates
        ],
        "assessments": [
            {
                "candidate_id": assessment.candidate_id,
                "risk": assessment.risk.value,
                "confidence": assessment.confidence,
                "impact": assessment.impact,
                "reversibility": assessment.reversibility.value,
                "reasons": list(assessment.reasons),
            }
            for assessment in entry.assessments
        ],
        "decision": {
            "situation_id": entry.decision.situation_id,
            "candidate_id": entry.decision.candidate_id,
            "disposition": entry.decision.disposition.value,
            "confidence": entry.decision.confidence,
            "risk": entry.decision.risk.value,
            "rationale": list(entry.decision.rationale),
            "decided_at": entry.decision.decided_at.isoformat(),
            "policy_level": entry.decision.policy_level.value,
            "decision_id": entry.decision.decision_id,
        },
        "outcome": _outcome_to_payload(entry.outcome),
    }


def _outcome_to_payload(outcome: DecisionOutcome | None) -> dict[str, Any] | None:
    if outcome is None:
        return None
    return {
        "decision_id": outcome.decision_id,
        "status": outcome.status.value,
        "observed_at": outcome.observed_at.isoformat(),
        "summary": outcome.summary,
        "evidence": list(outcome.evidence),
        "reversible_action_used": outcome.reversible_action_used,
        "outcome_id": outcome.outcome_id,
    }


def _entry_from_payload(payload: dict[str, Any]) -> DecisionJournalEntry:
    if payload["schema_version"] != 1:
        raise ValueError("unsupported decision journal schema version")
    situation_data = payload["situation"]
    decision_data = payload["decision"]
    outcome_data = payload["outcome"]
    return DecisionJournalEntry(
        situation=DecisionSituation(
            kind=situation_data["kind"],
            description=situation_data["description"],
            evidence=tuple(situation_data["evidence"]),
            observed_at=_parse_datetime(situation_data["observed_at"]),
            source=situation_data["source"],
            urgency=situation_data["urgency"],
            situation_id=situation_data["situation_id"],
        ),
        candidates=tuple(
            ActionCandidate(
                action=item["action"],
                description=item["description"],
                rationale=tuple(item["rationale"]),
                reversible=item["reversible"],
                estimated_cost=item["estimated_cost"],
                candidate_id=item["candidate_id"],
            )
            for item in payload["candidates"]
        ),
        assessments=tuple(
            RiskAssessment(
                candidate_id=item["candidate_id"],
                risk=item["risk"],
                confidence=item["confidence"],
                impact=item["impact"],
                reversibility=item["reversibility"],
                reasons=tuple(item["reasons"]),
            )
            for item in payload["assessments"]
        ),
        decision=AutonomyDecision(
            situation_id=decision_data["situation_id"],
            candidate_id=decision_data["candidate_id"],
            disposition=decision_data["disposition"],
            confidence=decision_data["confidence"],
            risk=decision_data["risk"],
            rationale=tuple(decision_data["rationale"]),
            decided_at=_parse_datetime(decision_data["decided_at"]),
            policy_level=decision_data["policy_level"],
            decision_id=decision_data["decision_id"],
        ),
        outcome=(
            None
            if outcome_data is None
            else DecisionOutcome(
                decision_id=outcome_data["decision_id"],
                status=outcome_data["status"],
                observed_at=_parse_datetime(outcome_data["observed_at"]),
                summary=outcome_data["summary"],
                evidence=tuple(outcome_data["evidence"]),
                reversible_action_used=outcome_data["reversible_action_used"],
                outcome_id=outcome_data["outcome_id"],
            )
        ),
        journal_id=payload["journal_id"],
    )


def _parse_datetime(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value)


__all__ = ["JsonlDecisionJournal"]
