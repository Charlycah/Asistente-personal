from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.adaptive_cognition_runtime import OfficialAdaptiveCognitionRuntimeGateway
from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)
from core.llm_provider import LLMRequest
from core.reasoning_runtime_integration import ReasoningRuntimeContributor

NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


def _request(text: str = "Analizá las opciones y decidí cuál conviene."):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="canonical-reasoning",
        text=text,
    )


def test_same_turn_productive_episode_is_evaluated_once():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    request = _request()
    identity = build_governed_conversation_turn_identity(request, NOW)
    first = gateway.evaluate_productive_episode(
        owner=request.owner,
        session_id=request.session_id,
        text="prompt enriquecido",
        now=NOW,
        turn_id=identity.turn_id,
        scope_reference=request.session_id,
        observe_productive_intake=False,
    )
    second = gateway.evaluate_productive_episode(
        owner=request.owner,
        session_id=request.session_id,
        text=request.text,
        now=NOW,
        turn_id=identity.turn_id,
        scope_reference=request.session_id,
        observe_productive_intake=False,
    )
    assert first is second
    assert gateway.snapshot.evaluations == 1


def test_cognitive_source_reuses_existing_official_episode():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    request = _request()
    identity = build_governed_conversation_turn_identity(request, NOW)
    episode = gateway.evaluate_productive_episode(
        owner=request.owner,
        session_id=request.session_id,
        text="prompt enriquecido",
        now=NOW,
        turn_id=identity.turn_id,
        scope_reference=request.session_id,
        observe_productive_intake=False,
    )
    projected = source(
        owner=request.owner,
        session_id=request.session_id,
        text=request.text,
        now=NOW,
    )
    assert projected.result_id == episode.result.result_id
    assert gateway.snapshot.evaluations == 1


def test_later_identical_turn_gets_new_episode():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    request = _request()
    first = source(
        owner=request.owner,
        session_id=request.session_id,
        text=request.text,
        now=NOW,
    )
    second = source(
        owner=request.owner,
        session_id=request.session_id,
        text=request.text,
        now=NOW + timedelta(seconds=1),
    )
    assert gateway.snapshot.evaluations == 2
    assert first is not second


def test_adaptive_cognition_uses_shared_productive_episode():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    adaptive = OfficialAdaptiveCognitionRuntimeGateway(reasoning_runtime=gateway)
    request = _request()
    identity = build_governed_conversation_turn_identity(request, NOW)
    adaptive.evaluate_text(
        owner=request.owner,
        text=request.text,
        now=NOW,
        scope_reference=request.session_id,
        observe_productive_intake=False,
        productive_turn_id=identity.turn_id,
    )
    source = CanonicalProductiveReasoningSource(gateway)
    source(
        owner=request.owner,
        session_id=request.session_id,
        text=request.text,
        now=NOW,
    )
    assert gateway.snapshot.evaluations == 1


def test_abstained_canonical_episode_is_projected_truthfully():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    contribution = ReasoningRuntimeContributor(
        CanonicalProductiveReasoningSource(gateway)
    ).contribute(
        owner="Carlos",
        session_id="canonical-reasoning",
        text="Analizá las opciones y decidí cuál conviene.",
        request=LLMRequest(prompt="resolver"),
        now=NOW,
    )
    assert contribution.status.value == "applied"
    assert "evidencia insuficiente" in contribution.prompt_lines[0]
    assert gateway.snapshot.evaluations == 1


def test_episode_is_turn_scoped_not_durable_history():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    request = _request()
    first_identity = build_governed_conversation_turn_identity(request, NOW)
    source(
        owner=request.owner,
        session_id=request.session_id,
        text=request.text,
        now=NOW,
    )
    later = NOW + timedelta(minutes=1)
    source(
        owner=request.owner,
        session_id=request.session_id,
        text=request.text,
        now=later,
    )
    assert (
        gateway.productive_episode(
            owner=request.owner,
            session_id=request.session_id,
            turn_id=first_identity.turn_id,
        )
        is None
    )


def test_turn_identity_matches_reliability_contract_shape():
    identity = build_governed_conversation_turn_identity(_request(), NOW)
    assert len(identity.conversation_id) == 64
    assert len(identity.request_id) == 64
    assert len(identity.turn_id) == 64
    assert len(identity.trace_id) == 64


def test_official_turn_reuses_same_gateway_episode_in_preparation(monkeypatch):
    from app.runtime_root_factory import build_runtime_root

    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    composition = root.compose()
    gateway = root.dependencies.governed_reasoning_runtime
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="canonical-e2e",
        text="Como evaluas la evidencia?",
    )
    execution = root.dependencies.conversation_reliability_observability_runtime
    result = execution.evaluate_turn(request, now=NOW)
    assert result.entry_action == "route_to_reasoning"
    assert gateway.snapshot.evaluations == 1
    composition.preparation.prepare_at(request, now=NOW)
    assert gateway.snapshot.evaluations == 1


def test_runtime_root_uses_same_gateway_for_adaptive_and_cognitive_source(monkeypatch):
    from app.runtime_root_factory import build_runtime_root

    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    gateway = root.dependencies.governed_reasoning_runtime
    assert root.dependencies.adaptive_cognition_runtime.reasoning_runtime is gateway
    source = root.dependencies.governed_reasoning_source
    assert isinstance(source, CanonicalProductiveReasoningSource)
    assert source.gateway is gateway
