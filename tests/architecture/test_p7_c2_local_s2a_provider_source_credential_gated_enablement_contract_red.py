from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from app.governed_information_sources import (
    DEFAULT_GOVERNED_INFORMATION_SOURCES,
    GovernedInformationSource,
    GovernedInformationSources,
    InformationSourceKind,
)
from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryContract
from app.governed_source_query_executor import GovernedSourceQueryExecutor
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic
from infrastructure.config.secrets_loader import SecretsLoader

ROOT = Path(__file__).resolve().parents[2]
MODULE = "app.foursquare_governed_source"
SOURCE_ID = "foursquare_places"


def _provider_module():
    try:
        return __import__(MODULE, fromlist=["*"])
    except ModuleNotFoundError:
        pytest.fail("RED: bounded Foursquare governed source adapter is missing")


def _provider_type():
    module = _provider_module()
    provider_type = getattr(module, "FoursquareGovernedSourceAdapter", None)
    assert provider_type is not None, "RED: FoursquareGovernedSourceAdapter is missing"
    return provider_type


def _non_default_source(source_id: str = "contract_non_default"):
    return GovernedInformationSource(
        source_id=source_id,
        name="Contract non-default source",
        kind=InformationSourceKind.EDITORIAL,
        topics=frozenset({InterestTopic.CULTURE_CABA}),
    )


class _DeclaredAdapter:
    network_enabled = True
    automatic_fetch_enabled = False

    def __init__(self, declaration: GovernedInformationSource) -> None:
        self.source_declaration = declaration

    def execute(self, query):
        return ()


class _UndeclaredAdapter:
    network_enabled = True
    automatic_fetch_enabled = False

    def execute(self, query):
        return ()


def test_s2a_reuses_existing_secret_enablement_and_execution_authorities():
    assert callable(SecretsLoader.get)
    assert hasattr(
        OfficialConversationGateway,
        "register_governed_source_query_adapter",
    )
    assert callable(GovernedSourceQueryExecutor.register)
    assert callable(GovernedSourceQueryExecutor.execute)


def test_rc1_protected_gateway_remains_byte_identical():
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source


def test_rc1_m343_5_default_registry_remains_exactly_six_sources():
    assert len(DEFAULT_GOVERNED_INFORMATION_SOURCES) == 6
    assert len(GovernedInformationSources().snapshot.sources) == 6
    with pytest.raises(KeyError):
        GovernedInformationSources().source_for(SOURCE_ID)


def test_rc1_executor_registration_admits_adapter_carried_non_default_source():
    sources = GovernedInformationSources()
    contract = GovernedSourceQueryContract(sources)
    executor = GovernedSourceQueryExecutor(contract)
    declaration = _non_default_source()
    adapter = _DeclaredAdapter(declaration)

    executor.register(declaration.source_id, adapter)

    assert sources.source_for(declaration.source_id) == declaration
    assert len(GovernedInformationSources().snapshot.sources) == 6


def test_rc1_existing_contract_prepares_explicitly_admitted_non_default_source():
    sources = GovernedInformationSources()
    contract = GovernedSourceQueryContract(sources)
    executor = GovernedSourceQueryExecutor(contract)
    declaration = _non_default_source()
    executor.register(declaration.source_id, _DeclaredAdapter(declaration))
    query = GovernedSourceQuery(
        source_id=declaration.source_id,
        query_text="bounded local information",
        topics=frozenset({InterestTopic.CULTURE_CABA}),
    )

    prepared = contract.prepare(query)

    assert prepared.source == declaration


def test_rc1_unknown_source_without_declaration_fails_closed_at_registration():
    sources = GovernedInformationSources()
    contract = GovernedSourceQueryContract(sources)
    executor = GovernedSourceQueryExecutor(contract)

    with pytest.raises((KeyError, ValueError)):
        executor.register("undeclared_source", _UndeclaredAdapter())


def test_rc1_declaration_and_registration_identity_must_match():
    sources = GovernedInformationSources()
    contract = GovernedSourceQueryContract(sources)
    executor = GovernedSourceQueryExecutor(contract)
    declaration = _non_default_source("declared_identity")

    with pytest.raises(ValueError):
        executor.register("different_identity", _DeclaredAdapter(declaration))


def test_s2a_provider_adapter_exists_under_existing_query_adapter_protocol():
    provider_type = _provider_type()
    assert callable(getattr(provider_type, "execute", None))
    assert getattr(provider_type, "SOURCE_ID", None) == SOURCE_ID


def test_s2a_adapter_requires_credential_at_construction_boundary():
    signature = inspect.signature(_provider_type())
    names = set(signature.parameters)
    assert {"api_key", "transport"}.issubset(names)
    assert signature.parameters["api_key"].default is inspect.Parameter.empty


def test_s2a_missing_or_blank_credential_fails_closed():
    provider_type = _provider_type()
    with pytest.raises((TypeError, ValueError)):
        provider_type(api_key="", transport=lambda *_: b"{}")


def test_s2a_adapter_snapshot_never_exposes_secret():
    provider_type = _provider_type()
    adapter = provider_type(api_key="fake-secret", transport=lambda *_: b"{}")
    snapshot = adapter.snapshot
    rendered = repr(snapshot).casefold()
    assert "fake-secret" not in rendered
    assert "api_key" not in rendered
    assert snapshot.network_enabled is True
    assert snapshot.automatic_fetch_enabled is False


def test_s2a_environment_wiring_uses_existing_secrets_loader_and_feature_gate():
    from app import runtime_environment_wiring as wiring

    builder = getattr(
        wiring,
        "build_foursquare_governed_source_from_environment",
        None,
    )
    assert callable(builder), "RED: provider environment builder is missing"
    source = inspect.getsource(builder)
    assert "SecretsLoader" in source
    assert "environment_flag" in source
    assert "FoursquareGovernedSourceAdapter" in source


def test_s2a_query_preparation_cannot_enable_or_execute_provider():
    from app.governed_place_business_source_query_composition import (
        GovernedPlaceBusinessSourceQueryComposition,
    )

    source = inspect.getsource(GovernedPlaceBusinessSourceQueryComposition)
    forbidden = (
        "enable_foursquare_governed_source",
        "register_governed_source_query_adapter",
        "execute_governed_source_query",
        "SecretsLoader",
    )
    assert not any(token in source for token in forbidden)


def test_s2a_provider_adapter_has_no_implicit_ip_geolocation_fallback():
    source = inspect.getsource(_provider_type())
    lowered = source.casefold()
    assert "ip geolocation" not in lowered
    assert "ip_geolocation" not in lowered
    assert "ipinfo" not in lowered
    assert "geolocate" not in lowered


def test_s2a_provider_adapter_supports_injected_transport_without_live_network():
    signature = inspect.signature(_provider_type())
    assert "transport" in signature.parameters
    source = inspect.getsource(_provider_type())
    assert "self._transport" in source


def test_s2a_does_not_create_parallel_authority_or_expand_execution_scope():
    provider_source = inspect.getsource(_provider_type())
    executor_source = inspect.getsource(GovernedSourceQueryExecutor)
    from app import runtime_environment_wiring as wiring

    combined = provider_source + executor_source + inspect.getsource(wiring)
    forbidden = (
        "FoursquareBrain",
        "FoursquareManager",
        "ProviderManager",
        "RestaurantAgent",
        "LocalBrain",
        "MapsBrain",
        "retrieval_enabled=True",
        "MemoryGateway",
        "LearningGateway",
        "PlanningGateway",
        "ExecutionGateway",
        "reserve(",
        "book(",
        "navigate(",
    )
    assert not any(token in combined for token in forbidden)
