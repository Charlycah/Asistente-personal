from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_maturity import (
    SIMULATION_DISCLOSURE,
    SimulatedActivationLevel,
    SimulatedAffectiveTone,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedInnerStateAuthority,
    SimulatedInnerStateSignal,
    SimulatedInnerStateStatus,
    SimulatedRelationalOpenness,
    SimulatedStabilityLevel,
    UnifiedEpistemicCategory,
)


def _signal(
    source_reference: str = "source-1",
    *,
    tone: SimulatedAffectiveTone = SimulatedAffectiveTone.NEUTRAL,
    activation: SimulatedActivationLevel = SimulatedActivationLevel.MODERATE,
    stability: SimulatedStabilityLevel = SimulatedStabilityLevel.STABLE,
    concern: SimulatedConcernLevel = SimulatedConcernLevel.LOW,
    openness: SimulatedRelationalOpenness = SimulatedRelationalOpenness.BALANCED,
    dominant: SimulatedDominantState = SimulatedDominantState.ATTENTIVE,
    epistemic: UnifiedEpistemicCategory = UnifiedEpistemicCategory.OBSERVED,
) -> SimulatedInnerStateSignal:
    return SimulatedInnerStateSignal(
        source_authority="certified_source",
        source_reference=source_reference,
        epistemic_category=epistemic,
        affective_tone=tone,
        activation_level=activation,
        stability_level=stability,
        concern_level=concern,
        relational_openness=openness,
        dominant_state=dominant,
        evidence_codes=("coded_evidence",),
    )


def test_m390_1_empty_input_is_explicitly_insufficient() -> None:
    snapshot = SimulatedInnerStateAuthority().evaluate(())
    assert snapshot.status is SimulatedInnerStateStatus.INSUFFICIENT_EVIDENCE
    assert snapshot.dominant_state is SimulatedDominantState.UNCERTAIN
    assert snapshot.uncertainty_codes == ("no_simulated_inner_state_signals",)


def test_m390_1_single_signal_is_preserved_without_reanalysis() -> None:
    signal = _signal()
    snapshot = SimulatedInnerStateAuthority().evaluate((signal,))
    assert snapshot.status is SimulatedInnerStateStatus.COMPLETE
    assert snapshot.affective_tone is signal.affective_tone
    assert snapshot.activation_level is signal.activation_level
    assert snapshot.stability_level is signal.stability_level
    assert snapshot.concern_level is signal.concern_level
    assert snapshot.relational_openness is signal.relational_openness
    assert snapshot.dominant_state is signal.dominant_state


def test_m390_1_conflicting_signals_remain_explicitly_conflicted() -> None:
    first = _signal(tone=SimulatedAffectiveTone.POSITIVE)
    second = _signal(
        "source-2",
        tone=SimulatedAffectiveTone.NEGATIVE,
        activation=SimulatedActivationLevel.HIGH,
        dominant=SimulatedDominantState.CAUTIOUS,
    )
    snapshot = SimulatedInnerStateAuthority().evaluate((first, second))
    assert snapshot.affective_tone is SimulatedAffectiveTone.MIXED
    assert snapshot.activation_level is SimulatedActivationLevel.UNKNOWN
    assert snapshot.dominant_state is SimulatedDominantState.CONFLICTED
    assert "simulated_inner_state_signal_conflict" in snapshot.risk_codes
    assert "conflict:affective_tone" in snapshot.uncertainty_codes


def test_m390_1_epistemic_uncertainty_is_not_promoted_to_fact() -> None:
    snapshot = SimulatedInnerStateAuthority().evaluate(
        (_signal(epistemic=UnifiedEpistemicCategory.POSSIBLE),)
    )
    assert "source_contains_possibility" in snapshot.uncertainty_codes


def test_m390_1_is_deterministic_regardless_of_signal_order() -> None:
    authority = SimulatedInnerStateAuthority()
    first = _signal("b")
    second = _signal("a")
    assert authority.evaluate((first, second)) == authority.evaluate((second, first))


def test_m390_1_snapshot_is_immutable() -> None:
    snapshot = SimulatedInnerStateAuthority().evaluate((_signal(),))
    with pytest.raises(FrozenInstanceError):
        snapshot.status = SimulatedInnerStateStatus.DEGRADED


def test_m390_1_discloses_simulation_and_denies_subjective_claims() -> None:
    snapshot = SimulatedInnerStateAuthority().evaluate((_signal(),))
    assert snapshot.simulation_disclosure == SIMULATION_DISCLOSURE
    assert snapshot.claims_consciousness is False
    assert snapshot.claims_subjective_experience is False
    assert snapshot.claims_real_emotion is False


def test_m390_1_has_no_governed_side_effects() -> None:
    snapshot = SimulatedInnerStateAuthority().evaluate((_signal(),))
    assert snapshot.read_only is True
    assert snapshot.grants_authority is False
    assert snapshot.persists_state is False
    assert snapshot.contains_conversation_content is False
    assert snapshot.creates_memory is False
    assert snapshot.modifies_memory is False
    assert snapshot.creates_learning_candidate is False
    assert snapshot.modifies_learning is False
    assert snapshot.modifies_planning is False
    assert snapshot.modifies_personality is False
    assert snapshot.modifies_permissions is False
    assert snapshot.creates_goal is False
    assert snapshot.creates_task is False
    assert snapshot.schedules_action is False
    assert snapshot.executes_action is False


def test_m390_1_safe_failure_degrades_without_authority() -> None:
    class BrokenAuthority(SimulatedInnerStateAuthority):
        def evaluate(self, signals):
            raise RuntimeError("synthetic failure")

    snapshot = BrokenAuthority().evaluate_safely(())
    assert snapshot.status is SimulatedInnerStateStatus.DEGRADED
    assert snapshot.risk_codes == ("simulated_inner_state_failure",)
    assert snapshot.grants_authority is False
