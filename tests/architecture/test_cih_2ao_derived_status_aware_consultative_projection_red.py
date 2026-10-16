from __future__ import annotations

from datetime import datetime, timezone

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.cognitive_runtime_orchestration import CognitiveRuntimeStageStatus
from core.governed_reasoning import GovernedReasoningStatus
from core.llm_provider import LLMRequest
from core.reasoning_runtime_integration import ReasoningRuntimeContributor

_NOW = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
_TEXT = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."
_OWNER = "owner-1"
_SESSION_ID = "session-cih-2ao"


def test_cih_2ao_derived_reasoning_requires_status_aware_consultative_projection(
) -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)

    result = source(
        owner=_OWNER,
        session_id=_SESSION_ID,
        text=_TEXT,
        now=_NOW,
    )
    assert result.status is GovernedReasoningStatus.DERIVED
    assert len(result.non_rule_derivations) == 1
    derived_claim = result.non_rule_derivations[0].derived_claim
    assert derived_claim is not None
    assert derived_claim.normalized_type.value == "hypothesis"
    assert derived_claim.confidence is None
    assert derived_claim.evidence_links == ()
    assert derived_claim.rule_reference is None
    assert result.inference_run.applied_claims == ()
    assert result.decision.rule_links == ()

    contribution = ReasoningRuntimeContributor(source).contribute(
        owner=_OWNER,
        session_id=_SESSION_ID,
        text=_TEXT,
        request=LLMRequest(prompt=_TEXT),
        now=_NOW,
    )

    assert contribution.status is CognitiveRuntimeStageStatus.APPLIED
    assert contribution.rationale != ("governed_reasoning_context_applied",)
    assert not any(
        line.startswith("Confianza del razonamiento:")
        for line in contribution.prompt_lines
    )
    projected = " ".join(contribution.prompt_lines).casefold()
    assert "hipótes" in projected or "modal" in projected
