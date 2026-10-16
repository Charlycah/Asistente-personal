from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LearningAuthorityContract:
    authority: str
    parent_authority: str
    schema_version: str
    read_only: bool
    runtime_connected: bool
    persistence_added: bool
    automatic_application: bool

    def __post_init__(self) -> None:
        if not self.authority.strip():
            raise ValueError("learning authority must not be blank")
        if not self.parent_authority.strip():
            raise ValueError("learning parent authority must not be blank")
        if not self.schema_version.strip():
            raise ValueError("learning schema version must not be blank")


@dataclass(frozen=True)
class LearningStabilizationReport:
    schema_version: str
    release: str
    authorities: tuple[LearningAuthorityContract, ...]
    authority_chain: tuple[str, ...]
    authority_names_unique: bool
    parent_chain_valid: bool
    read_only_boundary: bool
    runtime_isolated: bool
    persistence_absent: bool
    automatic_application_absent: bool
    integration_invariants_verified: bool
    series_closed: bool

    def __post_init__(self) -> None:
        names = tuple(item.authority for item in self.authorities)
        if len(names) != len(set(names)):
            raise ValueError("learning stabilization authorities must be unique")
        if names != self.authority_chain:
            raise ValueError("learning authority chain must match audited authorities")
        checks = (
            self.authority_names_unique,
            self.parent_chain_valid,
            self.read_only_boundary,
            self.runtime_isolated,
            self.persistence_absent,
            self.automatic_application_absent,
            self.integration_invariants_verified,
            self.series_closed,
        )
        if not all(checks):
            raise ValueError("learning stabilization requires every audit to pass")
