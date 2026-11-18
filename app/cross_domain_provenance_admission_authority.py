"""Isolated, fail-closed, non-authorizing provenance admission boundary.

This component deliberately has no trusted execution producer,
journal dependency, or provenance registry. It cannot admit.
"""

from app.cross_domain_provenance_admission_contracts import (
    AdmissionDecision,
    AdmissionReason,
    ProvenanceAdmissionRequest,
    ProvenanceAdmissionResult,
)


class CrossDomainProvenanceAdmissionAuthority:
    """Evaluate candidate metadata without granting provenance authority."""

    def evaluate(
        self,
        request: ProvenanceAdmissionRequest,
    ) -> ProvenanceAdmissionResult:
        if type(request) is not ProvenanceAdmissionRequest:
            return ProvenanceAdmissionResult(
                decision=AdmissionDecision.REJECTED,
                reason=AdmissionReason.INVALID_REQUEST,
            )

        try:
            return self._evaluate_candidate(request)
        except Exception:
            return ProvenanceAdmissionResult(
                decision=AdmissionDecision.UNRESOLVED,
                reason=AdmissionReason.INTERNAL_FAILURE,
            )

    def _evaluate_candidate(
        self,
        request: ProvenanceAdmissionRequest,
    ) -> ProvenanceAdmissionResult:
        return ProvenanceAdmissionResult(
            decision=AdmissionDecision.UNRESOLVED,
            reason=AdmissionReason.EXECUTION_NOT_VERIFIED,
            request=request,
        )
