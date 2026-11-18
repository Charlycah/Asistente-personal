"""Isolated non-authorizing composition for provenance admission.

This composition does not capture trusted executions, verify a
governed journal, or register provenance.
"""

from app.cross_domain_invocation_correlation import (
    CrossDomainInvocationCorrelator,
)
from app.cross_domain_provenance_admission_authority import (
    CrossDomainProvenanceAdmissionAuthority,
)
from app.cross_domain_provenance_admission_contracts import (
    ProvenanceAdmissionRequest,
    ProvenanceAdmissionResult,
)


class CrossDomainProvenanceAdmissionComposition:
    """Own non-authorizing dependencies without exposing admission."""

    __slots__ = ("__correlator", "__authority")

    def __init__(self) -> None:
        self.__correlator = CrossDomainInvocationCorrelator()
        self.__authority = CrossDomainProvenanceAdmissionAuthority()

    def evaluate(
        self,
        request: ProvenanceAdmissionRequest,
    ) -> ProvenanceAdmissionResult:
        """Evaluate candidate metadata; never grant provenance."""
        return self.__authority.evaluate(request)
