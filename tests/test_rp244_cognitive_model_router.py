from datetime import datetime, timezone

import pytest

from core.cognitive_model_router import (
    CognitiveModelProfile,
    CognitiveModelRouter,
    CognitiveRoutingRequest,
    InformationFreshness,
    ModelLocation,
    ReasoningDemand,
    RoutingOutcome,
)

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)


def profiles() -> tuple[CognitiveModelProfile, ...]:
    return (
        CognitiveModelProfile(
            name="ollama",
            location=ModelLocation.LOCAL,
            capabilities=("text", "code"),
            reasoning_strength=65,
            privacy_score=100,
            latency_score=80,
            cost_score=100,
        ),
        CognitiveModelProfile(
            name="gemini",
            location=ModelLocation.REMOTE,
            capabilities=("text", "vision", "code"),
            supports_current_information=True,
            reasoning_strength=92,
            privacy_score=30,
            latency_score=70,
            cost_score=60,
        ),
        CognitiveModelProfile(
            name="mistral",
            location=ModelLocation.REMOTE,
            capabilities=("text", "code"),
            reasoning_strength=80,
            privacy_score=35,
            latency_score=85,
            cost_score=80,
        ),
    )


def test_stable_standard_query_prefers_local_model() -> None:
    router = CognitiveModelRouter(profiles())
    decision = router.route(
        CognitiveRoutingRequest(owner="Carlos", purpose="conversación cotidiana"),
        now=NOW,
    )
    assert decision.outcome is RoutingOutcome.SELECTED
    assert decision.selected_model is not None
    assert decision.selected_model.name == "ollama"
    assert decision.network_access_required is False


def test_sensitive_query_never_leaves_local_machine() -> None:
    router = CognitiveModelRouter(profiles())
    decision = router.route(
        CognitiveRoutingRequest(
            owner="Carlos",
            purpose="resumir datos personales",
            sensitive=True,
            reasoning=ReasoningDemand.COMPLEX,
        ),
        now=NOW,
    )
    assert decision.selected_model is not None
    assert decision.selected_model.location is ModelLocation.LOCAL
    assert all(
        item.location is ModelLocation.LOCAL
        for item in decision.fallback_models
    )


def test_live_information_selects_capable_remote_model() -> None:
    router = CognitiveModelRouter(profiles())
    decision = router.route(
        CognitiveRoutingRequest(
            owner="Carlos",
            purpose="noticias de último momento",
            freshness=InformationFreshness.LIVE,
        ),
        now=NOW,
    )
    assert decision.selected_model is not None
    assert decision.selected_model.name == "gemini"
    assert decision.network_access_required is True


def test_remote_prohibition_with_live_request_withholds() -> None:
    router = CognitiveModelRouter(profiles())
    decision = router.route(
        CognitiveRoutingRequest(
            owner="Carlos",
            purpose="actualidad sin red",
            freshness=InformationFreshness.LIVE,
            remote_allowed=False,
        ),
        now=NOW,
    )
    assert decision.outcome is RoutingOutcome.WITHHELD
    assert decision.selected_model is None


def test_required_capability_filters_models() -> None:
    router = CognitiveModelRouter(profiles())
    decision = router.route(
        CognitiveRoutingRequest(
            owner="Carlos",
            purpose="analizar una imagen",
            required_capabilities=("vision",),
        ),
        now=NOW,
    )
    assert decision.selected_model is not None
    assert decision.selected_model.name == "gemini"


def test_low_cost_preference_can_choose_mistral() -> None:
    router = CognitiveModelRouter(profiles())
    decision = router.route(
        CognitiveRoutingRequest(
            owner="Carlos",
            purpose="generar código no sensible",
            required_capabilities=("code",),
            prefer_low_cost=True,
            remote_allowed=True,
        ),
        now=NOW,
    )
    assert decision.selected_model is not None
    assert decision.selected_model.name in {"ollama", "mistral"}
    assert decision.scores[0].cost >= 80


def test_disabled_and_unhealthy_models_are_excluded() -> None:
    router = CognitiveModelRouter(
        (
            CognitiveModelProfile(
                name="local-off",
                location="local",
                enabled=False,
            ),
            CognitiveModelProfile(
                name="remote-down",
                location="remote",
                healthy=False,
            ),
        )
    )
    decision = router.route(
        CognitiveRoutingRequest(owner="Carlos", purpose="consulta"),
        now=NOW,
    )
    assert decision.outcome is RoutingOutcome.WITHHELD


def test_no_model_required_is_declared_without_selection() -> None:
    router = CognitiveModelRouter(profiles())
    decision = router.route(
        CognitiveRoutingRequest(
            owner="Carlos",
            purpose="respuesta determinista",
            model_required=False,
        ),
        now=NOW,
    )
    assert decision.outcome is RoutingOutcome.NO_MODEL_REQUIRED
    assert decision.scores == ()


def test_decision_keeps_ranked_fallbacks_and_explanation() -> None:
    router = CognitiveModelRouter(profiles())
    decision = router.route(
        CognitiveRoutingRequest(
            owner="Carlos",
            purpose="razonamiento complejo",
            reasoning=ReasoningDemand.COMPLEX,
        ),
        now=NOW,
    )
    assert decision.selected_model is not None
    assert len(decision.fallback_models) == 2
    assert decision.scores[0].total >= decision.scores[1].total
    assert any("selected_" in item for item in decision.rationale)


def test_router_retains_auditable_history() -> None:
    router = CognitiveModelRouter(profiles())
    first = router.route(
        CognitiveRoutingRequest(owner="Carlos", purpose="primera"),
        now=NOW,
    )
    second = router.route(
        CognitiveRoutingRequest(owner="Cristi", purpose="segunda"),
        now=NOW,
    )
    assert router.history == (first, second)
    assert router.last_decision is second
    assert first.decision_id != second.decision_id


def test_naive_timestamp_is_rejected() -> None:
    router = CognitiveModelRouter(profiles())
    with pytest.raises(ValueError, match="timezone-aware"):
        router.route(
            CognitiveRoutingRequest(owner="Carlos", purpose="consulta"),
            now=datetime(2026, 7, 20, 12, 0),
        )


def test_duplicate_profile_names_are_rejected() -> None:
    profile = CognitiveModelProfile(name="ollama", location="local")
    with pytest.raises(ValueError, match="unique"):
        CognitiveModelRouter((profile, profile))
