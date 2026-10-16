from __future__ import annotations

import importlib
import inspect

from app.governed_external_information_source_integration import (
    GovernedExternalInformationSourceIntegration,
)
from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from core.cognitive_runtime_orchestration.external_evidence import (
    CognitiveExternalEvidenceAdmission,
)

MODULE = "app.governed_external_evidence_reasoning_composition"
TYPE = "GovernedExternalEvidenceReasoningComposition"


def _seam_type() -> type:
    module = importlib.import_module(MODULE)
    return getattr(module, TYPE)


def test_existing_authorities_are_reused_not_replaced() -> None:
    assert GovernedExternalInformationSourceIntegration is not None
    assert CognitiveExternalEvidenceAdmission is not None
    assert OfficialGovernedReasoningRuntimeGateway is not None


def test_red_bounded_composition_seam_exists() -> None:
    seam = _seam_type()
    assert inspect.isclass(seam)


def test_red_seam_references_existing_external_admission_contract() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    assert "CognitiveExternalEvidenceAdmission" in source
    assert "OfficialGovernedReasoningRuntimeGateway" in source


def test_red_requires_explicit_external_intent() -> None:
    seam = _seam_type()
    signature = inspect.signature(seam.compose)
    assert "explicit_external_intent" in signature.parameters


def test_red_does_not_create_parallel_retrieval_or_reasoning_authority() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "WebBrain",
        "ScientificBrain",
        "ExternalReasoningBrain",
        "RetrievalCoordinator",
        "ExternalEvidenceStore",
    )
    assert not any(token in source for token in forbidden)


def test_red_does_not_enable_global_retrieval_or_network_execution() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "retrieval_enabled=True",
        "requests.",
        "httpx.",
        "subprocess.",
    )
    assert not any(token in source for token in forbidden)


def test_red_preserves_no_memory_learning_planning_execution_authority() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "remember_governed_learning",
        "memory_gateway.write",
        "learning_gateway",
        "planning_gateway",
        "execution_gateway",
        "publish_text",
    )
    assert not any(token in source for token in forbidden)
