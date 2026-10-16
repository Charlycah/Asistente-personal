from core.cognitive_maturity import (
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    ConversationReflectionAuthority,
    ExplicitInnerContinuityEvaluator,
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


def _dossier():
    cycle = create_canonical_cognitive_cycle(
        "m390-7-turn",
        records=(
            CognitiveCycleNodeRecord(
                node_id="conversation_ingress",
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("m390_7_explicit_input",),
            ),
        ),
    )
    return create_cognitive_turn_dossier(cycle)


def _snapshot(*, dominant=SimulatedDominantState.ATTENTIVE, risk_codes=()):
    signal = SimulatedInnerStateSignal(
        source_authority="functional_psychology",
        source_reference="m390-7-explicit-source",
        epistemic_category=UnifiedEpistemicCategory.OBSERVED,
        affective_tone=SimulatedAffectiveTone.NEUTRAL,
        activation_level=SimulatedActivationLevel.MODERATE,
        stability_level=SimulatedStabilityLevel.STABLE,
        concern_level=SimulatedConcernLevel.LOW,
        relational_openness=SimulatedRelationalOpenness.BALANCED,
        dominant_state=dominant,
        evidence_codes=("m390_7_explicit_evidence",),
        risk_codes=risk_codes,
    )
    return SimulatedInnerStateAuthority().evaluate((signal,))


def test_m390_7_existing_reflection_authority_observes_inner_state() -> None:
    snapshot = _snapshot()
    report = ConversationReflectionAuthority().reflect(
        _dossier(), inner_state=snapshot
    )
    assert report.inner_state_snapshot_id == snapshot.snapshot_id
    assert "simulated_inner_state_observed" in report.inner_state_observation_codes
    assert report.grants_authority is False
    assert report.creates_memory is False


def test_m390_7_reflection_observes_explicit_continuity_and_regulation() -> None:
    previous = _snapshot()
    current = _snapshot(dominant=SimulatedDominantState.CONCERNED)
    continuity = ExplicitInnerContinuityEvaluator().compare(previous, current)
    regulation = SimulatedFunctionalRegulation().regulate(current, continuity)
    report = ConversationReflectionAuthority().reflect(
        _dossier(),
        inner_state=current,
        inner_continuity=continuity,
        inner_regulation=regulation,
    )
    assert report.inner_continuity_report_id == continuity.report_id
    assert report.inner_regulation_report_id == regulation.report_id
    assert "explicit_inner_state_change_observed" in (
        report.inner_state_observation_codes
    )


def test_m390_7_inner_risk_is_observed_not_reinterpreted() -> None:
    snapshot = _snapshot(risk_codes=("explicit_inner_risk",))
    report = ConversationReflectionAuthority().reflect(
        _dossier(), inner_state=snapshot
    )
    assert "simulated_inner_state_risk_present" in report.risk_codes
    assert "explicit_inner_risk" not in report.risk_codes


def test_m390_7_ancillary_reports_without_snapshot_are_ignored() -> None:
    current = _snapshot()
    regulation = SimulatedFunctionalRegulation().regulate(current)
    report = ConversationReflectionAuthority().reflect(
        _dossier(), inner_regulation=regulation
    )
    assert report.inner_state_snapshot_id is None
    assert report.inner_regulation_report_id is None
    assert report.inner_state_observation_codes == ()


def test_m390_7_legacy_reflection_is_unchanged_and_deterministic() -> None:
    authority = ConversationReflectionAuthority()
    dossier = _dossier()
    first = authority.reflect(dossier)
    second = authority.reflect(dossier)
    assert first == second
    assert first.inner_state_snapshot_id is None
    assert first.inner_state_observation_codes == ()
