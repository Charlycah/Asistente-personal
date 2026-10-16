from __future__ import annotations

import importlib
import inspect

import pytest

from app.governed_place_business_external_execution_composition import (
    GovernedPlaceBusinessExternalExecutionComposition,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_runtime_orchestration import (
    CognitiveExternalEvidenceAdmission,
    CognitiveExternalEvidenceLineage,
)
from core.governed_external_intelligence import (
    GovernedExternalEvidenceAssessor,
    GovernedExternalIntelligenceVerifier,
)

MODULE = "app.governed_external_cognitive_admission_composition"
TYPE = "GovernedExternalCognitiveAdmissionComposition"


def _seam_type() -> type:
    try:
        module = importlib.import_module(MODULE)
    except ModuleNotFoundError:
        pytest.fail("RED: M400 to M401 governed admission composition is missing")
    seam = getattr(module, TYPE, None)
    assert seam is not None, "RED: S2B-B composition type is missing"
    return seam


def test_s2b_b_reuses_existing_m400_m401_and_conversation_authorities() -> None:
    assert callable(GovernedExternalIntelligenceVerifier.verify)
    assert callable(GovernedExternalEvidenceAssessor.assess)
    assert CognitiveExternalEvidenceLineage is not None
    assert CognitiveExternalEvidenceAdmission is not None
    assert "external_evidence" in inspect.signature(
        OfficialConversationGateway.submit
    ).parameters


def test_s2b_b_preserves_s2b_a_stop_at_m400() -> None:
    source = inspect.getsource(GovernedPlaceBusinessExternalExecutionComposition)
    assert "ExternalIntelligenceEnvelope" in source
    assert "CognitiveExternalEvidenceAdmission" not in source
    assert "CognitiveExternalEvidenceLineage" not in source
    assert ".submit(" not in source


def test_s2b_b_composition_exists_under_application_composition_family() -> None:
    seam = _seam_type()
    assert seam.__module__ == MODULE


def test_s2b_b_accepts_existing_m400_envelope_and_assessment_time() -> None:
    source = inspect.getsource(_seam_type())
    assert "ExternalIntelligenceEnvelope" in source
    assert "assessed_at" in source
    assert "datetime" in source


def test_s2b_b_uses_existing_verifier_and_assessor() -> None:
    source = inspect.getsource(_seam_type())
    assert "GovernedExternalIntelligenceVerifier" in source
    assert "GovernedExternalEvidenceAssessor" in source
    assert ".verify(" in source
    assert ".assess(" in source


def test_s2b_b_constructs_existing_lineage_and_admission() -> None:
    source = inspect.getsource(_seam_type())
    assert "CognitiveExternalEvidenceLineage" in source
    assert "CognitiveExternalEvidenceAdmission" in source
    assert "evidence=" in source


def test_s2b_b_derives_admission_status_from_existing_assessment() -> None:
    source = inspect.getsource(_seam_type())
    assert "ExternalEvidenceAssessmentStatus" in source
    assert "CognitiveExternalEvidenceAdmissionStatus" in source
    assert "REJECTED" in source
    assert "LIMITED" in source
    assert "ADMITTED" in source


def test_s2b_b_preserves_limitations_and_explicit_rationale() -> None:
    source = inspect.getsource(_seam_type())
    assert "limitations" in source
    assert "rationale" in source
    assert "truth" in source.casefold()


def test_s2b_b_exposes_admission_for_existing_conversational_handoff() -> None:
    source = inspect.getsource(_seam_type())
    assert "CognitiveExternalEvidenceAdmission" in source
    assert ".submit(" not in source
    assert ".converse(" not in source


def test_s2b_b_does_not_execute_provider_or_authorize_network() -> None:
    source = inspect.getsource(_seam_type())
    forbidden = (
        "execute_governed_source_query",
        "GovernedSourceQueryExecutor",
        "ExternalIntelligenceRequest(",
        "external_access_requested",
        "Foursquare",
        "network_used=",
    )
    assert not any(token in source for token in forbidden)


def test_s2b_b_does_not_expand_persistence_or_action_authority() -> None:
    source = inspect.getsource(_seam_type())
    forbidden = (
        "MemoryGateway",
        "LearningGateway",
        "PlanningGateway",
        "ExecutionGateway",
        "persistence_authorized=True",
        "execution_authorized=True",
        "reserve(",
        "book(",
        "navigate(",
    )
    assert not any(token in source for token in forbidden)
