from __future__ import annotations

import importlib
import inspect

from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelector,
)
from app.governed_information_sources import (
    GovernedInformationSource,
    InformationEvidenceKind,
)
from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

MODULE = "app.governed_scientific_evidence_source_discrimination"
TYPE = "GovernedScientificEvidenceSourceDiscrimination"


def _seam_type() -> type:
    try:
        module = importlib.import_module(MODULE)
    except ModuleNotFoundError:
        raise AssertionError(
            "RED: bounded scientific evidence-source discrimination seam is missing"
        ) from None
    return getattr(module, TYPE)


def test_existing_source_and_evidence_authorities_are_reused() -> None:
    assert OfficialKnowledgeRuntimeGateway is not None
    assert DiscriminatingEvidenceRequirement is not None
    assert GovernedConversationalSourceSelector is not None
    assert GovernedInformationSource is not None
    assert InformationEvidenceKind is not None


def test_red_bounded_scientific_source_discrimination_seam_exists() -> None:
    seam = _seam_type()
    assert inspect.isclass(seam)


def test_red_seam_requires_explicit_scientific_intent_and_evidence_need() -> None:
    seam = _seam_type()
    signature = inspect.signature(seam.discriminate)
    assert "explicit_scientific_intent" in signature.parameters
    assert "requirement" in signature.parameters


def test_red_seam_reuses_registered_governed_source_contracts() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    assert "DiscriminatingEvidenceRequirement" in source
    assert "GovernedInformationSource" in source
    assert "GovernedConversationalSourceSelector" in source


def test_red_source_discrimination_stops_before_retrieval_or_network() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "OfficialExternalRetrievalRuntimeGateway",
        "OfficialUnifiedRetrievalExecutionRuntimeGateway",
        "retrieval_enabled=True",
        "requests.",
        "httpx.",
        "urllib.request",
        "subprocess.",
    )
    assert not any(token in source for token in forbidden)


def test_red_source_discrimination_does_not_claim_truth_or_sufficiency() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "GovernedEpistemicSufficiencyAssessment(",
        "OfficialGovernedReasoningRuntimeGateway(",
        "establishes_truth=True",
        "truth_certified=True",
    )
    assert not any(token in source for token in forbidden)


def test_red_unknown_or_unsupported_source_need_must_fail_closed() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    assert "UNAVAILABLE" in source or "NOT_SUPPORTED" in source


def test_red_creates_no_parallel_brain_selector_or_authority() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "ScientificBrain",
        "ScientificAgent",
        "ScientificRetrievalCoordinator",
        "ScientificSourceManager",
        "ScientificReasoningGateway",
        "ScientificEvidenceStore",
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
