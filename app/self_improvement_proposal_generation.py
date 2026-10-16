from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from core.self_diagnostics import (
    DiagnosticProofResult,
    DiagnosticProofSpecification,
    DiagnosticProofStatus,
    DiagnosticProposalRequest,
)

_MAX_AFFECTED_FILES = 4
_MAX_VALIDATION_TESTS = 8

_PROTECTED_EXACT = frozenset(
    {
        "CHANGELOG.md",
        "CHANGELOG_ARCHITECTURE.md",
        "docs/history/ESTADO_MAESTRO_INTEGRAL.md",
        "README.md",
        "docs/history/ROOT_DOCUMENTATION_INSTALLATION.md",
        "VISION.md",
        "architecture_rules.md",
        "integration_decision.md",
        "app/self_improvement_proposal_generation.py",
    }
)
_PROTECTED_PREFIXES = (
    "core/self_diagnostics/",
    "core/unified_permission_consent/",
    "docs/quality/",
)
_PROTECTED_NAME_FRAGMENTS = (
    "approval",
    "authority",
    "consent",
    "constitution",
    "governance",
    "permission",
    "quality_baseline",
    "self_diagnostics",
    "self_improvement",
)


@dataclass(frozen=True)
class DiagnosticProjectFileEvidence:
    """Explicit, hash-bound project evidence for one proposal target or test."""

    relative_path: str
    content_sha256: str
    rationale: str

    def __post_init__(self) -> None:
        path = _safe_relative_path(self.relative_path)
        digest = self.content_sha256.strip().casefold()
        rationale = self.rationale.strip()
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("project evidence requires sha256 content digest")
        if not rationale:
            raise ValueError("project evidence requires rationale")
        object.__setattr__(self, "relative_path", path)
        object.__setattr__(self, "content_sha256", digest)
        object.__setattr__(self, "rationale", rationale)


@dataclass(frozen=True)
class DiagnosticProjectEvidence:
    """Bounded project evidence supplied to the subordinate proposal producer."""

    affected_files: tuple[DiagnosticProjectFileEvidence, ...]
    validation_tests: tuple[DiagnosticProjectFileEvidence, ...]

    def __post_init__(self) -> None:
        if not self.affected_files:
            raise ValueError("proposal generation requires affected-file evidence")
        if not self.validation_tests:
            raise ValueError("proposal generation requires validation-test evidence")
        if len(self.affected_files) > _MAX_AFFECTED_FILES:
            raise ValueError("proposal generation affected-file scope is too broad")
        if len(self.validation_tests) > _MAX_VALIDATION_TESTS:
            raise ValueError("proposal generation validation-test scope is too broad")
        affected = tuple(item.relative_path for item in self.affected_files)
        tests = tuple(item.relative_path for item in self.validation_tests)
        if len(set(affected)) != len(affected):
            raise ValueError("affected-file evidence must be unique")
        if len(set(tests)) != len(tests):
            raise ValueError("validation-test evidence must be unique")
        if any(not path.startswith("tests/") for path in tests):
            raise ValueError("validation evidence must reference existing tests")


def generate_diagnostic_proposal_request(
    proof: DiagnosticProofSpecification,
    result: DiagnosticProofResult,
    evidence: DiagnosticProjectEvidence,
    *,
    project_root: Path,
    proposal_id: str,
) -> DiagnosticProposalRequest:
    """Generate one inert M399.5 request from reproduced proof and project evidence."""

    _validate_reproduced_proof(proof, result)
    _verify_project_evidence(evidence, project_root=project_root)

    affected_files = tuple(item.relative_path for item in evidence.affected_files)
    validation_tests = tuple(item.relative_path for item in evidence.validation_tests)
    for path in affected_files:
        if _is_protected_path(path):
            raise ValueError(
                "proposal generation cannot target protected governance scope"
            )

    metric = proof.metric.strip()
    source = proof.source_authority.strip()
    title = f"Review reproduced {metric} diagnostic behavior"
    target_summary = ", ".join(affected_files)
    change_intent = (
        f"Minimally adjust the {source} implementation for {metric} in "
        f"{target_summary} so the reproduced diagnostic condition can be addressed "
        "without expanding authority or bypassing existing review boundaries."
    )
    risk_notes = (
        (
            f"Generated from reproduced proof {proof.proof_id}; "
            "causal truth is not assumed."
        ),
        "Only hash-verified project files and existing tests are in scope.",
        "Proposal generation does not authorize application or operational mutation.",
    )
    return DiagnosticProposalRequest(
        proposal_id=proposal_id,
        title=title,
        change_intent=change_intent,
        affected_files=affected_files,
        validation_tests=validation_tests,
        risk_notes=risk_notes,
    )


def _validate_reproduced_proof(
    proof: DiagnosticProofSpecification,
    result: DiagnosticProofResult,
) -> None:
    if result.proof_id != proof.proof_id:
        raise ValueError("proposal generation proof result must match proof")
    if result.hypothesis_id != proof.hypothesis.hypothesis_id:
        raise ValueError("proposal generation hypothesis must match proof")
    if result.evidence_digest != proof.evidence_digest:
        raise ValueError("proposal generation evidence digest must match proof")
    if result.status is not DiagnosticProofStatus.REPRODUCED:
        raise ValueError("proposal generation requires reproduced proof")


def _verify_project_evidence(
    evidence: DiagnosticProjectEvidence,
    *,
    project_root: Path,
) -> None:
    root = project_root.resolve()
    for item in (*evidence.affected_files, *evidence.validation_tests):
        path = (root / item.relative_path).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError("project evidence escaped project root") from exc
        if not path.is_file():
            raise ValueError("project evidence requires existing file")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item.content_sha256:
            raise ValueError("project evidence content digest mismatch")


def _safe_relative_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or normalized in {".", ".."}
        or ".." in path.parts
    ):
        raise ValueError("project evidence requires safe relative path")
    return path.as_posix()


def _is_protected_path(relative_path: str) -> bool:
    if relative_path in _PROTECTED_EXACT:
        return True
    if any(relative_path.startswith(prefix) for prefix in _PROTECTED_PREFIXES):
        return True
    name = PurePosixPath(relative_path).name.casefold()
    return any(fragment in name for fragment in _PROTECTED_NAME_FRAGMENTS)
