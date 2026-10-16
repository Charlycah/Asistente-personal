from __future__ import annotations

from datetime import datetime, timezone

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from core.governed_reasoning import (
    BoundedNonRuleDerivationStatus,
    BoundedProductiveSupportInterpretationStatus,
    GovernedBoundedNonRuleDerivationFoundationV1,
    GovernedBoundedProductiveSupportInterpreterV1,
    GovernedReasoningStatus,
)

_NOW = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
_TEXT = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."


def test_cih_2aj_support_interpretation_and_non_rule_derivation_contract() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    binding = gateway._compose_bounded_situational_productive_binding(
        owner="owner-1",
        session_id="session-1",
        turn_id="turn-1",
        text=_TEXT,
        now=_NOW,
        scope_reference="session-1",
    )
    assert binding is not None
    assert binding.source_claim is not None

    interpretation = GovernedBoundedProductiveSupportInterpreterV1().interpret(
        source_claim=binding.source_claim
    )
    assert (
        interpretation.status
        is BoundedProductiveSupportInterpretationStatus.INTERPRETED
    )
    assert interpretation.interpreted_claim is not None
    claim = interpretation.interpreted_claim
    assert (
        claim.subject,
        claim.predicate,
        claim.object_value,
    ) == (
        "current_turn_situation",
        "may_admit_contextual_assistance",
        "organization_support",
    )
    assert claim.normalized_type.value == "hypothesis"
    assert claim.normalized_origin.value == "system"
    assert claim.normalized_status.value == "proposed"
    assert claim.confidence is None
    assert claim.evidence_links == ()
    assert claim.rule_reference is None

    derivation = GovernedBoundedNonRuleDerivationFoundationV1().derive(
        interpreted_claim=claim
    )
    assert derivation.status is BoundedNonRuleDerivationStatus.DERIVED
    assert derivation.derived_claim is claim
    assert derivation.authorizes_inference is False
    assert derivation.authorizes_action is False
    assert derivation.registers_rules is False


def test_cih_2aj_productive_episode_is_canonically_derived_without_rule_inference(
) -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = gateway.evaluate_productive_episode(
        owner="owner-1",
        session_id="session-derived",
        turn_id="turn-derived",
        text=_TEXT,
        now=_NOW,
        scope_reference="session-derived",
        observe_productive_intake=False,
    )

    result = episode.result
    assert result.status is GovernedReasoningStatus.DERIVED
    assert result.inference_run.applied_claims == ()
    assert len(result.non_rule_derivations) == 1
    derivation = result.non_rule_derivations[0]
    assert derivation.status is BoundedNonRuleDerivationStatus.DERIVED
    assert derivation.derived_claim is not None
    assert derivation.derived_claim.predicate == "may_admit_contextual_assistance"
    assert result.decision.normalized_status.value == "completed"
    assert result.decision.normalized_outcome.value == "conclusion"
    assert derivation.derived_claim.claim_id in {
        link.claim_id for link in result.decision.claim_links
    }
    assert result.decision.rule_links == ()
    assert "may_admit_contextual_assistance" in result.decision.conclusion


def test_cih_2aj_unrelated_text_remains_abstained_without_non_rule_derivation() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = gateway.evaluate_productive_episode(
        owner="owner-1",
        session_id="session-ordinary",
        turn_id="turn-ordinary",
        text="La capital de Japón es Tokio.",
        now=_NOW,
        scope_reference="session-ordinary",
        observe_productive_intake=False,
    )

    assert episode.result.status is GovernedReasoningStatus.ABSTAINED
    assert episode.result.non_rule_derivations == ()
