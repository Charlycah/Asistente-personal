from __future__ import annotations

from typing import Protocol

from .epistemic import EpistemicLevel


class StatusView(Protocol):
    value: str


class ExecutiveFindingView(Protocol):
    finding_code: str
    source_authority: str
    source_reference: str
    epistemic_level: EpistemicLevel
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]


class ExecutiveReportView(Protocol):
    report_id: str
    status: StatusView
    findings: tuple[ExecutiveFindingView, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]


class PeriodicReflectionView(Protocol):
    report_id: str
    status: StatusView
    open_matter_count: int
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
