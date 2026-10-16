from __future__ import annotations

from inspect import getsource

from app.governed_reasoning_runtime import (
    build_default_governed_reasoning_orchestrator,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    EpistemicEvidenceAdapter,
    EpistemicLevel,
)
from core.governed_reasoning import (
    Claim,
    ClaimEvidenceLink,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    EvidenceLinkRole,
    GovernedReasoningOrchestrator,
)


def _claim(
    claim_type: ClaimType,
    *,
    status: ClaimStatus = ClaimStatus.PROPOSED,
    origin: ClaimOrigin = ClaimOrigin.HUMAN,
    supported: bool = False,
) -> Claim:
    links = ()
    if supported:
        links = (
            ClaimEvidenceLink(
                evidence_id="evidence-1",
                role=EvidenceLinkRole.SUPPORTS,
                source_type="test",
                source_id="source-1",
                evidence_fingerprint="a" * 64,
            ),
        )
    return Claim(
        subject="private subject",
        predicate="private predicate",
        object_value="private object",
        claim_type=claim_type,
        origin=origin,
        status=status,
        evidence_links=links,
        rule_reference=(
            "rule:test:v1" if claim_type is ClaimType.RULE_RESULT else None
        ),
    )


def _capture(*claims: Claim):
    records = []
    adapter = EpistemicEvidenceAdapter()
    with adapter.capture(records.append):
        assessments = adapter.observe_claims(claims)
    return records[0], assessments


def test_m388_3_supported_fact_participates_productively() -> None:
    record, assessments = _capture(
        _claim(ClaimType.FACT, status=ClaimStatus.SUPPORTED, supported=True)
    )
    assert record.state is CognitiveCycleNodeState.PARTICIPATED
    assert assessments[0].level is EpistemicLevel.FACT
    assert record.evidence_codes == ("epistemic:fact",)


def test_m388_3_rule_result_remains_inference() -> None:
    record, assessments = _capture(
        _claim(ClaimType.RULE_RESULT, origin=ClaimOrigin.RULE)
    )
    assert assessments[0].level is EpistemicLevel.INFERENCE
    assert record.evidence_codes == ("epistemic:inference",)


def test_m388_3_hypothesis_is_never_promoted_to_fact() -> None:
    record, assessments = _capture(_claim(ClaimType.HYPOTHESIS))
    assert assessments[0].level is EpistemicLevel.HYPOTHESIS
    assert "epistemic:fact" not in record.evidence_codes


def test_m388_3_unknown_claim_degrades_explicitly() -> None:
    record, assessments = _capture(
        _claim(ClaimType.OBSERVATION, supported=True)
    )
    assert assessments[0].level is EpistemicLevel.UNKNOWN
    assert record.state is CognitiveCycleNodeState.DEGRADED
    assert record.reason_codes == ("epistemic:uncertainty_present",)


def test_m388_3_mixed_levels_are_unique_and_deterministic() -> None:
    record, _ = _capture(
        _claim(ClaimType.HYPOTHESIS),
        _claim(ClaimType.RULE_RESULT, origin=ClaimOrigin.RULE),
        _claim(ClaimType.HYPOTHESIS),
    )
    assert record.evidence_codes == (
        "epistemic:inference",
        "epistemic:hypothesis",
    )


def test_m388_3_empty_governed_context_is_omitted_not_fabricated() -> None:
    record, assessments = _capture()
    assert assessments == ()
    assert record.state is CognitiveCycleNodeState.OMITTED
    assert record.reason_codes == ("epistemic:no_claims_available",)


def test_m388_3_inactive_observer_has_no_side_effect() -> None:
    result = EpistemicEvidenceAdapter().observe_claims((_claim(ClaimType.HYPOTHESIS),))
    assert result == ()


def test_m388_3_cycle_evidence_contains_no_private_claim_content() -> None:
    record, _ = _capture(_claim(ClaimType.HYPOTHESIS))
    rendered = repr(record)
    assert "private subject" not in rendered
    assert "private predicate" not in rendered
    assert "private object" not in rendered


def test_m388_3_classification_precedes_governed_inference() -> None:
    source = getsource(GovernedReasoningOrchestrator.reason)
    observation = source.index("self.pre_inference_observer(context.claims)")
    inference = source.index("self.inference_engine.infer(context")
    assert observation < inference


def test_m388_3_diagnostic_failure_is_contained() -> None:
    source = getsource(GovernedReasoningOrchestrator.reason)
    assert "except Exception:" in source
    assert source.index("except Exception:") < source.index(
        "self.inference_engine.infer(context"
    )


def test_m388_3_default_reasoning_runtime_wires_the_adapter() -> None:
    orchestrator = build_default_governed_reasoning_orchestrator()
    observer = orchestrator.pre_inference_observer
    assert observer is not None
    assert isinstance(observer.__self__, EpistemicEvidenceAdapter)


def test_m388_3_official_gateway_captures_epistemic_evidence() -> None:
    source = getsource(OfficialConversationGateway.submit)
    assert "self._epistemic_evidence.capture(" in source
    module_source = getsource(OfficialConversationGateway.__init__)
    assert "EpistemicEvidenceAdapter()" in module_source
    assert "CanonicalCognitiveCore(" in module_source
