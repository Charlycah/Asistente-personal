from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.capability_registry import CapabilityDescriptor
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.permission_consent import (
    ConsentDecisionStatus,
    PermissionConsentManager,
    PermissionGrant,
)


@dataclass(frozen=True)
class GovernedCapabilityRoutingSnapshot:
    evaluations: int
    grants: tuple[str, ...]
    last_capability: str | None
    last_status: str | None
    last_action: str | None


class OfficialGovernedCapabilityRoutingRuntimeGateway:
    """Explicit, permission-first routing over the official capability registry."""

    _ROUTE_PREFIXES = (
        "usar capacidad ",
        "usa capacidad ",
        "enrutar capacidad ",
        "enruta capacidad ",
        "activar capacidad ",
        "activa capacidad ",
    )
    _GRANT_PREFIXES = (
        "autorizar capacidad ",
        "autoriza capacidad ",
        "conceder capacidad ",
        "concede capacidad ",
    )
    _REVOKE_PREFIXES = (
        "revocar capacidad ",
        "revoca capacidad ",
    )
    _DISCOVER_PREFIXES = (
        "buscar capacidad para ",
        "busca capacidad para ",
        "qué capacidad sirve para ",
        "que capacidad sirve para ",
    )
    _STATUS_TRIGGERS = (
        "estado del enrutamiento de capacidades",
        "estado del runtime de enrutamiento de capacidades",
    )
    _AUDIT_TRIGGERS = (
        "audita enrutamiento de capacidades",
        "auditá enrutamiento de capacidades",
    )

    def __init__(
        self,
        registry,
        *,
        permissions: PermissionConsentManager | None = None,
    ) -> None:
        self.registry = registry
        self.permissions = permissions or PermissionConsentManager()
        self._evaluations = 0
        self._last_capability: str | None = None
        self._last_status: str | None = None
        self._last_action: str | None = None

    @property
    def snapshot(self) -> GovernedCapabilityRoutingSnapshot:
        return GovernedCapabilityRoutingSnapshot(
            evaluations=self._evaluations,
            grants=tuple(sorted(self.permissions.grants)),
            last_capability=self._last_capability,
            last_status=self._last_status,
            last_action=self._last_action,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        normalized = request.text.strip().casefold()
        if normalized in self._STATUS_TRIGGERS:
            return self._status_response()
        if normalized in self._AUDIT_TRIGGERS:
            return self._audit_response()

        name = self._suffix(normalized, self._GRANT_PREFIXES)
        if name is not None:
            return self._grant(name, request.owner, now)
        name = self._suffix(normalized, self._REVOKE_PREFIXES)
        if name is not None:
            return self._revoke(name)
        query = self._suffix(normalized, self._DISCOVER_PREFIXES)
        if query is not None:
            return self._discover(query)
        name = self._suffix(normalized, self._ROUTE_PREFIXES)
        if name is not None:
            return self._route(name, request, now)
        return None

    def _route(
        self,
        name: str,
        request,
        now: datetime,
    ) -> GovernedOperationalInterception:
        registration = self.registry.registration_for(name)
        self._evaluations += 1
        self._last_capability = name
        self._last_action = "route"
        if registration is None or not registration.descriptor.enabled:
            self._last_status = "not_available"
            return GovernedOperationalInterception(
                response_text=f"La capacidad '{name}' no está disponible.",
                rationale="governed_capability_route_not_available",
            )

        decision = self.permissions.authorize_descriptor(registration.descriptor)
        self._last_status = decision.normalized_status.value
        if decision.normalized_status is ConsentDecisionStatus.REQUIRES_CONSENT:
            return GovernedOperationalInterception(
                response_text=(
                    f"La capacidad '{name}' requiere consentimiento explícito. "
                    f"Usá: autorizar capacidad {name}"
                ),
                rationale="governed_capability_route_consent_required",
            )
        if not decision.allowed:
            return GovernedOperationalInterception(
                response_text=f"La capacidad '{name}' fue denegada por la política.",
                rationale="governed_capability_route_denied",
            )

        if registration.interceptor is self:
            self._last_status = "authorized"
            return GovernedOperationalInterception(
                response_text=f"Capacidad '{name}' autorizada y activa.",
                rationale="governed_capability_route_authorized",
            )

        delegated = self.registry.execute_registration(
            registration, request, now=now, origin="governed_routing"
        )
        if delegated is not None:
            self._last_status = "delegated"
            return delegated
        self._last_status = "authorized"
        return GovernedOperationalInterception(
            response_text=(
                f"Capacidad '{name}' autorizada y seleccionada. "
                "No se ejecutó ninguna operación porque falta una solicitud "
                "estructurada compatible con su adaptador."
            ),
            rationale="governed_capability_route_authorized_no_execution",
        )

    def _grant(
        self,
        name: str,
        owner: str,
        now: datetime,
    ) -> GovernedOperationalInterception:
        registration = self.registry.registration_for(name)
        self._evaluations += 1
        self._last_capability = name
        self._last_action = "grant"
        if registration is None:
            self._last_status = "not_available"
            return GovernedOperationalInterception(
                response_text=f"No se puede autorizar '{name}': no está registrada.",
                rationale="governed_capability_grant_not_available",
            )
        descriptor: CapabilityDescriptor = registration.descriptor
        self.permissions.grant(
            PermissionGrant(
                capability_name=descriptor.name,
                scope=descriptor.normalized_permission_scope,
                granted_by=owner,
                reason="explicit_conversation_consent",
                granted_at=now,
            )
        )
        self._last_status = "granted"
        return GovernedOperationalInterception(
            response_text=(
                f"Consentimiento registrado para '{name}' con alcance "
                f"'{descriptor.normalized_permission_scope.value}'."
            ),
            rationale="governed_capability_grant_completed",
        )

    def _revoke(self, name: str) -> GovernedOperationalInterception:
        self._evaluations += 1
        self._last_capability = name
        self._last_action = "revoke"
        self.permissions.revoke(name)
        self._last_status = "revoked"
        return GovernedOperationalInterception(
            response_text=f"Consentimiento revocado para '{name}'.",
            rationale="governed_capability_revoke_completed",
        )

    def _discover(self, query: str) -> GovernedOperationalInterception:
        self._evaluations += 1
        self._last_action = "discover"
        matches = self.registry.manager.semantic_search(query)
        if not matches:
            self._last_capability = None
            self._last_status = "no_match"
            return GovernedOperationalInterception(
                response_text=(
                    "No encontré una capacidad habilitada para esa solicitud."
                ),
                rationale="governed_capability_discovery_no_match",
            )
        names = tuple(item.name for item in matches if item.enabled)
        self._last_capability = names[0] if names else None
        self._last_status = "matched" if names else "no_match"
        response = "\n".join(
            ("Capacidades candidatas:", *(f"- {name}" for name in names))
        )
        return GovernedOperationalInterception(
            response_text=response,
            rationale="governed_capability_discovery_completed",
        )

    def _status_response(self) -> GovernedOperationalInterception:
        snapshot = self.snapshot
        return GovernedOperationalInterception(
            response_text="\n".join(
                (
                    "Estado del Governed Capability Routing Runtime:",
                    f"- Evaluaciones: {snapshot.evaluations}",
                    f"- Permisos activos: {len(snapshot.grants)}",
                    f"- Última capacidad: {snapshot.last_capability or 'ninguna'}",
                    f"- Último estado: {snapshot.last_status or 'ninguno'}",
                    "- Modo: explícito, permission-first y sin ejecución implícita.",
                )
            ),
            rationale="governed_capability_routing_status_completed",
        )

    def _audit_response(self) -> GovernedOperationalInterception:
        return GovernedOperationalInterception(
            response_text="\n".join(
                (
                    "Auditoría del Governed Capability Routing Runtime:",
                    "- Descubrimiento: usa descriptores semánticos del registro M62.",
                    "- Autorización: usa permisos y consentimiento M63.",
                    "- Activación: solo mediante solicitud explícita por nombre.",
                    "- Capacidades sensibles: requieren consentimiento previo.",
                    "- Coincidencias semánticas: nunca ejecutan adapters por sí solas.",
                )
            ),
            rationale="governed_capability_routing_audit_completed",
        )

    @staticmethod
    def _suffix(text: str, prefixes: tuple[str, ...]) -> str | None:
        for prefix in prefixes:
            if text.startswith(prefix):
                value = text[len(prefix) :].strip()
                return value or None
        return None
