from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

from .models import (
    DiagnosticProposal,
    DiagnosticProposalStatus,
    DiagnosticSandboxRequest,
    DiagnosticSandboxResult,
    DiagnosticSandboxStatus,
)


def _validate_diagnostic_sandbox(
    proposal: DiagnosticProposal,
    request: DiagnosticSandboxRequest,
    *,
    project_root: Path,
) -> DiagnosticSandboxResult:
    """Validate explicit candidate files only inside an isolated project copy."""

    if proposal.status is not DiagnosticProposalStatus.DRAFT:
        raise ValueError("diagnostic sandbox requires draft proposal")

    allowed_files = set(proposal.affected_files)
    candidate_paths = tuple(item.relative_path for item in request.candidate_files)
    if not set(candidate_paths).issubset(allowed_files):
        raise ValueError("sandbox candidate files must be declared by proposal")

    root = project_root.resolve()
    sandbox_relative = (
        PurePosixPath(proposal.review_path).parent / "sandbox" / request.sandbox_id
    )
    sandbox_root = (root / sandbox_relative).resolve()
    review_root = (root / ".roby/review/proposals").resolve()
    try:
        sandbox_root.relative_to(review_root)
    except ValueError as exc:
        raise ValueError("diagnostic sandbox must remain inside review root") from exc
    if sandbox_root.exists():
        raise FileExistsError("diagnostic sandbox already exists")

    _copy_project(root, sandbox_root)
    for candidate in request.candidate_files:
        destination = (sandbox_root / candidate.relative_path).resolve()
        try:
            destination.relative_to(sandbox_root)
        except ValueError as exc:
            raise ValueError("sandbox candidate escaped isolated root") from exc
        if not destination.is_file():
            raise ValueError("sandbox candidate must replace an existing project file")
        destination.write_text(candidate.content, encoding="utf-8")

    validation_tests = _validated_test_paths(
        proposal.validation_tests,
        sandbox_root=sandbox_root,
    )
    command = [sys.executable, "-m", "pytest", "-q", *validation_tests]
    completed = subprocess.run(
        command,
        cwd=sandbox_root,
        capture_output=True,
        text=True,
        check=False,
    )
    status = (
        DiagnosticSandboxStatus.PASSED
        if completed.returncode == 0
        else DiagnosticSandboxStatus.FAILED
    )
    return DiagnosticSandboxResult(
        sandbox_id=request.sandbox_id,
        proposal_id=proposal.proposal_id,
        status=status,
        sandbox_path=sandbox_relative.as_posix(),
        candidate_files=candidate_paths,
        validation_tests=validation_tests,
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        rationale=(
            "candidate_changes_materialized_only_in_isolated_copy",
            "only_proposal_declared_tests_executed",
            "sandbox_result_does_not_authorize_application",
            "operational_project_remained_unchanged",
            "human_decision_required_before_any_change",
            "prediction_is_not_certainty",
        ),
    )


def _copy_project(project_root: Path, sandbox_root: Path) -> None:
    ignored = shutil.ignore_patterns(
        ".git",
        ".venv",
        "venv",
        ".pytest_cache",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".roby",
    )
    shutil.copytree(project_root, sandbox_root, ignore=ignored)


def _validated_test_paths(
    validation_tests: tuple[str, ...],
    *,
    sandbox_root: Path,
) -> tuple[str, ...]:
    validated: list[str] = []
    for raw in validation_tests:
        value = raw.strip().replace("\\", "/")
        path_part = value.split("::", 1)[0]
        path = PurePosixPath(path_part)
        if (
            not value
            or value.startswith("-")
            or path.is_absolute()
            or ".." in path.parts
            or not path.parts
            or path.parts[0] != "tests"
            or path.suffix != ".py"
        ):
            raise ValueError("sandbox validation tests must be safe test paths")
        if not (sandbox_root / path_part).is_file():
            raise ValueError("sandbox validation test path must exist")
        validated.append(value)
    return tuple(validated)
