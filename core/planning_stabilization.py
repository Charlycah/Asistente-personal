from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanningAuthorityContract:
    authority: str
    parent_authority: str
    schema_version: str
    runtime_connected: bool
    persistence_added: bool
    execution_authorized: bool

    def __post_init__(self) -> None:
        if not self.authority.strip():
            raise ValueError("planning authority must not be blank")
        if not self.parent_authority.strip():
            raise ValueError("planning parent authority must not be blank")
        if not self.schema_version.strip():
            raise ValueError("planning schema version must not be blank")


@dataclass(frozen=True)
class PlanningStabilizationReport:
    schema_version: str
    release: str
    authorities: tuple[PlanningAuthorityContract, ...]
    authority_chain: tuple[str, ...]
    authority_names_unique: bool
    parent_chain_valid: bool
    runtime_isolated: bool
    persistence_absent: bool
    execution_absent: bool
    integration_invariants_verified: bool
    series_closed: bool

    def __post_init__(self) -> None:
        names = tuple(item.authority for item in self.authorities)
        if len(names) != len(set(names)):
            raise ValueError("planning stabilization authorities must be unique")
        if names != self.authority_chain:
            raise ValueError("planning authority chain must match audited authorities")
        if not all(
            (
                self.authority_names_unique,
                self.parent_chain_valid,
                self.runtime_isolated,
                self.persistence_absent,
                self.execution_absent,
                self.integration_invariants_verified,
                self.series_closed,
            )
        ):
            raise ValueError("planning stabilization requires every audit to pass")
