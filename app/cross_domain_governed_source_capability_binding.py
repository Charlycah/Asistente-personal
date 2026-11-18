"""Non-authorizing structural binding of governed sources to M62 capabilities."""

from dataclasses import dataclass
from enum import Enum

from app.cross_domain_execution_authorization import ExecutionAuthorizationRequest
from app.governed_information_sources import InformationSourceStatus
from app.governed_source_query import GovernedSourceQueryContract
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


class SourceCapabilityBindingDecision(str, Enum):
    BOUND = "bound"
    REJECTED = "rejected"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class SourceCapabilityAssociation:
    source_id: str
    capability: str

    def __post_init__(self) -> None:
        for field in ("source_id", "capability"):
            value = getattr(self, field)
            if type(value) is not str or not value or value != value.strip():
                raise ValueError(f"invalid association field: {field}")


@dataclass(frozen=True)
class SourceCapabilityBindingResult:
    decision: SourceCapabilityBindingDecision
    reason: str
    authorized: bool = False

    def __post_init__(self) -> None:
        if type(self.decision) is not SourceCapabilityBindingDecision:
            raise ValueError("invalid source capability binding decision")
        if type(self.reason) is not str or not self.reason.strip():
            raise ValueError("invalid source capability binding reason")
        if type(self.authorized) is not bool or self.authorized:
            raise ValueError("source capability binding cannot authorize execution")


class CrossDomainGovernedSourceCapabilityBinding:
    """Observe explicit associations without granting execution authority."""

    def __init__(
        self,
        sources: GovernedSourceQueryContract,
        registry: OfficialRuntimeCapabilityRegistry,
        associations: tuple[SourceCapabilityAssociation, ...],
    ) -> None:
        if type(sources) is not GovernedSourceQueryContract:
            raise ValueError("canonical source contract required")
        if type(registry) is not OfficialRuntimeCapabilityRegistry:
            raise ValueError("official runtime registry required")
        if type(associations) is not tuple:
            raise ValueError("immutable association tuple required")
        if any(type(item) is not SourceCapabilityAssociation for item in associations):
            raise ValueError("invalid source capability association")
        self._sources = sources
        self._registry = registry
        normalized_pairs = tuple(
            (item.source_id.casefold(), item.capability)
            for item in associations
        )
        if len(normalized_pairs) != len(set(normalized_pairs)):
            raise ValueError("duplicate source capability association")
        self._associations = frozenset(normalized_pairs)

    def evaluate(self, request: object) -> SourceCapabilityBindingResult:
        if type(request) is not ExecutionAuthorizationRequest:
            return SourceCapabilityBindingResult(
                SourceCapabilityBindingDecision.REJECTED,
                "invalid_request",
            )

        try:
            source = self._sources.source_for(request.source_id)
        except KeyError:
            return SourceCapabilityBindingResult(
                SourceCapabilityBindingDecision.UNRESOLVED,
                "source_not_registered",
            )

        if source.status is not InformationSourceStatus.DECLARED:
            return SourceCapabilityBindingResult(
                SourceCapabilityBindingDecision.REJECTED,
                "source_disabled",
            )

        if source.source_id.casefold() != request.source_id.casefold():
            return SourceCapabilityBindingResult(
                SourceCapabilityBindingDecision.REJECTED,
                "source_identity_mismatch",
            )

        registration = self._registry.registration_for(request.capability)
        if registration is None:
            return SourceCapabilityBindingResult(
                SourceCapabilityBindingDecision.UNRESOLVED,
                "capability_not_registered",
            )

        descriptor = registration.descriptor
        canonical = self._registry.manager.get(request.capability)

        if descriptor.name != request.capability or canonical is not descriptor:
            return SourceCapabilityBindingResult(
                SourceCapabilityBindingDecision.REJECTED,
                "capability_identity_mismatch",
            )

        if descriptor.enabled is not True:
            return SourceCapabilityBindingResult(
                SourceCapabilityBindingDecision.REJECTED,
                "capability_disabled",
            )

        pair = (request.source_id.casefold(), request.capability)
        if pair not in self._associations:
            return SourceCapabilityBindingResult(
                SourceCapabilityBindingDecision.REJECTED,
                "association_not_declared",
            )

        return SourceCapabilityBindingResult(
            SourceCapabilityBindingDecision.BOUND,
            "declared_structural_association_only",
        )
