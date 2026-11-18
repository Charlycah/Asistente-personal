"""Non-authorizing M63 permission observation for RC-01B.

A permission decision is not an execution credential.
This module never grants execution or invokes a capability.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.cross_domain_execution_authorization import (
    ExecutionAuthorizationRequest,
)
from core.capability_registry import CapabilityDescriptor
from core.permission_consent import (
    ConsentDecisionStatus,
    PermissionConsentManager,
)


class GovernedPermissionStatus(str, Enum):
    UNRESOLVED = "unresolved"
    REJECTED = "rejected"
    CONSENT_REQUIRED = "consent_required"
    POLICY_ALLOWED = "policy_allowed"


@dataclass(frozen=True)
class GovernedPermissionObservation:
    status: GovernedPermissionStatus
    reason: str
    authorized: bool = False

    def __post_init__(self) -> None:
        if type(self.status) is not GovernedPermissionStatus:
            raise ValueError("invalid permission status")
        if type(self.reason) is not str or not self.reason.strip():
            raise ValueError("invalid permission reason")
        if type(self.authorized) is not bool or self.authorized:
            raise ValueError("permission observation cannot authorize execution")


class CrossDomainGovernedPermissionAdapter:
    """Read an M63 decision without converting it into execution authority."""

    def __init__(self, permissions: PermissionConsentManager) -> None:
        if type(permissions) is not PermissionConsentManager:
            raise ValueError("a canonical M63 permission manager is required")
        self._permissions = permissions

    def evaluate(
        self,
        request: object,
        descriptor: object,
    ) -> GovernedPermissionObservation:
        if type(request) is not ExecutionAuthorizationRequest:
            return GovernedPermissionObservation(
                GovernedPermissionStatus.REJECTED,
                "invalid_authorization_request",
            )

        if type(descriptor) is not CapabilityDescriptor:
            return GovernedPermissionObservation(
                GovernedPermissionStatus.REJECTED,
                "invalid_capability_descriptor",
            )

        if descriptor.name != request.capability:
            return GovernedPermissionObservation(
                GovernedPermissionStatus.REJECTED,
                "capability_mismatch",
            )

        if descriptor.enabled is not True:
            return GovernedPermissionObservation(
                GovernedPermissionStatus.REJECTED,
                "capability_disabled",
            )

        try:
            decision = self._permissions.authorize_descriptor(descriptor)
        except (ValueError, TypeError):
            return GovernedPermissionObservation(
                GovernedPermissionStatus.UNRESOLVED,
                "permission_evaluation_failed",
            )

        if type(decision.normalized_status) is not ConsentDecisionStatus:
            return GovernedPermissionObservation(
                GovernedPermissionStatus.UNRESOLVED,
                "invalid_permission_decision",
            )

        if decision.capability_name != request.capability:
            return GovernedPermissionObservation(
                GovernedPermissionStatus.REJECTED,
                "permission_capability_mismatch",
            )

        if decision.normalized_status is ConsentDecisionStatus.DENIED:
            return GovernedPermissionObservation(
                GovernedPermissionStatus.REJECTED,
                "permission_denied",
            )

        if decision.normalized_status is ConsentDecisionStatus.REQUIRES_CONSENT:
            return GovernedPermissionObservation(
                GovernedPermissionStatus.CONSENT_REQUIRED,
                "consent_required",
            )

        if (
            decision.normalized_status is ConsentDecisionStatus.ALLOWED
            and decision.allowed is True
        ):
            return GovernedPermissionObservation(
                GovernedPermissionStatus.POLICY_ALLOWED,
                "m63_allowed_execution_authority_unverified",
            )

        return GovernedPermissionObservation(
            GovernedPermissionStatus.UNRESOLVED,
            "permission_not_verified",
        )