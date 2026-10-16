from __future__ import annotations

from core.cognitive_maturity import (
    GovernedAffectiveEvaluator,
    SimulatedDominantState,
    SimulatedInnerStateAuthority,
    SimulatedInnerStateStatus,
    UnifiedEpistemicCategory,
    UnifiedEpistemicEvidenceAuthority,
)


def test_m390_2_empty_certified_sources_emit_no_signal() -> None:
    assert GovernedAffectiveEvaluator().evaluate(None, None, None) == ()


def test_m390_2_epistemic_insufficiency_is_not_invented_as_emotion() -> None:
    epistemic = UnifiedEpistemicEvidenceAuthority().unify(None)
    signals = GovernedAffectiveEvaluator().evaluate(None, None, epistemic)
    assert len(signals) == 1
    signal = signals[0]
    assert signal.epistemic_category is (
        UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION
    )
    assert signal.dominant_state is SimulatedDominantState.UNCERTAIN


def test_m390_2_signals_are_consumed_by_existing_inner_state_authority() -> None:
    epistemic = UnifiedEpistemicEvidenceAuthority().unify(None)
    signals = GovernedAffectiveEvaluator().evaluate(None, None, epistemic)
    snapshot = SimulatedInnerStateAuthority().evaluate(signals)
    assert snapshot.status is SimulatedInnerStateStatus.COMPLETE
    assert snapshot.source_references == (
        f"unified_epistemic_evidence:{epistemic.report_id}",
    )


def test_m390_2_is_deterministic() -> None:
    epistemic = UnifiedEpistemicEvidenceAuthority().unify(None)
    evaluator = GovernedAffectiveEvaluator()
    assert evaluator.evaluate(None, None, epistemic) == evaluator.evaluate(
        None, None, epistemic
    )
