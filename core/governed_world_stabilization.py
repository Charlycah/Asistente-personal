from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from core.governed_world_integration import GovernedWorldIntegrationSnapshot


class WorldStabilizationStatus(StrEnum):
    STABLE = "stable"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedWorldStabilizationReport:
    status: WorldStabilizationStatus
    checked_domains: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    integration_fingerprint: str
    schema_version: str = "m392.8"
    canonical_authority: str = "internal_world_model"
    read_only: bool = True
    persistence_added: bool = False
    inference_added: bool = False
    source_data_modified: bool = False
    authority_added: bool = False
    automation_added: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "internal_world_model":
            raise ValueError("world stabilization must preserve world authority")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.inference_added,
                self.source_data_modified,
                self.authority_added,
                self.automation_added,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("world stabilization violates governed limits")


class GovernedWorldStabilizationDiagnostic:
    """Read-only audit of the integrated M392 world-model lineage."""

    _EXPECTED_VERSIONS = (
        ("household", "m392.1"),
        ("people", "m392.2"),
        ("places", "m392.3"),
        ("objects", "m392.4"),
        ("timeline", "m392.5"),
        ("context", "m392.6"),
    )

    def inspect(
        self,
        snapshot: GovernedWorldIntegrationSnapshot,
    ) -> GovernedWorldStabilizationReport:
        risks: list[str] = []
        evidence: list[str] = [
            "authority:internal_world_model",
            "integration:m392.7",
            "stabilization:diagnostic_only",
        ]

        if snapshot.schema_version != "m392.7":
            risks.append("integration_schema_mismatch")
        if snapshot.canonical_authority != "internal_world_model":
            risks.append("integration_authority_mismatch")
        if not snapshot.source_fingerprint:
            risks.append("integration_fingerprint_missing")

        for domain_name, expected_version in self._EXPECTED_VERSIONS:
            domain = getattr(snapshot, domain_name)
            evidence.append(f"domain:{domain_name}:{expected_version}")
            if domain.schema_version != expected_version:
                risks.append(f"domain_schema_mismatch:{domain_name}")
            if domain.canonical_authority != snapshot.canonical_authority:
                risks.append(f"domain_authority_mismatch:{domain_name}")
            if not domain.source_fingerprint:
                risks.append(f"domain_fingerprint_missing:{domain_name}")
            status = str(domain.status.value)
            if status == "review_required":
                risks.append(f"domain_review_required:{domain_name}")

        for code in snapshot.risk_codes:
            if code not in risks:
                risks.append(code)

        risk_codes = tuple(sorted(set(risks)))
        return GovernedWorldStabilizationReport(
            status=(
                WorldStabilizationStatus.REVIEW_REQUIRED
                if risk_codes
                else WorldStabilizationStatus.STABLE
            ),
            checked_domains=tuple(name for name, _ in self._EXPECTED_VERSIONS),
            evidence_codes=tuple(evidence),
            risk_codes=risk_codes,
            integration_fingerprint=snapshot.source_fingerprint,
        )
