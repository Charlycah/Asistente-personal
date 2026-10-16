from __future__ import annotations

import importlib
import inspect
from pathlib import Path

import pytest

from app.governed_external_information_source_integration import (
    GovernedExternalInformationSourceIntegration,
)
from app.governed_place_business_source_query_composition import (
    GovernedPlaceBusinessSourceQueryComposition,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.governed_external_intelligence.models import (
    ExternalIntelligenceCapability,
    ExternalIntelligenceRequest,
)

ROOT = Path(__file__).resolve().parents[2]
MODULE = "app.governed_place_business_external_execution_composition"


def _seam_type() -> type:
    try:
        module = importlib.import_module(MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: authorized place/business execution to M400 composition is missing"
        )
    seam = getattr(
        module,
        "GovernedPlaceBusinessExternalExecutionComposition",
        None,
    )
    assert seam is not None, "RED: S2B-A composition type is missing"
    return seam


def test_s2b_a_reuses_existing_execution_and_m400_authorities() -> None:
    assert callable(OfficialConversationGateway.execute_governed_source_query)
    assert callable(GovernedExternalInformationSourceIntegration.admit_query_result)
    assert ExternalIntelligenceRequest is not None
    assert ExternalIntelligenceCapability.INFORMATION_SOURCE.value == (
        "information_source"
    )


def test_s2b_a_preserves_s1_stop_before_retrieval() -> None:
    source = inspect.getsource(GovernedPlaceBusinessSourceQueryComposition)
    assert "composition_stops_before_retrieval" in source
    assert "execute_governed_source_query" not in source
    assert "ExternalIntelligenceRequest" not in source


def test_s2b_a_composition_exists_under_application_composition_family() -> None:
    seam = _seam_type()
    assert seam.__module__ == MODULE


def test_s2b_a_requires_explicit_external_access_authorization() -> None:
    source = inspect.getsource(_seam_type())
    assert "external_access" in source
    assert "authorized" in source.casefold()
    assert "ExternalIntelligenceRequest" in source
    assert "external_access_requested" in source


def test_s2b_a_consumes_only_an_already_prepared_s1_result() -> None:
    source = inspect.getsource(_seam_type())
    assert "prepared_query" in source
    assert "PREPARED" in source
    assert "GovernedPlaceBusinessSourceQueryComposition" not in source


def test_s2b_a_executes_through_existing_gateway_surface() -> None:
    source = inspect.getsource(_seam_type())
    assert "execute_governed_source_query" in source
    assert "GovernedSourceQueryExecutor(" not in source
    assert "register_governed_source_query_adapter" not in source


def test_s2b_a_uses_existing_information_source_m400_ingress() -> None:
    source = inspect.getsource(_seam_type())
    assert "GovernedExternalInformationSourceIntegration" in source
    assert "ExternalIntelligenceCapability.INFORMATION_SOURCE" in source
    assert "admit_" in source


def test_s2b_a_preserves_source_identity_and_network_provenance() -> None:
    source = inspect.getsource(_seam_type())
    assert "target_id" in source
    assert "network_used" in source
    assert "source_id" in source


def test_s2b_a_stops_at_m400_without_m401_or_conversation_publication() -> None:
    source = inspect.getsource(_seam_type())
    forbidden = (
        "CognitiveExternalEvidenceLineage",
        "CognitiveExternalEvidenceAdmission",
        "build_external_evidence_contribution",
        "external_evidence=",
        ".submit(",
        ".converse(",
    )
    assert not any(token in source for token in forbidden)


def test_s2b_a_does_not_expand_authority_or_execution_scope() -> None:
    source = inspect.getsource(_seam_type())
    forbidden = (
        "LocalBrain",
        "MapsBrain",
        "RestaurantAgent",
        "ProviderManager",
        "retrieval_enabled=True",
        "MemoryGateway",
        "LearningGateway",
        "PlanningGateway",
        "ExecutionGateway",
        "reserve(",
        "book(",
        "navigate(",
    )
    assert not any(token in source for token in forbidden)


def test_s2b_a_protected_gateway_remains_byte_identical() -> None:
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source
