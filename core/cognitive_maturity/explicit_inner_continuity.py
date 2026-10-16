from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .simulated_inner_state import (
    SIMULATION_DISCLOSURE,
    SimulatedInnerStateSnapshot,
    SimulatedInnerStateStatus,
)


class ExplicitInnerContinuityStatus(str, Enum):
    COMPLETE = "complete"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


class ExplicitInnerContinuityKind(str, Enum):
    UNCHANGED = "unchanged"
    CHANGED = "changed"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class ExplicitInnerContinuityReport:
    report_id: str
    status: ExplicitInnerContinuityStatus
    continuity: ExplicitInnerContinuityKind
    previous_snapshot_id: str | None
    current_snapshot_id: str | None
    changed_fields: tuple[str, ...]
    unchanged_fields: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    uncertainty_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    simulation_disclosure: str = SIMULATION_DISCLOSURE
    schema_version: str = "m390.3"
    read_only: bool = True
    explicit_inputs_only: bool = True
    persists_state: bool = False
    infers_missing_history: bool = False
    uses_clock: bool = False
    creates_memory: bool = False
    modifies_learning: bool = False
    modifies_personality: bool = False
    executes_action: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("explicit-inner-continuity-"):
            raise ValueError("explicit inner-continuity identifier is invalid")
        if self.simulation_disclosure != SIMULATION_DISCLOSURE:
            raise ValueError("inner continuity must preserve simulation disclosure")
        if not self.read_only or not self.explicit_inputs_only or self.persists_state:
            raise ValueError("inner continuity must remain explicit and transient")
        if self.infers_missing_history or self.uses_clock:
            raise ValueError("inner continuity cannot infer hidden temporal history")
        if any(
            (
                self.creates_memory,
                self.modifies_learning,
                self.modifies_personality,
                self.executes_action,
            )
        ):
            raise ValueError("inner continuity cannot modify governed domains")


class ExplicitInnerContinuityEvaluator:
    """Pure comparison of two explicitly supplied simulated-state snapshots."""

    evaluator_id = "explicit_inner_continuity"

    _FIELDS = (
        "affective_tone",
        "activation_level",
        "stability_level",
        "concern_level",
        "relational_openness",
        "dominant_state",
    )

    def compare(
        self,
        previous: SimulatedInnerStateSnapshot | None,
        current: SimulatedInnerStateSnapshot | None,
    ) -> ExplicitInnerContinuityReport:
        if previous is None or current is None:
            return self._insufficient(previous, current)
        if (
            previous.status is SimulatedInnerStateStatus.DEGRADED
            or current.status is SimulatedInnerStateStatus.DEGRADED
        ):
            return self._degraded(previous, current)

        changed_fields = tuple(
            field
            for field in self._FIELDS
            if getattr(previous, field) != getattr(current, field)
        )
        unchanged_fields = tuple(
            field for field in self._FIELDS if field not in changed_fields
        )
        continuity = (
            ExplicitInnerContinuityKind.CHANGED
            if changed_fields
            else ExplicitInnerContinuityKind.UNCHANGED
        )
        evidence_codes = {
            "explicit_previous_snapshot_supplied",
            "explicit_current_snapshot_supplied",
            "simulated_inner_state_continuity_compared",
        }
        if (
            not changed_fields
            and previous.source_fingerprint != current.source_fingerprint
        ):
            evidence_codes.add("source_changed_without_affective_change")

        return self._report(
            status=ExplicitInnerContinuityStatus.COMPLETE,
            continuity=continuity,
            previous=previous,
            current=current,
            changed_fields=changed_fields,
            unchanged_fields=unchanged_fields,
            evidence_codes=tuple(sorted(evidence_codes)),
            uncertainty_codes=(),
            risk_codes=tuple(sorted(set(previous.risk_codes + current.risk_codes))),
        )

    def compare_safely(
        self,
        previous: SimulatedInnerStateSnapshot | None,
        current: SimulatedInnerStateSnapshot | None,
    ) -> ExplicitInnerContinuityReport:
        try:
            return self.compare(previous, current)
        except Exception:
            fingerprint = sha256(b"explicit-inner-continuity-failure").hexdigest()
            return ExplicitInnerContinuityReport(
                report_id=f"explicit-inner-continuity-{fingerprint[:16]}",
                status=ExplicitInnerContinuityStatus.DEGRADED,
                continuity=ExplicitInnerContinuityKind.DEGRADED,
                previous_snapshot_id=None,
                current_snapshot_id=None,
                changed_fields=(),
                unchanged_fields=(),
                evidence_codes=("safe_degradation_without_side_effects",),
                uncertainty_codes=("explicit_inner_continuity_unavailable",),
                risk_codes=("explicit_inner_continuity_failure",),
                source_fingerprint=fingerprint,
            )

    def _insufficient(
        self,
        previous: SimulatedInnerStateSnapshot | None,
        current: SimulatedInnerStateSnapshot | None,
    ) -> ExplicitInnerContinuityReport:
        uncertainty_codes = []
        if previous is None:
            uncertainty_codes.append("missing_explicit_previous_snapshot")
        if current is None:
            uncertainty_codes.append("missing_explicit_current_snapshot")
        return self._report(
            status=ExplicitInnerContinuityStatus.INSUFFICIENT_EVIDENCE,
            continuity=ExplicitInnerContinuityKind.UNAVAILABLE,
            previous=previous,
            current=current,
            changed_fields=(),
            unchanged_fields=(),
            evidence_codes=("continuity_requires_two_explicit_snapshots",),
            uncertainty_codes=tuple(uncertainty_codes),
            risk_codes=(),
        )

    def _degraded(
        self,
        previous: SimulatedInnerStateSnapshot,
        current: SimulatedInnerStateSnapshot,
    ) -> ExplicitInnerContinuityReport:
        return self._report(
            status=ExplicitInnerContinuityStatus.DEGRADED,
            continuity=ExplicitInnerContinuityKind.DEGRADED,
            previous=previous,
            current=current,
            changed_fields=(),
            unchanged_fields=(),
            evidence_codes=("degraded_snapshot_prevents_continuity_claim",),
            uncertainty_codes=("continuity_not_claimed_from_degraded_snapshot",),
            risk_codes=tuple(
                sorted(
                    set(previous.risk_codes + current.risk_codes)
                    | {"degraded_snapshot_in_continuity"}
                )
            ),
        )

    def _report(
        self,
        *,
        status: ExplicitInnerContinuityStatus,
        continuity: ExplicitInnerContinuityKind,
        previous: SimulatedInnerStateSnapshot | None,
        current: SimulatedInnerStateSnapshot | None,
        changed_fields: tuple[str, ...],
        unchanged_fields: tuple[str, ...],
        evidence_codes: tuple[str, ...],
        uncertainty_codes: tuple[str, ...],
        risk_codes: tuple[str, ...],
    ) -> ExplicitInnerContinuityReport:
        previous_id = previous.snapshot_id if previous is not None else None
        current_id = current.snapshot_id if current is not None else None
        previous_fingerprint = (
            previous.source_fingerprint if previous is not None else None
        )
        current_fingerprint = (
            current.source_fingerprint if current is not None else None
        )
        fingerprint = sha256(
            repr(
                (
                    previous_id,
                    current_id,
                    previous_fingerprint,
                    current_fingerprint,
                    status,
                    continuity,
                    changed_fields,
                    unchanged_fields,
                    evidence_codes,
                    uncertainty_codes,
                    risk_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return ExplicitInnerContinuityReport(
            report_id=f"explicit-inner-continuity-{fingerprint[:16]}",
            status=status,
            continuity=continuity,
            previous_snapshot_id=previous_id,
            current_snapshot_id=current_id,
            changed_fields=changed_fields,
            unchanged_fields=unchanged_fields,
            evidence_codes=evidence_codes,
            uncertainty_codes=uncertainty_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )
