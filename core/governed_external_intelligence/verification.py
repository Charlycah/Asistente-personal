from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .models import (
    ExternalIntelligenceCapability,
    ExternalIntelligenceEnvelope,
    ExternalIntelligenceStatus,
)


class ExternalVerificationStatus(str, Enum):
    VERIFIED = "verified"
    LIMITED = "limited"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ExternalIntelligenceVerification:
    envelope_id: str
    status: ExternalVerificationStatus | str
    provenance_digest: str
    checks: tuple[str, ...]
    limitations: tuple[str, ...] = ()
    verification_id: str = ""

    def __post_init__(self) -> None:
        status = ExternalVerificationStatus(self.status)
        checks = tuple(item.strip() for item in self.checks)
        limitations = tuple(item.strip() for item in self.limitations)
        if not self.envelope_id.strip():
            raise ValueError("external verification requires envelope_id")
        if not self.provenance_digest.strip():
            raise ValueError("external verification requires provenance digest")
        if not checks or any(not item for item in checks):
            raise ValueError("external verification requires explicit checks")
        if any(not item for item in limitations):
            raise ValueError("external verification limitations must not be blank")
        payload = "|".join(
            (
                self.envelope_id,
                status.value,
                self.provenance_digest,
                *checks,
                *limitations,
            )
        )
        expected = sha256(payload.encode()).hexdigest()
        if self.verification_id and self.verification_id != expected:
            raise ValueError("external verification id is inconsistent")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "checks", checks)
        object.__setattr__(self, "limitations", limitations)
        object.__setattr__(self, "verification_id", expected)

    @property
    def cognitive_authority_granted(self) -> bool:
        return False

    @property
    def truth_certified(self) -> bool:
        return False


class GovernedExternalIntelligenceVerifier:
    """Verifies envelope provenance and admissibility without certifying truth."""

    VERIFIER_ID = "external_intelligence_provenance_verifier"

    @property
    def verifier_id(self) -> str:
        return self.VERIFIER_ID

    def verify(
        self,
        envelope: ExternalIntelligenceEnvelope,
    ) -> ExternalIntelligenceVerification:
        provenance = envelope.provenance
        request = envelope.request
        checks = [
            "envelope_identity_is_self_consistent",
            "request_and_provenance_capability_match",
            "actor_matches_evidence_origin",
            "observed_at_is_timezone_aware",
            "trace_ids_are_unique",
            "external_evidence_has_no_cognitive_authority",
        ]
        limitations = ["external_content_truth_is_not_certified"]

        if request.target_id and request.target_id != provenance.actor_id:
            raise ValueError("external verification target must match provenance actor")
        if request.capability is ExternalIntelligenceCapability.INFERENCE_PROVIDER:
            if envelope.inference is None:
                raise ValueError("external verification requires inference evidence")
            if envelope.inference.provider != provenance.actor_id:
                raise ValueError("external verification provider provenance mismatch")
            checks.append("provider_identity_matches_provenance")
            if not provenance.trace_ids:
                limitations.append("provider_execution_trace_is_missing")
        else:
            if envelope.information is None:
                raise ValueError("external verification requires information evidence")
            if envelope.information.source_id != provenance.actor_id:
                raise ValueError("external verification source provenance mismatch")
            checks.append("source_identity_matches_provenance")
            if not provenance.trace_ids:
                limitations.append("source_execution_trace_is_not_available")

        status = ExternalVerificationStatus.VERIFIED
        if envelope.status is ExternalIntelligenceStatus.REJECTED:
            status = ExternalVerificationStatus.REJECTED
            limitations.append("external_result_was_rejected_at_admission")
        elif limitations != ["external_content_truth_is_not_certified"]:
            status = ExternalVerificationStatus.LIMITED

        digest = sha256(
            "|".join(
                (
                    provenance.actor_id,
                    provenance.capability.value,
                    provenance.execution_scope.value,
                    str(provenance.network_used),
                    provenance.observed_at.isoformat(),
                    *provenance.trace_ids,
                )
            ).encode()
        ).hexdigest()
        return ExternalIntelligenceVerification(
            envelope_id=envelope.envelope_id,
            status=status,
            provenance_digest=digest,
            checks=tuple(checks),
            limitations=tuple(limitations),
        )
