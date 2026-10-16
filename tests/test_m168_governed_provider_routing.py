from dataclasses import FrozenInstanceError, replace

import pytest

from core.governed_provider_routing import (
    GovernedProviderRouter,
    GovernedProviderRoutingConfig,
    GovernedProviderRoutingRequest,
    InMemoryGovernedProviderRoutingRepository,
    ProviderRouteAction,
    ProviderRouteStatus,
)
from core.local_first_provider_policy import (
    LocalFirstProviderConfig,
    ProviderPolicyStatus,
)
from core.provider_health_evaluation import ProviderCapability, ProviderKind
from tests.test_m166_provider_health_evaluation import (
    NOW,
    observation,
)
from tests.test_m166_provider_health_evaluation import (
    evaluate as health,
)
from tests.test_m167_local_first_provider_policy import (
    decide as policy,
)
from tests.test_m167_local_first_provider_policy import (
    workload,
)

HEALTH = health(
    items=(
        observation(latency_ms=80),
        observation(
            "gemini",
            kind="remote",
            model="gemini",
            endpoint="https://example.invalid",
            latency_ms=120,
        ),
    )
)
POLICY = policy(health_result=HEALTH)


def request(*, policy_decision=POLICY, **changes):
    values = {"owner": "Carlos", "policy_decision": policy_decision}
    values.update(changes)
    return GovernedProviderRoutingRequest(**values)


def route(*, config=None, policy_decision=POLICY, **changes):
    router = GovernedProviderRouter(config=config)
    return router.route(
        request(policy_decision=policy_decision, **changes),
        now=NOW,
    )


def test_selects_local_provider_for_local_preference():
    result = route()
    assert result.status is ProviderRouteStatus.ROUTED_LOCAL
    assert result.action is ProviderRouteAction.DECLARE_LOCAL_ROUTE
    assert result.selected_provider.provider_name == "ollama"
    assert result.route_kind is ProviderKind.LOCAL
    assert result.route_declared


def test_preserves_exact_m167_lineage():
    result = route()
    assert result.request.policy_decision is POLICY


def test_remote_policy_selects_remote_provider():
    decision = policy(
        health_result=HEALTH,
        task=workload(current_information_required=True),
    )
    result = route(policy_decision=decision)
    assert result.status is ProviderRouteStatus.ROUTED_REMOTE
    assert result.selected_provider.provider_name == "gemini"
    assert result.route_kind is ProviderKind.REMOTE


def test_no_provider_policy_declares_no_provider_route():
    decision = policy(task=workload(provider_required=False, capabilities=()))
    result = route(policy_decision=decision)
    assert result.status is ProviderRouteStatus.NO_PROVIDER_REQUIRED
    assert result.action is ProviderRouteAction.DECLARE_NO_PROVIDER_ROUTE
    assert result.selected_provider is None
    assert not result.route_declared


def test_withheld_policy_withholds_route():
    config = LocalFirstProviderConfig(allow_remote_fallback=False)
    decision = policy(
        config=config,
        health_result=health(
            items=(
                observation(
                    "gemini",
                    kind="remote",
                    model="gemini",
                    endpoint="https://example.invalid",
                ),
            )
        ),
    )
    assert decision.status is ProviderPolicyStatus.WITHHELD
    result = route(policy_decision=decision)
    assert result.status is ProviderRouteStatus.WITHHELD
    assert result.selected_provider is None


def test_not_requested_is_not_applicable():
    result = route(routing_requested=False)
    assert result.status is ProviderRouteStatus.NOT_APPLICABLE
    assert result.action is ProviderRouteAction.NONE


def test_preferred_local_provider_name_wins_before_latency():
    source = health(
        items=(
            observation("local-fast", model="fast", latency_ms=20),
            observation("ollama", model="llama3", latency_ms=100),
        )
    )
    decision = policy(health_result=source)
    result = route(policy_decision=decision)
    assert result.selected_provider.provider_name == "ollama"
    assert result.fallback_providers[0].provider_name == "local-fast"


def test_custom_local_preference_can_override_default():
    source = health(
        items=(
            observation("ollama", model="llama3", latency_ms=20),
            observation("mistral-local", model="mistral", latency_ms=100),
        )
    )
    decision = policy(health_result=source)
    config = GovernedProviderRoutingConfig(
        preferred_local_providers=("mistral-local", "ollama")
    )
    result = route(config=config, policy_decision=decision)
    assert result.selected_provider.provider_name == "mistral-local"


def test_lower_latency_breaks_unranked_provider_tie():
    source = health(
        items=(
            observation("local-slow", model="slow", latency_ms=200),
            observation("local-fast", model="fast", latency_ms=20),
        )
    )
    decision = policy(health_result=source)
    result = route(policy_decision=decision)
    assert result.selected_provider.provider_name == "local-fast"


def test_name_breaks_equal_latency_tie_deterministically():
    source = health(
        items=(
            observation("zeta", model="zeta", latency_ms=20),
            observation("alpha", model="alpha", latency_ms=20),
        )
    )
    decision = policy(health_result=source)
    result = route(policy_decision=decision)
    assert result.selected_provider.provider_name == "alpha"


def test_remote_preferences_rank_gemini_before_mistral():
    source = health(
        items=(
            observation(
                "mistral",
                kind="remote",
                model="mistral",
                endpoint="https://m.invalid",
                latency_ms=10,
            ),
            observation(
                "gemini",
                kind="remote",
                model="gemini",
                endpoint="https://g.invalid",
                latency_ms=100,
            ),
        )
    )
    decision = policy(
        health_result=source,
        task=workload(remote_required=True),
    )
    result = route(policy_decision=decision)
    assert result.selected_provider.provider_name == "gemini"
    assert result.fallback_providers[0].provider_name == "mistral"


def test_alternate_kind_is_appended_after_same_kind_fallbacks():
    source = health(
        items=(
            observation("ollama", model="llama3", latency_ms=80),
            observation("local-two", model="other", latency_ms=90),
            observation(
                "gemini",
                kind="remote",
                model="gemini",
                endpoint="https://g.invalid",
            ),
        )
    )
    decision = policy(health_result=source)
    result = route(policy_decision=decision)
    assert tuple(item.provider_name for item in result.fallback_providers) == (
        "local-two",
        "gemini",
    )


def test_route_never_authorizes_execution():
    result = route()
    assert not result.provider_call_allowed
    assert not result.inference_allowed
    assert not result.network_access_allowed
    assert not result.platform_mutation_allowed


def test_repository_stores_route_and_exposes_last():
    repository = InMemoryGovernedProviderRoutingRepository()
    router = GovernedProviderRouter(repository=repository)
    result = router.route(request(), now=NOW)
    assert repository.get(result.route_id) is result
    assert repository.list_all() == (result,)
    assert router.last_route is result


def test_empty_repository_has_no_last_route():
    assert GovernedProviderRouter().last_route is None


def test_duplicate_route_is_rejected():
    repository = InMemoryGovernedProviderRoutingRepository()
    router = GovernedProviderRouter(repository=repository)
    result = router.route(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_route_is_immutable():
    result = route()
    with pytest.raises(FrozenInstanceError):
        result.route_declared = False


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_policy_owner():
    with pytest.raises(ValueError, match="match policy owner"):
        request(owner="Other")


def test_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        GovernedProviderRouter().route(request(), now=NOW.replace(tzinfo=None))


def test_preference_names_must_not_be_blank():
    with pytest.raises(ValueError, match="must not be blank"):
        GovernedProviderRoutingConfig(preferred_local_providers=(" ",))


def test_local_preference_names_must_be_unique():
    with pytest.raises(ValueError, match="must be unique"):
        GovernedProviderRoutingConfig(preferred_local_providers=("ollama", "OLLAMA"))


def test_remote_preference_names_must_be_unique():
    with pytest.raises(ValueError, match="must be unique"):
        GovernedProviderRoutingConfig(preferred_remote_providers=("gemini", "GEMINI"))


def test_route_id_is_deterministic():
    first = route()
    second = GovernedProviderRouter().route(request(), now=NOW)
    assert first.route_id == second.route_id


def test_inconsistent_route_id_is_rejected():
    result = route()
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(result, route_id="wrong")


def test_selected_provider_cannot_be_a_fallback():
    result = route()
    with pytest.raises(ValueError, match="cannot also be a fallback"):
        replace(
            result,
            fallback_providers=(result.selected_provider,),
            route_id="",
        )


def test_fallbacks_must_be_unique():
    source = health(
        items=(
            observation("ollama", model="llama3"),
            observation("local-two", model="other"),
        )
    )
    decision = policy(health_result=source)
    result = route(policy_decision=decision)
    fallback = result.fallback_providers[0]
    with pytest.raises(ValueError, match="fallbacks must be unique"):
        replace(
            result,
            fallback_providers=(fallback, fallback),
            route_id="",
        )


def test_vision_route_selects_capable_remote_provider():
    source = health(
        items=(
            observation(),
            observation(
                "gemini",
                kind="remote",
                model="gemini",
                endpoint="https://g.invalid",
                capabilities=(ProviderCapability.TEXT, ProviderCapability.VISION),
            ),
        )
    )
    decision = policy(
        health_result=source,
        task=workload(
            kind="vision",
            capabilities=(ProviderCapability.VISION,),
        ),
    )
    result = route(policy_decision=decision)
    assert result.status is ProviderRouteStatus.ROUTED_REMOTE
    assert result.selected_provider.provider_name == "gemini"


def test_rationale_explains_selected_route():
    assert route().rationale == ("local_provider_route_selected",)


def test_policy_candidates_are_not_mutated():
    before = POLICY.eligible_local_providers
    route()
    assert POLICY.eligible_local_providers == before
