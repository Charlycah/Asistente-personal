from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class InternalWorldDomain(StrEnum):
    SELF = "self"
    USER = "user"
    PROJECTS = "projects"
    GOALS = "goals"
    CONTEXT = "context"
    RELATIONSHIPS = "relationships"
    MEMORY = "memory"
    CAPABILITIES = "capabilities"
    ENVIRONMENT = "environment"
    CONSTRAINTS = "constraints"


@dataclass(frozen=True)
class InternalWorldAuthority:
    domain: InternalWorldDomain
    authority_key: str
    implementation_path: str
    purpose: str
    runtime_connected: bool
    persistent: bool

    def __post_init__(self) -> None:
        if not self.authority_key.strip():
            raise ValueError("authority key must not be blank")
        if ":" not in self.implementation_path:
            raise ValueError("implementation path must use module:Symbol form")
        if not self.purpose.strip():
            raise ValueError("authority purpose must not be blank")


@dataclass(frozen=True)
class InternalWorldModelSnapshot:
    schema_version: str
    canonical_authority: str
    authorities: tuple[InternalWorldAuthority, ...]
    supported_domains: tuple[InternalWorldDomain, ...]
    read_only: bool
    inference_added: bool
    persistence_added: bool
    runtime_behavior_changed: bool
    consciousness_claimed: bool

    def authority_for(
        self, domain: InternalWorldDomain | str
    ) -> InternalWorldAuthority:
        normalized = InternalWorldDomain(domain)
        return next(item for item in self.authorities if item.domain is normalized)
