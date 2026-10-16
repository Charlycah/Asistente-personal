from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class ExternalResourceKind(str, Enum):
    """Broad identity class for a resource outside ROBY's cognitive core."""

    DEVICE = "device"
    CAMERA = "camera"
    SENSOR = "sensor"
    SERVICE = "service"
    NODE = "node"
    DATA_SOURCE = "data_source"
    INTERFACE = "interface"
    UNKNOWN = "unknown"


class ExternalResourceRegistryState(str, Enum):
    """Governed descriptive state for an external resource.

    State is declarative evidence owned by the registry. It never performs discovery,
    connectivity, authorization, activation or any other external operation.
    """

    KNOWN = "known"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class ExternalResourceAuthorizationState(str, Enum):
    """Governed authorization decision for a registered external resource.

    Authorization is descriptive policy only. It never authenticates, connects,
    activates or operates the resource.
    """

    UNKNOWN = "unknown"
    DENIED = "denied"
    AUTHORIZED = "authorized"


@dataclass(frozen=True)
class ExternalResourceAuthorizationDecision:
    """Explicit immutable authorization evidence for one registered resource."""

    state: ExternalResourceAuthorizationState | str
    source: str
    authorized_by: str
    decided_at: str
    reason: str = ""
    revision: int = 1

    def __post_init__(self) -> None:
        state = ExternalResourceAuthorizationState(self.state)
        source = self.source.strip()
        authorized_by = self.authorized_by.strip()
        decided_at = self.decided_at.strip()
        reason = self.reason.strip()

        if state is ExternalResourceAuthorizationState.UNKNOWN:
            raise ValueError("explicit authorization decision cannot be unknown")
        if not source:
            raise ValueError("authorization decision requires a source")
        if not authorized_by:
            raise ValueError("authorization decision requires an authorizer")
        if not decided_at:
            raise ValueError("authorization decision requires an explicit timestamp")
        if self.revision < 1:
            raise ValueError("authorization revision must be positive")

        object.__setattr__(self, "state", state)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "authorized_by", authorized_by)
        object.__setattr__(self, "decided_at", decided_at)
        object.__setattr__(self, "reason", reason)


class ExternalResourceConnectivityState(str, Enum):
    """Governed descriptive connectivity state for an external resource.

    Connectivity is declarative only. It never opens a connection or probes the
    resource.
    """

    UNKNOWN = "unknown"
    CONFIGURED = "configured"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ExternalResourceConnectivityDeclaration:
    """Immutable evidence describing how a resource could be connected."""

    state: ExternalResourceConnectivityState | str
    transport_type: str
    endpoint_reference: str
    source: str
    declared_at: str
    revision: int = 1

    def __post_init__(self) -> None:
        state = ExternalResourceConnectivityState(self.state)
        transport_type = self.transport_type.strip().casefold()
        endpoint_reference = self.endpoint_reference.strip()
        source = self.source.strip()
        declared_at = self.declared_at.strip()

        if state is ExternalResourceConnectivityState.UNKNOWN:
            raise ValueError("explicit connectivity declaration cannot be unknown")
        if not source:
            raise ValueError("connectivity declaration requires a source")
        if not declared_at:
            raise ValueError("connectivity declaration requires an explicit timestamp")
        if state is ExternalResourceConnectivityState.CONFIGURED:
            if not transport_type:
                raise ValueError("configured connectivity requires a transport type")
            if not endpoint_reference:
                raise ValueError(
                    "configured connectivity requires an endpoint reference"
                )
        if self.revision < 1:
            raise ValueError("connectivity revision must be positive")

        object.__setattr__(self, "state", state)
        object.__setattr__(self, "transport_type", transport_type)
        object.__setattr__(self, "endpoint_reference", endpoint_reference)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "declared_at", declared_at)


@dataclass(frozen=True)
class ExternalResourceAuditEvent:
    """Immutable audit evidence for one governed external-resource decision."""

    audit_id: str
    resource_id: str
    event_type: str
    previous_value: str
    new_value: str
    reason: str
    declared_by: str
    declared_at: str
    revision: int = 1

    def __post_init__(self) -> None:
        audit_id = self.audit_id.strip()
        resource_id = self.resource_id.strip()
        event_type = self.event_type.strip().casefold()
        previous_value = self.previous_value.strip()
        new_value = self.new_value.strip()
        reason = self.reason.strip()
        declared_by = self.declared_by.strip()
        declared_at = self.declared_at.strip()

        if not audit_id:
            raise ValueError("audit event requires an audit id")
        if not resource_id:
            raise ValueError("audit event requires a resource id")
        if not event_type:
            raise ValueError("audit event requires an event type")
        if not declared_by:
            raise ValueError("audit event requires a declarer")
        if not declared_at:
            raise ValueError("audit event requires an explicit timestamp")
        if self.revision < 1:
            raise ValueError("audit revision must be positive")

        object.__setattr__(self, "audit_id", audit_id)
        object.__setattr__(self, "resource_id", resource_id)
        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "previous_value", previous_value)
        object.__setattr__(self, "new_value", new_value)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "declared_by", declared_by)
        object.__setattr__(self, "declared_at", declared_at)


@dataclass(frozen=True)
class ExternalResourceIdentity:
    """Stable governed identity for one external resource.

    Identity is descriptive only. It does not authenticate, authorize, connect or
    activate the resource.
    """

    namespace: str
    local_id: str

    def __post_init__(self) -> None:
        namespace = self.namespace.strip().casefold()
        local_id = self.local_id.strip()
        if not namespace:
            raise ValueError("external resource identity requires a namespace")
        if not local_id:
            raise ValueError("external resource identity requires a local id")
        if any(character.isspace() for character in namespace):
            raise ValueError(
                "external resource identity namespace must not contain spaces"
            )

        object.__setattr__(self, "namespace", namespace)
        object.__setattr__(self, "local_id", local_id)

    @property
    def canonical_id(self) -> str:
        return f"{self.namespace}:{self.local_id}"


@dataclass(frozen=True)
class ExternalResourceRegistration:
    """Explicit declaration of a resource known to ROBY.

    Registration and state are descriptive only. A state declaration does not imply
    discovery, connectivity, authorization, activation or execution.
    """

    resource_id: str
    label: str
    kind: ExternalResourceKind | str
    source_authority: str
    external_ref: str = ""
    capabilities: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)
    state: ExternalResourceRegistryState | str = ExternalResourceRegistryState.KNOWN
    identity: ExternalResourceIdentity | None = None
    authorization_state: ExternalResourceAuthorizationState | str = (
        ExternalResourceAuthorizationState.UNKNOWN
    )
    authorization_history: tuple[ExternalResourceAuthorizationDecision, ...] = ()
    connectivity_state: ExternalResourceConnectivityState | str = (
        ExternalResourceConnectivityState.UNKNOWN
    )
    connectivity_history: tuple[ExternalResourceConnectivityDeclaration, ...] = ()

    def __post_init__(self) -> None:
        resource_id = self.resource_id.strip()
        label = self.label.strip()
        source_authority = self.source_authority.strip()
        external_ref = self.external_ref.strip()
        if not resource_id:
            raise ValueError("external resource registration requires a resource id")
        if not label:
            raise ValueError("external resource registration requires a label")
        if not source_authority:
            raise ValueError(
                "external resource registration requires a source authority"
            )

        kind = ExternalResourceKind(self.kind)
        state = ExternalResourceRegistryState(self.state)
        authorization_state = ExternalResourceAuthorizationState(
            self.authorization_state
        )
        authorization_history = tuple(self.authorization_history)
        connectivity_state = ExternalResourceConnectivityState(self.connectivity_state)
        connectivity_history = tuple(self.connectivity_history)
        if authorization_history:
            revisions = tuple(item.revision for item in authorization_history)
            if revisions != tuple(range(1, len(authorization_history) + 1)):
                raise ValueError("authorization history revisions must be contiguous")
            if authorization_history[-1].state is not authorization_state:
                raise ValueError("authorization state must match latest decision")
        elif authorization_state is not ExternalResourceAuthorizationState.UNKNOWN:
            raise ValueError("explicit authorization state requires decision history")

        if connectivity_history:
            revisions = tuple(item.revision for item in connectivity_history)
            if revisions != tuple(range(1, len(connectivity_history) + 1)):
                raise ValueError("connectivity history revisions must be contiguous")
            if connectivity_history[-1].state is not connectivity_state:
                raise ValueError("connectivity state must match latest declaration")
        elif connectivity_state is not ExternalResourceConnectivityState.UNKNOWN:
            raise ValueError("explicit connectivity state requires declaration history")

        capabilities = tuple(item.strip().casefold() for item in self.capabilities)
        if any(not item for item in capabilities):
            raise ValueError("external resource capabilities must not contain blanks")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("external resource capabilities must be unique")

        normalized_metadata: dict[str, str] = {}
        for key, value in self.metadata.items():
            normalized_key = key.strip()
            normalized_value = value.strip()
            if not normalized_key or not normalized_value:
                raise ValueError("external resource metadata must not contain blanks")
            if normalized_key in normalized_metadata:
                raise ValueError("external resource metadata keys must be unique")
            normalized_metadata[normalized_key] = normalized_value

        object.__setattr__(self, "resource_id", resource_id)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "source_authority", source_authority)
        object.__setattr__(self, "external_ref", external_ref)
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(sorted(normalized_metadata.items()))),
        )
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "authorization_state", authorization_state)
        object.__setattr__(self, "authorization_history", authorization_history)
        object.__setattr__(self, "connectivity_state", connectivity_state)
        object.__setattr__(self, "connectivity_history", connectivity_history)
        identity = self.identity or ExternalResourceIdentity(
            namespace="roby.external",
            local_id=resource_id,
        )
        object.__setattr__(self, "identity", identity)


class ExternalResourceRecoveryStatus(str, Enum):
    """Evidence level available for a safe cognitive recovery snapshot."""

    REGISTERED_ONLY = "registered_only"
    AUDITED = "audited"


@dataclass(frozen=True)
class ExternalResourceRecoverySnapshot:
    """Immutable read-only reconstruction of governed resource knowledge."""

    authority_id: str
    resource: ExternalResourceRegistration
    recovery_status: ExternalResourceRecoveryStatus | str
    audit_revision: int
    latest_audit_id: str = ""

    def __post_init__(self) -> None:
        authority_id = self.authority_id.strip()
        recovery_status = ExternalResourceRecoveryStatus(self.recovery_status)
        latest_audit_id = self.latest_audit_id.strip()
        if not authority_id:
            raise ValueError("recovery snapshot requires an authority id")
        if self.audit_revision < 0:
            raise ValueError("recovery audit revision cannot be negative")
        if self.audit_revision == 0 and latest_audit_id:
            raise ValueError("unaudited recovery cannot reference an audit event")
        if self.audit_revision > 0 and not latest_audit_id:
            raise ValueError("audited recovery requires the latest audit id")
        if recovery_status is ExternalResourceRecoveryStatus.REGISTERED_ONLY:
            if self.audit_revision != 0:
                raise ValueError(
                    "registered-only recovery cannot include audit evidence"
                )
        elif self.audit_revision == 0:
            raise ValueError("audited recovery requires audit evidence")

        object.__setattr__(self, "authority_id", authority_id)
        object.__setattr__(self, "recovery_status", recovery_status)
        object.__setattr__(self, "latest_audit_id", latest_audit_id)


@dataclass(frozen=True)
class ExternalResourceRegistrySnapshot:
    authority_id: str
    resources: tuple[ExternalResourceRegistration, ...]


class ExternalResourceRegistryAuthority:
    """Canonical M394 authority for explicit external-resource registration."""

    authority_id = "external_resource_registry"

    def __init__(self) -> None:
        self._resources: dict[str, ExternalResourceRegistration] = {}
        self._identity_index: dict[str, str] = {}
        self._audit_events: dict[str, tuple[ExternalResourceAuditEvent, ...]] = {}

    def register(
        self, registration: ExternalResourceRegistration
    ) -> ExternalResourceRegistration:
        if registration.resource_id in self._resources:
            raise ValueError("external resource is already registered")
        canonical_id = registration.identity.canonical_id
        if canonical_id in self._identity_index:
            raise ValueError("external resource identity is already registered")
        self._resources[registration.resource_id] = registration
        self._identity_index[canonical_id] = registration.resource_id
        return registration

    def get(self, resource_id: str) -> ExternalResourceRegistration | None:
        return self._resources.get(resource_id.strip())

    def resolve_identity(
        self, identity: ExternalResourceIdentity
    ) -> ExternalResourceRegistration | None:
        resource_id = self._identity_index.get(identity.canonical_id)
        if resource_id is None:
            return None
        return self._resources[resource_id]

    def declare_state(
        self,
        resource_id: str,
        state: ExternalResourceRegistryState | str,
    ) -> ExternalResourceRegistration:
        """Declare descriptive state without probing or operating the resource."""

        normalized_resource_id = resource_id.strip()
        registration = self._resources.get(normalized_resource_id)
        if registration is None:
            raise KeyError("external resource is not registered")

        governed_state = ExternalResourceRegistryState(state)
        if governed_state is registration.state:
            return registration

        updated = replace(registration, state=governed_state)
        self._resources[normalized_resource_id] = updated
        return updated

    def authorize(
        self,
        resource_id: str,
        *,
        source: str,
        authorized_by: str,
        authorized_at: str,
        reason: str = "",
    ) -> ExternalResourceRegistration:
        """Record explicit authorization without operating the resource."""

        return self._record_authorization(
            resource_id,
            state=ExternalResourceAuthorizationState.AUTHORIZED,
            source=source,
            authorized_by=authorized_by,
            decided_at=authorized_at,
            reason=reason,
        )

    def revoke_authorization(
        self,
        resource_id: str,
        *,
        source: str,
        authorized_by: str,
        authorized_at: str,
        reason: str = "",
    ) -> ExternalResourceRegistration:
        """Record explicit denial/revocation without external side effects."""

        return self._record_authorization(
            resource_id,
            state=ExternalResourceAuthorizationState.DENIED,
            source=source,
            authorized_by=authorized_by,
            decided_at=authorized_at,
            reason=reason,
        )

    def authorization_state(
        self, resource_id: str
    ) -> ExternalResourceAuthorizationState:
        registration = self._require_resource(resource_id)
        return registration.authorization_state

    def authorization_history(
        self, resource_id: str
    ) -> tuple[ExternalResourceAuthorizationDecision, ...]:
        registration = self._require_resource(resource_id)
        return registration.authorization_history

    def declare_connectivity(
        self,
        resource_id: str,
        *,
        state: ExternalResourceConnectivityState | str,
        transport_type: str = "",
        endpoint_reference: str = "",
        source: str,
        declared_at: str,
    ) -> ExternalResourceRegistration:
        """Record descriptive connectivity without opening any connection."""

        registration = self._require_resource(resource_id)
        declaration = ExternalResourceConnectivityDeclaration(
            state=state,
            transport_type=transport_type,
            endpoint_reference=endpoint_reference,
            source=source,
            declared_at=declared_at,
            revision=len(registration.connectivity_history) + 1,
        )
        updated = replace(
            registration,
            connectivity_state=declaration.state,
            connectivity_history=registration.connectivity_history + (declaration,),
        )
        self._resources[registration.resource_id] = updated
        return updated

    def connectivity_state(
        self, resource_id: str
    ) -> ExternalResourceConnectivityState:
        return self._require_resource(resource_id).connectivity_state

    def connectivity_history(
        self, resource_id: str
    ) -> tuple[ExternalResourceConnectivityDeclaration, ...]:
        return self._require_resource(resource_id).connectivity_history

    def connection_profile(
        self, resource_id: str
    ) -> ExternalResourceConnectivityDeclaration | None:
        history = self._require_resource(resource_id).connectivity_history
        if not history:
            return None
        latest = history[-1]
        if latest.state is not ExternalResourceConnectivityState.CONFIGURED:
            return None
        return latest

    def record_audit_event(
        self,
        resource_id: str,
        *,
        event_type: str,
        previous_value: str = "",
        new_value: str = "",
        reason: str = "",
        declared_by: str,
        declared_at: str,
    ) -> ExternalResourceAuditEvent:
        """Append immutable audit evidence without modifying the resource."""

        registration = self._require_resource(resource_id)
        history = self._audit_events.get(registration.resource_id, ())
        revision = len(history) + 1
        event = ExternalResourceAuditEvent(
            audit_id=f"{registration.resource_id}:audit:{revision}",
            resource_id=registration.resource_id,
            event_type=event_type,
            previous_value=previous_value,
            new_value=new_value,
            reason=reason,
            declared_by=declared_by,
            declared_at=declared_at,
            revision=revision,
        )
        self._audit_events[registration.resource_id] = history + (event,)
        return event

    def audit_history(
        self, resource_id: str
    ) -> tuple[ExternalResourceAuditEvent, ...]:
        registration = self._require_resource(resource_id)
        return self._audit_events.get(registration.resource_id, ())

    def latest_audit(self, resource_id: str) -> ExternalResourceAuditEvent | None:
        history = self.audit_history(resource_id)
        return history[-1] if history else None

    def audit_revision(self, resource_id: str) -> int:
        return len(self.audit_history(resource_id))

    def recover_resource_snapshot(
        self, resource_id: str
    ) -> ExternalResourceRecoverySnapshot:
        """Reconstruct current governed knowledge without external side effects."""

        registration = self._require_resource(resource_id)
        history = self.audit_history(registration.resource_id)
        if history:
            status = ExternalResourceRecoveryStatus.AUDITED
            latest_audit_id = history[-1].audit_id
        else:
            status = ExternalResourceRecoveryStatus.REGISTERED_ONLY
            latest_audit_id = ""
        return ExternalResourceRecoverySnapshot(
            authority_id=self.authority_id,
            resource=registration,
            recovery_status=status,
            audit_revision=len(history),
            latest_audit_id=latest_audit_id,
        )

    def validate_recovery(
        self, snapshot: ExternalResourceRecoverySnapshot
    ) -> bool:
        """Validate a recovery snapshot against current governed knowledge."""

        if snapshot.authority_id != self.authority_id:
            return False
        registration = self.get(snapshot.resource.resource_id)
        if registration != snapshot.resource:
            return False
        history = self.audit_history(snapshot.resource.resource_id)
        if snapshot.audit_revision != len(history):
            return False
        expected_audit_id = history[-1].audit_id if history else ""
        if snapshot.latest_audit_id != expected_audit_id:
            return False
        expected_status = (
            ExternalResourceRecoveryStatus.AUDITED
            if history
            else ExternalResourceRecoveryStatus.REGISTERED_ONLY
        )
        return snapshot.recovery_status is expected_status

    def _require_resource(self, resource_id: str) -> ExternalResourceRegistration:
        normalized_resource_id = resource_id.strip()
        registration = self._resources.get(normalized_resource_id)
        if registration is None:
            raise KeyError("external resource is not registered")
        return registration

    def _record_authorization(
        self,
        resource_id: str,
        *,
        state: ExternalResourceAuthorizationState,
        source: str,
        authorized_by: str,
        decided_at: str,
        reason: str,
    ) -> ExternalResourceRegistration:
        registration = self._require_resource(resource_id)
        decision = ExternalResourceAuthorizationDecision(
            state=state,
            source=source,
            authorized_by=authorized_by,
            decided_at=decided_at,
            reason=reason,
            revision=len(registration.authorization_history) + 1,
        )
        updated = replace(
            registration,
            authorization_state=state,
            authorization_history=registration.authorization_history + (decision,),
        )
        self._resources[registration.resource_id] = updated
        return updated

    def list_resources(self) -> tuple[ExternalResourceRegistration, ...]:
        return tuple(
            sorted(
                self._resources.values(),
                key=lambda item: (item.label.casefold(), item.resource_id),
            )
        )

    def snapshot(self) -> ExternalResourceRegistrySnapshot:
        return ExternalResourceRegistrySnapshot(
            authority_id=self.authority_id,
            resources=self.list_resources(),
        )
