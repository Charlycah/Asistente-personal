from __future__ import annotations

from core.adaptive_personality import (
    AdaptiveDeliveryTone,
    AdaptivePersonalityRequest,
)

from .simulated_functional_regulation import (
    SimulatedFunctionalRegulationReport,
    SimulatedFunctionalRegulationStatus,
)
from .simulated_inner_state import (
    SimulatedAffectiveTone,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedInnerStateSnapshot,
    SimulatedInnerStateStatus,
)


class GovernedExpressiveModulation:
    """Pure adapter from simulated inner state to M377 expressive signals."""

    evaluator_id = "governed_expressive_modulation"

    _WARM_STATES = {
        SimulatedDominantState.ENCOURAGED,
        SimulatedDominantState.SUPPORTIVE,
    }
    _CAREFUL_STATES = {
        SimulatedDominantState.CONCERNED,
        SimulatedDominantState.CAUTIOUS,
        SimulatedDominantState.CONFLICTED,
        SimulatedDominantState.UNCERTAIN,
    }

    def modulate(
        self,
        inner_state: SimulatedInnerStateSnapshot | None,
        request: AdaptivePersonalityRequest | None = None,
        regulation: SimulatedFunctionalRegulationReport | None = None,
    ) -> AdaptivePersonalityRequest:
        base = request or AdaptivePersonalityRequest()
        tone = self._delivery_tone(inner_state)
        regulation_reference = None
        if regulation is not None:
            self._validate_regulation(inner_state, regulation)
            if (
                tone is not None
                and regulation.status is SimulatedFunctionalRegulationStatus.COMPLETE
                and regulation.delivery_tone_limit is AdaptiveDeliveryTone.CAREFUL
            ):
                tone = AdaptiveDeliveryTone.CAREFUL
                regulation_reference = regulation.report_id
        source_reference = (
            inner_state.snapshot_id
            if inner_state is not None and tone is not None
            else None
        )
        return AdaptivePersonalityRequest(
            task_complexity=base.task_complexity,
            urgency=base.urgency,
            sensitive=base.sensitive,
            requested_detail=base.requested_detail,
            requested_structure=base.requested_structure,
            affective_delivery_tone=tone,
            affective_source_reference=source_reference,
            affective_regulation_reference=regulation_reference,
        )

    @staticmethod
    def _validate_regulation(
        inner_state: SimulatedInnerStateSnapshot | None,
        regulation: SimulatedFunctionalRegulationReport,
    ) -> None:
        if inner_state is None:
            if regulation.current_snapshot_id is not None:
                raise ValueError("regulation current snapshot requires inner state")
            return
        if regulation.current_snapshot_id != inner_state.snapshot_id:
            raise ValueError("regulation report does not match inner-state snapshot")

    @classmethod
    def _delivery_tone(
        cls,
        inner_state: SimulatedInnerStateSnapshot | None,
    ) -> AdaptiveDeliveryTone | None:
        if inner_state is None:
            return None
        if inner_state.status is not SimulatedInnerStateStatus.COMPLETE:
            return None
        if inner_state.dominant_state in cls._CAREFUL_STATES:
            return AdaptiveDeliveryTone.CAREFUL
        if inner_state.concern_level in {
            SimulatedConcernLevel.MODERATE,
            SimulatedConcernLevel.HIGH,
        }:
            return AdaptiveDeliveryTone.CAREFUL
        if inner_state.affective_tone in {
            SimulatedAffectiveTone.NEGATIVE,
            SimulatedAffectiveTone.MIXED,
        }:
            return AdaptiveDeliveryTone.CAREFUL
        if inner_state.dominant_state in cls._WARM_STATES:
            return AdaptiveDeliveryTone.WARM
        if inner_state.affective_tone is SimulatedAffectiveTone.POSITIVE:
            return AdaptiveDeliveryTone.WARM
        return AdaptiveDeliveryTone.NEUTRAL
