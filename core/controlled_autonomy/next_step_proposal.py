from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Protocol, runtime_checkable
from uuid import uuid4

from .goal_blocking import GoalBlockageSnapshot
from .goal_planning import (
    GoalPlan,
    GoalPlanSnapshot,
    GoalPlanStatus,
    GoalPlanStep,
    GoalPlanStepStatus,
)
from .goal_selection import GoalSelectionReport


@dataclass(frozen=True, slots=True)
class NextStepProposal:
    proposal_id: str
    selection_id: str
    goal_id: str | None
    plan_id: str | None
    step_id: str | None
    proposed_at: datetime
    description: str
    rationale: str
    risk: str
    required_capability: str | None
    authorization_required: bool
    blockers: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        if not self.proposal_id.strip() or not self.selection_id.strip():
            raise ValueError("proposal identifiers must not be blank")
        if self.proposed_at.tzinfo is None:
            raise ValueError("proposal timestamp must be timezone-aware")
        if self.risk not in {"none", "low", "medium", "high"}:
            raise ValueError("proposal risk is invalid")
        if not self.description.strip() or not self.rationale.strip():
            raise ValueError("proposal text must not be blank")
        if not self.summary.strip():
            raise ValueError("proposal summary must not be blank")
        if self.step_id is not None and (self.goal_id is None or self.plan_id is None):
            raise ValueError("proposed step requires goal and plan ids")


@dataclass(frozen=True, slots=True)
class NextStepProposalSnapshot:
    proposals: tuple[NextStepProposal, ...]

    @property
    def actionable_count(self) -> int:
        return sum(
            item.step_id is not None and not item.blockers
            for item in self.proposals
        )


@runtime_checkable
class NextStepProposer(Protocol):
    def propose(
        self,
        *,
        selection: GoalSelectionReport,
        plans: GoalPlanSnapshot,
        blockages: GoalBlockageSnapshot,
        proposed_at: datetime,
    ) -> NextStepProposal: ...


class DeterministicNextStepProposer:
    """Proposes attention to one plan step without authorizing or executing it."""

    def propose(
        self,
        *,
        selection: GoalSelectionReport,
        plans: GoalPlanSnapshot,
        blockages: GoalBlockageSnapshot,
        proposed_at: datetime,
    ) -> NextStepProposal:
        if proposed_at.tzinfo is None:
            raise ValueError("proposal timestamp must be timezone-aware")
        goal_id = selection.selected_goal_id
        plan = _active_plan(goal_id, plans)
        step = _next_available_step(plan)
        blockers = _latest_blockers(goal_id, blockages)
        if goal_id is None:
            return self._empty(selection, proposed_at, "No selected goal is available.")
        if plan is None:
            return self._empty(
                selection,
                proposed_at,
                "The selected goal has no active persistent plan.",
                goal_id=goal_id,
            )
        if step is None:
            return self._empty(
                selection,
                proposed_at,
                "The selected goal has no currently available pending step.",
                goal_id=goal_id,
                plan_id=plan.plan_id,
                blockers=blockers,
            )
        authorization_required = step.risk in {"medium", "high"} or (
            step.required_capability is not None
        )
        summary = (
            f"Proposed step {step.step_id} for goal {goal_id}; "
            "authorization and execution remain separate."
        )
        return NextStepProposal(
            proposal_id=uuid4().hex,
            selection_id=selection.selection_id,
            goal_id=goal_id,
            plan_id=plan.plan_id,
            step_id=step.step_id,
            proposed_at=proposed_at,
            description=step.description,
            rationale=step.rationale,
            risk=step.risk,
            required_capability=step.required_capability,
            authorization_required=authorization_required,
            blockers=blockers,
            summary=summary,
        )

    def _empty(
        self,
        selection: GoalSelectionReport,
        proposed_at: datetime,
        message: str,
        *,
        goal_id: str | None = None,
        plan_id: str | None = None,
        blockers: tuple[str, ...] = (),
    ) -> NextStepProposal:
        return NextStepProposal(
            proposal_id=uuid4().hex,
            selection_id=selection.selection_id,
            goal_id=goal_id,
            plan_id=plan_id,
            step_id=None,
            proposed_at=proposed_at,
            description=message,
            rationale="No action is proposed without an available auditable step.",
            risk="none",
            required_capability=None,
            authorization_required=False,
            blockers=blockers,
            summary=message,
        )


@runtime_checkable
class NextStepProposalStore(Protocol):
    def append(self, proposal: NextStepProposal) -> None: ...

    def snapshot(self) -> NextStepProposalSnapshot: ...


class JsonNextStepProposalStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._proposals = self._load()

    def append(self, proposal: NextStepProposal) -> None:
        with self._lock:
            if proposal.proposal_id in self._proposals:
                raise ValueError(
                    f"duplicate next step proposal id: {proposal.proposal_id}"
                )
            updated = dict(self._proposals)
            updated[proposal.proposal_id] = proposal
            self._persist(updated)
            self._proposals = updated

    def snapshot(self) -> NextStepProposalSnapshot:
        with self._lock:
            values = tuple(
                sorted(
                    self._proposals.values(),
                    key=lambda item: (item.proposed_at, item.proposal_id),
                )
            )
        return NextStepProposalSnapshot(values)

    def _persist(self, proposals: dict[str, NextStepProposal]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "proposals": [_to_payload(item) for item in proposals.values()],
        }
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    def _load(self) -> dict[str, NextStepProposal]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != 1:
                raise ValueError("unsupported schema")
            proposals = [_from_payload(item) for item in payload["proposals"]]
            result = {item.proposal_id: item for item in proposals}
            if len(result) != len(proposals):
                raise ValueError("duplicate ids")
            return result
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError(f"invalid next step proposal file: {self.path}") from error


def _active_plan(goal_id: str | None, plans: GoalPlanSnapshot) -> GoalPlan | None:
    matches = [
        plan
        for plan in plans.plans
        if plan.goal_id == goal_id and plan.status is GoalPlanStatus.ACTIVE
    ]
    return max(matches, key=lambda item: (item.updated_at, item.plan_id), default=None)


def _next_available_step(plan: GoalPlan | None) -> GoalPlanStep | None:
    if plan is None:
        return None
    resolved = {
        step.step_id
        for step in plan.steps
        if step.status in {GoalPlanStepStatus.COMPLETED, GoalPlanStepStatus.SKIPPED}
    }
    candidates = [
        step
        for step in plan.steps
        if step.status is GoalPlanStepStatus.PENDING
        and set(step.dependencies).issubset(resolved)
    ]
    return min(candidates, key=lambda item: item.sequence, default=None)


def _latest_blockers(
    goal_id: str | None, blockages: GoalBlockageSnapshot
) -> tuple[str, ...]:
    reports = [item for item in blockages.reports if item.goal_id == goal_id]
    if not reports:
        return ()
    latest = max(reports, key=lambda item: (item.observed_at, item.report_id))
    return tuple(blocker.summary for blocker in latest.blockers)


def _to_payload(item: NextStepProposal) -> dict[str, object]:
    return {
        "proposal_id": item.proposal_id,
        "selection_id": item.selection_id,
        "goal_id": item.goal_id,
        "plan_id": item.plan_id,
        "step_id": item.step_id,
        "proposed_at": item.proposed_at.isoformat(),
        "description": item.description,
        "rationale": item.rationale,
        "risk": item.risk,
        "required_capability": item.required_capability,
        "authorization_required": item.authorization_required,
        "blockers": list(item.blockers),
        "summary": item.summary,
    }


def _from_payload(payload: dict[str, object]) -> NextStepProposal:
    return NextStepProposal(
        proposal_id=str(payload["proposal_id"]),
        selection_id=str(payload["selection_id"]),
        goal_id=payload.get("goal_id"),
        plan_id=payload.get("plan_id"),
        step_id=payload.get("step_id"),
        proposed_at=datetime.fromisoformat(str(payload["proposed_at"])),
        description=str(payload["description"]),
        rationale=str(payload["rationale"]),
        risk=str(payload["risk"]),
        required_capability=payload.get("required_capability"),
        authorization_required=bool(payload["authorization_required"]),
        blockers=tuple(str(item) for item in payload.get("blockers", [])),
        summary=str(payload["summary"]),
    )
