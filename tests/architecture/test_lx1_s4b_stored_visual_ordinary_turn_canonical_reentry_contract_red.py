from __future__ import annotations

import inspect

from app import desktop_ui, official_conversation_gateway, runtime_ui_adapter
from core.cognitive_runtime_orchestration import runtime as cognitive_runtime
from core.end_to_end_local_conversation import runtime as local_runtime
from core.governed_operational_conversation_pipeline.models import (
    GovernedConversationPipelineRequest,
)


def test_s4b_canonical_request_already_owns_integrated_visual_context():
    fields = GovernedConversationPipelineRequest.__dataclass_fields__

    assert "integrated_visual_context" in fields
    assert "explicit_image_ids" not in fields


def test_s4b_existing_cognitive_runtime_consumes_canonical_visual_context():
    source = inspect.getsource(cognitive_runtime.CognitiveRuntimeOrchestrator)

    assert "integrated_visual_context" in source
    assert "visual_context_contribution" in source
    assert "explicit_document_ids" in source


def test_s4b_desktop_reenters_stored_visual_context_with_same_turn_documents():
    source = inspect.getsource(desktop_ui.ROBYDesktopApp)

    assert "analyze_image_for_cognitive_convergence(" in source
    assert "stored.image_id" in source
    assert "integrated_visual_context=" in source
    assert "explicit_document_ids=" in source
    assert "explicit_image_ids" not in source


def test_s4b_desktop_transport_preserves_existing_visual_context_field():
    protocol_source = inspect.getsource(desktop_ui.DesktopROBYAdapter)
    controller_source = inspect.getsource(
        desktop_ui.DesktopConversationController.submit
    )

    assert "integrated_visual_context" in protocol_source
    assert "integrated_visual_context" in controller_source
    assert "explicit_image_ids" not in protocol_source
    assert "explicit_image_ids" not in controller_source


def test_s4b_runtime_transport_reuses_canonical_visual_context_field():
    ui_source = inspect.getsource(
        runtime_ui_adapter.LocalConversationUIAdapter.submit_text
    )
    gateway_source = inspect.getsource(
        official_conversation_gateway.OfficialConversationGateway.submit
    )
    local_source = inspect.getsource(local_runtime.EndToEndLocalConversation.converse)

    assert "integrated_visual_context" in ui_source
    assert "integrated_visual_context" in gateway_source
    assert "integrated_visual_context" in local_source


def test_s4b_reentry_creates_no_parallel_visual_or_reasoning_authority():
    source = inspect.getsource(desktop_ui.ROBYDesktopApp)

    forbidden = (
        "FileImageRepository(",
        "OfficialVisionCore(",
        "GovernedVisualSemanticComposition(",
        "GovernedVisualCognitiveContextBridge(",
        "CognitiveRuntimeOrchestrator(",
        "OfficialGovernedReasoningRuntimeGateway(",
        "explicit_image_ids",
    )
    assert all(item not in source for item in forbidden)
