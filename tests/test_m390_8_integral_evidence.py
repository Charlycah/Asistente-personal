from dataclasses import replace

from core.cognitive_maturity import (
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    ConversationReflectionAuthority,
    ExplicitInnerContinuityEvaluator,
    GovernedExpressiveModulation,
    M390IntegralEvidenceDiagnostic,
    M390IntegralEvidenceStatus,
    SimulatedActivationLevel,
    SimulatedAffectiveTone,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedFunctionalRegulation,
    SimulatedInnerStateAuthority,
    SimulatedInnerStateSignal,
    SimulatedRelationalOpenness,
    SimulatedStabilityLevel,
    UnifiedEpistemicCategory,
    create_canonical_cognitive_cycle,
    create_cognitive_turn_dossier,
)


def _snapshot(reference: str, dominant: SimulatedDominantState):
    signal = SimulatedInnerStateSignal(
        source_authority="functional_psychology",
        source_reference=reference,
        epistemic_category=UnifiedEpistemicCategory.OBSERVED,
        affective_tone=SimulatedAffectiveTone.NEUTRAL,
        activation_level=SimulatedActivationLevel.MODERATE,
        stability_level=SimulatedStabilityLevel.STABLE,
        concern_level=SimulatedConcernLevel.LOW,
        relational_openness=SimulatedRelationalOpenness.BALANCED,
        dominant_state=dominant,
        evidence_codes=(f"evidence:{reference}",),
    )
    return SimulatedInnerStateAuthority().evaluate((signal,))


def _dossier():
    cycle = create_canonical_cognitive_cycle(
        "m390-8-turn",
        records=(
            CognitiveCycleNodeRecord(
                node_id="conversation_ingress",
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("m390_8_explicit_input",),
            ),
        ),
    )
    return create_cognitive_turn_dossier(cycle)


def _complete_chain():
    previous = _snapshot("previous", SimulatedDominantState.ATTENTIVE)
    current = _snapshot("current", SimulatedDominantState.CONCERNED)
    continuity = ExplicitInnerContinuityEvaluator().compare(previous, current)
    regulation = SimulatedFunctionalRegulation().regulate(current, continuity)
    reflection = ConversationReflectionAuthority().reflect(
        _dossier(),
        inner_state=current,
        inner_continuity=continuity,
        inner_regulation=regulation,
    )
    expression = GovernedExpressiveModulation().modulate(
        current,
        regulation=regulation,
    )
    return current, continuity, regulation, reflection, expression


def test_m390_8_empty_chain_is_incomplete_without_side_effects() -> None:
    report = M390IntegralEvidenceDiagnostic().diagnose(None)
    assert report.status is M390IntegralEvidenceStatus.INCOMPLETE
    assert report.read_only is True
    assert report.grants_authority is False
    assert report.persists_state is False
    assert report.executes_action is False


def test_m390_8_complete_chain_is_integrally_evidenced() -> None:
    report = M390IntegralEvidenceDiagnostic().diagnose(*_complete_chain())
    assert report.status is M390IntegralEvidenceStatus.COMPLETE
    assert report.missing_codes == ()
    assert report.conflict_codes == ()
    assert "simulated_inner_state_present" in report.evidence_codes
    assert "inner_state_reflection_present" in report.evidence_codes
    assert "governed_expressive_modulation_present" in report.evidence_codes


def test_m390_8_lineage_conflict_is_exposed_not_repaired() -> None:
    current, continuity, regulation, reflection, expression = _complete_chain()
    mismatched = replace(
        regulation,
        current_snapshot_id="simulated-inner-state-other",
    )
    report = M390IntegralEvidenceDiagnostic().diagnose(
        current,
        continuity,
        mismatched,
        reflection,
        expression,
    )
    assert report.status is M390IntegralEvidenceStatus.CONFLICT
    assert "regulation_current_snapshot_mismatch" in report.conflict_codes


def test_m390_8_diagnostic_is_deterministic() -> None:
    diagnostic = M390IntegralEvidenceDiagnostic()
    chain = _complete_chain()
    assert diagnostic.diagnose(*chain) == diagnostic.diagnose(*chain)
