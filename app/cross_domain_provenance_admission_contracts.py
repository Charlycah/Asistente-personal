"""Typed, non-authorizing contracts for provenance admission."""

from dataclasses import dataclass
from enum import Enum

from app.cross_domain_context_resolver import ContextDomain


class AdmissionDecision(str, Enum):
    ADMITTED = "admitted"
    REJECTED = "rejected"
    UNRESOLVED = "unresolved"


class AdmissionReason(str, Enum):
    VERIFIED = "verified"
    INVALID_REQUEST = "invalid_request"
    UNTRUSTED_PRODUCER = "untrusted_producer"
    EXECUTION_NOT_VERIFIED = "execution_not_verified"
    EXECUTION_FAILED = "execution_failed"
    INVOCATION_MISMATCH = "invocation_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    DOMAIN_NOT_ELIGIBLE = "domain_not_eligible"
    TURN_NOT_PERSISTED = "turn_not_persisted"
    DUPLICATE_ADMISSION = "duplicate_admission"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    INTERNAL_FAILURE = "internal_failure"


def _valid_identifier(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
    )


@dataclass(frozen=True)
class ProvenanceAdmissionRequest:
    """Candidate metadata; never proof of governed execution."""

    invocation_id: str
    owner: str
    session_id: str
    domain: ContextDomain
    execution_id: str
    turn_id: str
    sequence: int

    def __post_init__(self) -> None:
        for name in (
            "invocation_id",
            "owner",
            "session_id",
            "execution_id",
            "turn_id",
        ):
            if not _valid_identifier(getattr(self, name)):
                raise ValueError(f"invalid {name}")

        if not isinstance(self.domain, ContextDomain):
            raise ValueError("invalid domain")

        if type(self.sequence) is not int or self.sequence <= 0:
            raise ValueError("invalid sequence")


@dataclass(frozen=True)
class ProvenanceAdmissionResult:
    """Decision data, not an authority token or permission."""

    decision: AdmissionDecision
    reason: AdmissionReason
    request: ProvenanceAdmissionRequest | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.decision, AdmissionDecision):
            raise ValueError("invalid admission decision")

        if not isinstance(self.reason, AdmissionReason):
            raise ValueError("invalid admission reason")

        if self.request is not None and not isinstance(
            self.request, ProvenanceAdmissionRequest
        ):
            raise ValueError("invalid admission request")

        if self.decision is AdmissionDecision.ADMITTED:
            if self.reason is not AdmissionReason.VERIFIED:
                raise ValueError("admitted decision requires verified reason")
            if self.request is None:
                raise ValueError("admitted decision requires request")
        elif self.reason is AdmissionReason.VERIFIED:
            raise ValueError("verified reason requires admitted decision")
