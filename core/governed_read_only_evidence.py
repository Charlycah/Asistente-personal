from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GovernedReadOnlyEvidenceRequest:
    """One bounded read request with exact authorization/planning lineage."""

    authorization_id: str
    requirement_id: str
    plan_id: str
    capability_name: str
    evidence_description: str
    declared_evidence_output: str
    source_reference: str
    world_snapshot_id: str
    max_attempts: int = 1
    read_only: bool = True
    permits_retry: bool = False
    permits_follow_up_execution: bool = False

    def __post_init__(self) -> None:
        for value, label in (
            (self.authorization_id, "authorization id"),
            (self.requirement_id, "requirement id"),
            (self.plan_id, "plan id"),
            (self.capability_name, "capability name"),
            (self.evidence_description, "evidence description"),
            (self.declared_evidence_output, "declared evidence output"),
            (self.source_reference, "source reference"),
            (self.world_snapshot_id, "world snapshot id"),
        ):
            if not value.strip():
                raise ValueError(f"read-only evidence {label} must not be blank")
        if self.max_attempts != 1:
            raise ValueError("read-only evidence request permits exactly one attempt")
        if not self.read_only or self.permits_retry or self.permits_follow_up_execution:
            raise ValueError("read-only evidence request violates bounded execution")


@dataclass(frozen=True)
class GovernedReadOnlyEvidenceObservation:
    """Raw read observation returned by one registered evidence reader."""

    evidence_output: str
    value: object
    source_reference: str
    rationale_codes: tuple[str, ...] = ()
    establishes_truth: bool = False
    modifies_state: bool = False

    def __post_init__(self) -> None:
        if not self.evidence_output.strip() or not self.source_reference.strip():
            raise ValueError("read-only evidence observation requires source identity")
        if any(not code.strip() for code in self.rationale_codes):
            raise ValueError("read-only evidence rationale codes must not be blank")
        if self.establishes_truth or self.modifies_state:
            raise ValueError(
                "read-only observation cannot establish truth or modify state"
            )
