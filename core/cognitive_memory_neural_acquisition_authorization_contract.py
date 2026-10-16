"""Pure preflight contract for a bounded experimental model acquisition.

This module cannot grant executable permission or perform an acquisition.
The existing Authorization authority and Owner retain all actual decisions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath, PureWindowsPath

_REPOSITORY = "BAAI/bge-reranker-v2-m3"
_SOURCE = "https://huggingface.co/BAAI/bge-reranker-v2-m3"
_ARTIFACTS = frozenset({"config.json", "tokenizer.json", "model.safetensors"})
_REVISION = re.compile(r"[0-9a-fA-F]{40}\Z")
_POSITIVE = "ELIGIBLE_FOR_SEPARATE_OWNER_INVOKED_ACQUISITION"


@dataclass(frozen=True)
class AcquisitionAuthorizationRequest:
    request_id: str
    requester: str
    approving_owner: str
    decision_timestamp: str
    expires_at: str
    action: str
    repository: str
    revision: str
    license_id: str
    license_evidence: str
    sources: tuple[str, ...]
    artifacts: tuple[str, ...]
    destination: str
    max_bytes: int
    max_files: int
    timeout_seconds: int
    retry_limit: int
    privacy_public_only: bool
    evidence_ledger: str


@dataclass(frozen=True)
class OwnerAcquisitionApproval:
    request_id: str
    owner: str
    decision: str
    signed_evidence: str
    revoked: bool


def _bounded_relative_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if ":" in value or "\x00" in value or value.startswith("/"):
        return False
    path = PurePosixPath(value)
    windows = PureWindowsPath(value)
    return (
        not path.is_absolute()
        and not windows.is_absolute()
        and not windows.drive
        and all(part not in {"", ".", ".."} for part in value.split("/"))
    )


def _ordered_timestamps(request: AcquisitionAuthorizationRequest) -> bool:
    try:
        start_text = request.decision_timestamp.replace("Z", "+00:00")
        start = datetime.fromisoformat(start_text)
        end = datetime.fromisoformat(request.expires_at.replace("Z", "+00:00"))
        return start.tzinfo is not None and end.tzinfo is not None and end > start
    except (AttributeError, TypeError, ValueError):
        return False


def acquisition_authorization_decision(
    request: object, approval: object
) -> str:
    """Check synthetic preflight scope; never produce an executable grant.

    Time ordering is deterministic. Live expiry and attestation verification
    remain mandatory at the existing Owner-invoked Authorization boundary.
    """
    if not isinstance(request, AcquisitionAuthorizationRequest):
        return "DENY"
    if not isinstance(approval, OwnerAcquisitionApproval):
        return "DENY"
    if not all(
        isinstance(value, str) and bool(value.strip())
        for value in (
            request.request_id,
            request.requester,
            request.approving_owner,
            request.license_evidence,
            request.evidence_ledger,
            approval.signed_evidence,
        )
    ):
        return "DENY"
    if (
        approval.request_id != request.request_id
        or approval.owner != request.approving_owner
        or approval.decision != "APPROVE"
        or approval.revoked is not False
        or request.action != "MODEL_ACQUISITION"
        or request.repository != _REPOSITORY
        or request.license_id != "Apache-2.0"
        or request.privacy_public_only is not True
    ):
        return "DENY"
    if not isinstance(request.revision, str) or not _REVISION.fullmatch(
        request.revision
    ):
        return "DENY"
    if not _ordered_timestamps(request):
        return "DENY"
    if request.sources != (_SOURCE,):
        return "DENY"
    if (
        not isinstance(request.artifacts, tuple)
        or len(request.artifacts) != len(_ARTIFACTS)
        or frozenset(request.artifacts) != _ARTIFACTS
    ):
        return "DENY"
    if not _bounded_relative_path(request.destination):
        return "DENY"
    if not request.destination.startswith("isolated/"):
        return "DENY"
    if not _bounded_relative_path(request.evidence_ledger):
        return "DENY"
    if not request.evidence_ledger.startswith("isolated/"):
        return "DENY"
    if any(
        type(value) is not int or value < minimum
        for value, minimum in (
            (request.max_bytes, 1),
            (request.max_files, len(_ARTIFACTS)),
            (request.timeout_seconds, 1),
            (request.retry_limit, 0),
        )
    ):
        return "DENY"
    return _POSITIVE


def phase_can_authorize_next(phase: str) -> bool:
    """No experiment phase inherits authorization from another phase."""
    del phase
    return False
