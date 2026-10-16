from __future__ import annotations

import difflib
import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path, PurePosixPath

from .models import (
    DiagnosticDiffFile,
    DiagnosticHumanDecision,
    DiagnosticProposal,
    DiagnosticReviewPackage,
    DiagnosticSandboxResult,
    DiagnosticSandboxStatus,
)

REVIEW_ROOT = PurePosixPath(".roby/review/proposals")


def _prepare_diagnostic_review(
    proposal: DiagnosticProposal,
    sandbox: DiagnosticSandboxResult,
    *,
    project_root: Path,
    review_id: str,
) -> DiagnosticReviewPackage:
    """Build an inert diff/explanation package from a passed isolated sandbox."""

    review_id = review_id.strip()
    if not review_id or "/" in review_id or "\\" in review_id:
        raise ValueError("diagnostic review requires safe review_id")
    if sandbox.proposal_id != proposal.proposal_id:
        raise ValueError("diagnostic review sandbox must match proposal")
    if sandbox.status is not DiagnosticSandboxStatus.PASSED:
        raise ValueError("diagnostic review requires passed sandbox")

    root = project_root.resolve()
    sandbox_root = (root / sandbox.sandbox_path).resolve()
    governed_root = (root / REVIEW_ROOT).resolve()
    try:
        sandbox_root.relative_to(governed_root)
    except ValueError as exc:
        raise ValueError(
            "diagnostic review sandbox must remain in review root"
        ) from exc
    if not sandbox_root.is_dir():
        raise ValueError("diagnostic review requires existing sandbox")

    diff_files: list[DiagnosticDiffFile] = []
    for relative_path in sandbox.candidate_files:
        active = (root / relative_path).resolve()
        candidate = (sandbox_root / relative_path).resolve()
        try:
            active.relative_to(root)
            candidate.relative_to(sandbox_root)
        except ValueError as exc:
            raise ValueError("diagnostic review file escaped governed roots") from exc
        if not active.is_file() or not candidate.is_file():
            raise ValueError("diagnostic review requires comparable project files")
        before = active.read_text(encoding="utf-8").splitlines()
        after = candidate.read_text(encoding="utf-8").splitlines()
        diff = "\n".join(
            difflib.unified_diff(
                before,
                after,
                fromfile=f"a/{relative_path}",
                tofile=f"b/{relative_path}",
                lineterm="",
            )
        )
        if diff:
            diff_files.append(DiagnosticDiffFile(relative_path, diff))

    if not diff_files:
        raise ValueError("diagnostic review requires an explicit candidate diff")

    review_path = (
        REVIEW_ROOT / proposal.proposal_id / "review" / review_id / "review.json"
    )
    return DiagnosticReviewPackage(
        review_id=review_id,
        proposal_id=proposal.proposal_id,
        sandbox_id=sandbox.sandbox_id,
        diff_files=tuple(diff_files),
        explanation=(
            f"proposal: {proposal.title}",
            f"change_intent: {proposal.change_intent}",
            f"sandbox_tests: {len(sandbox.validation_tests)} passed",
            f"changed_files: {len(diff_files)}",
            "sandbox success is evidence, not authorization",
        ),
        review_path=review_path.as_posix(),
        rationale=(
            "diff_derived_from_active_baseline_and_passed_sandbox",
            "review_package_is_inert",
            "human_decision_required_before_any_change",
            "approval_does_not_apply_code",
            "prediction_is_not_certainty",
        ),
    )


def _write_diagnostic_review(
    review: DiagnosticReviewPackage,
    *,
    project_root: Path,
) -> Path:
    root = project_root.resolve()
    destination = (root / review.review_path).resolve()
    governed_root = (root / REVIEW_ROOT).resolve()
    try:
        destination.relative_to(governed_root)
    except ValueError as exc:
        raise ValueError("diagnostic review must remain inside review root") from exc
    if destination.exists():
        raise FileExistsError("diagnostic review artifact already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(_json_safe(asdict(review)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def _record_human_decision(
    review: DiagnosticReviewPackage,
    decision: DiagnosticHumanDecision,
    *,
    project_root: Path,
) -> Path:
    """Record an explicit human decision; never apply the candidate change."""

    if decision.review_id != review.review_id:
        raise ValueError("human decision must match diagnostic review")
    root = project_root.resolve()
    review_dir = (root / PurePosixPath(review.review_path).parent).resolve()
    governed_root = (root / REVIEW_ROOT).resolve()
    try:
        review_dir.relative_to(governed_root)
    except ValueError as exc:
        raise ValueError("human decision must remain inside review root") from exc
    destination = review_dir / "decision.json"
    if destination.exists():
        raise FileExistsError("diagnostic human decision already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(_json_safe(asdict(decision)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def _json_safe(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
