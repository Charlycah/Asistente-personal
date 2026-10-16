from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from core.adaptive_personality import AdaptiveDeliveryTone

from .explicit_inner_continuity import (
    ExplicitInnerContinuityKind,
    ExplicitInnerContinuityReport,
    ExplicitInnerContinuityStatus,
)
from .simulated_inner_state import (
    SIMULATION_DISCLOSURE,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedInnerStateSnapshot,
    SimulatedInnerStateStatus,
    SimulatedStabilityLevel,
)


class SimulatedFunctionalRegulationStatus(str, Enum):
    COMPLETE = "complete"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


class SimulatedFunctionalRegulationMode(str, Enum):
    PASSTHROUGH = "passthrough"
    STABILIZE = "stabilize"
    CAUTIOUS = "cautious"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class SimulatedFunctionalRegulationReport:
    report_id: str
    status: SimulatedFunctionalRegulationStatus
    mode: SimulatedFunctionalRegulationMode
    current_snapshot_id: str | None
    continuity_report_id: str | None
    delivery_tone_limit: AdaptiveDeliveryTone | None
    evidence_codes: tuple[str, ...]
    uncertainty_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    simulation_disclosure: str = SIMULATION_DISCLOSURE
    schema_version: str = "m390.6"
    read_only: bool = True
    explicit_inputs_only: bool = True
    persists_state: bool = False
    uses_clock: bool = False
    creates_memory: bool = False
    modifies_learning: bool = False
    modifies_personality: bool = False
    creates_goal: bool = False
    executes_action: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("simulated-functional-regulation-"):
            raise ValueError("functional regulation identifier is invalid")
        if self.simulation_disclosure != SIMULATION_DISCLOSURE:
            raise ValueError(
                "functional regulation must preserve simulation disclosure"
            )
        if not self.read_only or not self.explicit_inputs_only or self.persists_state:
            raise ValueError("functional regulation must remain explicit and transient")
        if self.uses_clock:
            raise ValueError("functional regulation cannot use hidden time state")
        if any(
            (
                self.creates_memory,
                self.modifies_learning,
                self.modifies_personality,
                self.creates_goal,
                self.executes_action,
            )
        ):
            raise ValueError("functional regulation cannot modify governed domains")
        if self.delivery_tone_limit not in {
            None,
            AdaptiveDeliveryTone.CAREFUL,
        }:
            raise ValueError("functional regulation may only limit delivery to careful")


class SimulatedFunctionalRegulation:
    """Pure regulator over explicit M390 state and continuity evidence."""

    evaluator_id = "simulated_functional_regulation"

    _BROAD_CHANGE_THRESHOLD = 3

    def regulate(
        self,
        current: SimulatedInnerStateSnapshot | None,
        continuity: ExplicitInnerContinuityReport | None = None,
    ) -> SimulatedFunctionalRegulationReport:
        if current is None:
            return self._report(
                status=SimulatedFunctionalRegulationStatus.INSUFFICIENT_EVIDENCE,
                mode=SimulatedFunctionalRegulationMode.UNAVAILABLE,
                current=None,
                continuity=continuity,
                delivery_tone_limit=None,
                evidence_codes=("functional_regulation_requires_current_snapshot",),
                uncertainty_codes=("missing_explicit_current_snapshot",),
                risk_codes=(),
            )
        if current.status is SimulatedInnerStateStatus.DEGRADED:
            return self._report(
                status=SimulatedFunctionalRegulationStatus.DEGRADED,
                mode=SimulatedFunctionalRegulationMode.DEGRADED,
                current=current,
                continuity=continuity,
                delivery_tone_limit=None,
                evidence_codes=("degraded_inner_state_not_regulated",),
                uncertainty_codes=("functional_regulation_unavailable",),
                risk_codes=tuple(
                    sorted(set(current.risk_codes) | {"degraded_inner_state"})
                ),
            )

        evidence_codes = {"explicit_current_snapshot_regulated"}
        uncertainty_codes = set(current.uncertainty_codes)
        risk_codes = set(current.risk_codes)

        if continuity is not None:
            evidence_codes.add("explicit_continuity_considered")
            uncertainty_codes.update(continuity.uncertainty_codes)
            risk_codes.update(continuity.risk_codes)

        mode = SimulatedFunctionalRegulationMode.PASSTHROUGH
        tone_limit = None

        if self._requires_caution(current, continuity):
            mode = SimulatedFunctionalRegulationMode.CAUTIOUS
            tone_limit = AdaptiveDeliveryTone.CAREFUL
            evidence_codes.add("proportional_caution_applied")
        elif self._requires_stabilization(continuity):
            mode = SimulatedFunctionalRegulationMode.STABILIZE
            tone_limit = AdaptiveDeliveryTone.CAREFUL
            evidence_codes.add("broad_explicit_change_stabilized")

        if self._single_relational_source(current):
            evidence_codes.add("single_relational_source_not_allowed_to_escalate")
            if tone_limit is None:
                mode = SimulatedFunctionalRegulationMode.STABILIZE
                tone_limit = AdaptiveDeliveryTone.CAREFUL

        return self._report(
            status=SimulatedFunctionalRegulationStatus.COMPLETE,
            mode=mode,
            current=current,
            continuity=continuity,
            delivery_tone_limit=tone_limit,
            evidence_codes=tuple(sorted(evidence_codes)),
            uncertainty_codes=tuple(sorted(uncertainty_codes)),
            risk_codes=tuple(sorted(risk_codes)),
        )

    @classmethod
    def _requires_caution(
        cls,
        current: SimulatedInnerStateSnapshot,
        continuity: ExplicitInnerContinuityReport | None,
    ) -> bool:
        if current.risk_codes:
            return True
        if current.stability_level is SimulatedStabilityLevel.UNSTABLE:
            return True
        if current.concern_level is SimulatedConcernLevel.HIGH:
            return True
        if current.dominant_state in {
            SimulatedDominantState.CONFLICTED,
            SimulatedDominantState.UNCERTAIN,
        }:
            return True
        return bool(
            continuity is not None
            and continuity.status is ExplicitInnerContinuityStatus.DEGRADED
        )

    @classmethod
    def _requires_stabilization(
        cls,
        continuity: ExplicitInnerContinuityReport | None,
    ) -> bool:
        return bool(
            continuity is not None
            and continuity.status is ExplicitInnerContinuityStatus.COMPLETE
            and continuity.continuity is ExplicitInnerContinuityKind.CHANGED
            and len(continuity.changed_fields) >= cls._BROAD_CHANGE_THRESHOLD
        )

    @staticmethod
    def _single_relational_source(current: SimulatedInnerStateSnapshot) -> bool:
        return bool(
            len(current.source_references) == 1
            and current.source_references[0].startswith(
                "relational_affective_context:"
            )
        )

    @staticmethod
    def _report(
        *,
        status: SimulatedFunctionalRegulationStatus,
        mode: SimulatedFunctionalRegulationMode,
        current: SimulatedInnerStateSnapshot | None,
        continuity: ExplicitInnerContinuityReport | None,
        delivery_tone_limit: AdaptiveDeliveryTone | None,
        evidence_codes: tuple[str, ...],
        uncertainty_codes: tuple[str, ...],
        risk_codes: tuple[str, ...],
    ) -> SimulatedFunctionalRegulationReport:
        current_id = current.snapshot_id if current is not None else None
        continuity_id = continuity.report_id if continuity is not None else None
        current_fingerprint = (
            current.source_fingerprint if current is not None else None
        )
        continuity_fingerprint = (
            continuity.source_fingerprint if continuity is not None else None
        )
        fingerprint = sha256(
            repr(
                (
                    status,
                    mode,
                    current_id,
                    continuity_id,
                    current_fingerprint,
                    continuity_fingerprint,
                    delivery_tone_limit,
                    evidence_codes,
                    uncertainty_codes,
                    risk_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return SimulatedFunctionalRegulationReport(
            report_id=f"simulated-functional-regulation-{fingerprint[:16]}",
            status=status,
            mode=mode,
            current_snapshot_id=current_id,
            continuity_report_id=continuity_id,
            delivery_tone_limit=delivery_tone_limit,
            evidence_codes=evidence_codes,
            uncertainty_codes=uncertainty_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )
