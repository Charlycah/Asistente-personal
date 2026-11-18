"""Structural identity/capability binding; never execution authority."""

from dataclasses import dataclass
from enum import Enum

from app.cross_domain_execution_authorization import ExecutionAuthorizationRequest
from app.cross_domain_invocation_capture import (
    CrossDomainInvocationCapture,
    InvocationCaptureState,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


class GovernedIdentityBindingDecision(str, Enum):
    BOUND = "bound"
    REJECTED = "rejected"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class GovernedIdentityBindingResult:
    decision: GovernedIdentityBindingDecision
    reason: str
    authorized: bool = False

    def __post_init__(self) -> None:
        if type(self.decision) is not GovernedIdentityBindingDecision:
            raise ValueError("invalid binding decision")
        if type(self.reason) is not str or not self.reason.strip():
            raise ValueError("invalid binding reason")
        if type(self.authorized) is not bool or self.authorized:
            raise ValueError("binding cannot authorize execution")


class CrossDomainGovernedIdentityBinder:
    """Compare an invocation with the official capability registration."""

    def __init__(
        self,
        registry: OfficialRuntimeCapabilityRegistry,
        capture: CrossDomainInvocationCapture,
    ) -> None:
        if type(registry) is not OfficialRuntimeCapabilityRegistry:
            raise ValueError("official runtime registry required")
        if type(capture) is not CrossDomainInvocationCapture:
            raise ValueError("canonical invocation capture required")
        self._registry = registry
        self._capture = capture

    def evaluate(self, request: object) -> GovernedIdentityBindingResult:
        if type(request) is not ExecutionAuthorizationRequest:
            return GovernedIdentityBindingResult(
                GovernedIdentityBindingDecision.REJECTED,
                "invalid_request",
            )

        snapshot = self._capture.snapshot(
            request.invocation_id,
            owner=request.owner,
            session_id=request.session_id,
        )
        if snapshot is None:
            return GovernedIdentityBindingResult(
                GovernedIdentityBindingDecision.REJECTED,
                "invocation_identity_mismatch_or_missing",
            )

        if snapshot.state is not InvocationCaptureState.STARTED:
            return GovernedIdentityBindingResult(
                GovernedIdentityBindingDecision.REJECTED,
                "invocation_not_started",
            )

        registration = self._registry.registration_for(request.capability)
        if registration is None:
            return GovernedIdentityBindingResult(
                GovernedIdentityBindingDecision.UNRESOLVED,
                "capability_not_registered",
            )

        descriptor = registration.descriptor
        canonical = self._registry.manager.get(request.capability)

        if descriptor.name != request.capability:
            return GovernedIdentityBindingResult(
                GovernedIdentityBindingDecision.REJECTED,
                "noncanonical_capability_name",
            )

        if canonical is not descriptor:
            return GovernedIdentityBindingResult(
                GovernedIdentityBindingDecision.REJECTED,
                "registry_descriptor_mismatch",
            )

        if descriptor.enabled is not True:
            return GovernedIdentityBindingResult(
                GovernedIdentityBindingDecision.REJECTED,
                "capability_disabled",
            )

        return GovernedIdentityBindingResult(
            GovernedIdentityBindingDecision.BOUND,
            "structural_binding_only",
        )