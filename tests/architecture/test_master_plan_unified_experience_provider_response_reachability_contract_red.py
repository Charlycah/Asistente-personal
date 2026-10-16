from __future__ import annotations

import inspect
from dataclasses import fields
from pathlib import Path

from app.unified_experience_layer import UnifiedExperienceLayer
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalConversationPipeline,
)
from core.operational_response_assembly import OperationalResponse
from core.runtime_composition_root.models import RuntimeCompositionDependencies

ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "app/runtime_root_factory.py"
COMPOSITION_ROOT = ROOT / "core/runtime_composition_root/root.py"
PIPELINE = ROOT / "core/governed_operational_conversation_pipeline/pipeline.py"

PRESERVED_FIELDS = {
    "request",
    "status",
    "action",
    "evidence",
    "limitations",
    "provider_execution_id",
    "retrieval_execution_id",
    "provider_call_performed",
    "retrieval_performed",
    "network_access_performed",
    "platform_mutation_performed",
    "rationale",
    "created_at",
}


def test_red_1_existing_unified_experience_has_typed_provider_projection() -> None:
    method = getattr(UnifiedExperienceLayer, "present_operational_response", None)
    assert callable(method), (
        "RED: canonical UnifiedExperienceLayer cannot yet present an "
        "OperationalResponse without interception coercion"
    )
    annotation = inspect.signature(method).return_annotation
    assert annotation in {OperationalResponse, "OperationalResponse"}


def test_red_2_provider_projection_contract_preserves_operational_lineage() -> None:
    method = getattr(UnifiedExperienceLayer, "present_operational_response", None)
    assert callable(method), "RED: typed provider-response presentation is missing"
    source = inspect.getsource(method)
    assert "response_text" in source
    assert "replace(" in source
    assert "response_id=" in source
    assert 'response_id=""' in source or "response_id = " in source
    assert PRESERVED_FIELDS <= {item.name for item in fields(OperationalResponse)}


def test_red_3_pipeline_owns_one_optional_presentation_dependency() -> None:
    signature = inspect.signature(GovernedOperationalConversationPipeline.__init__)
    assert "experience_layer" in signature.parameters
    source = inspect.getsource(GovernedOperationalConversationPipeline.__init__)
    assert "self.experience_layer = experience_layer" in source


def test_red_4_provider_response_is_presented_post_assembly_pre_result() -> None:
    source = inspect.getsource(GovernedOperationalConversationPipeline.process)
    assembly = source.index("self.response_assembler.assemble(")
    presentation = source.index("present_operational_response")
    result = source.index("GovernedConversationPipelineResult(")
    assert assembly < presentation < result
    assert "GovernedOperationalInterception(" not in source


def test_red_5_existing_composition_reuses_same_canonical_layer() -> None:
    models_source = inspect.getsource(RuntimeCompositionDependencies)
    root_source = COMPOSITION_ROOT.read_text(encoding="utf-8")
    factory_source = FACTORY.read_text(encoding="utf-8")
    assert "experience_layer" in models_source
    assert "experience_layer=dependencies.experience_layer" in root_source
    assert "unified_experience_layer = UnifiedExperienceLayer()" in factory_source
    assert "experience_layer=unified_experience_layer" in factory_source
    assert factory_source.count("UnifiedExperienceLayer()") == 1


def test_red_6_interception_authority_is_not_repurposed() -> None:
    source = PIPELINE.read_text(encoding="utf-8")
    assert "operational_interceptor.intercept(" in source
    assert "operational_interceptor.present" not in source
    assert "operational_interceptor.present_operational_response" not in source


def test_red_7_no_parallel_humanization_authority_is_introduced() -> None:
    source = FACTORY.read_text(encoding="utf-8")
    forbidden = (
        "HumanizationManager(",
        "HumanizationEngine(",
        "ProviderExperienceLayer(",
        "ResponseHumanizer(",
        "PersonalityRenderer(",
    )
    assert all(item not in source for item in forbidden)
    assert source.count("UnifiedExperienceLayer()") == 1
