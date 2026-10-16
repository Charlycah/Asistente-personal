from __future__ import annotations

import inspect
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from core.cognitive_runtime_orchestration import (
    VISUAL_CONTEXT_STAGE,
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
    GovernedVisualCognitiveContextBridge,
)
from core.cognitive_runtime_orchestration.models import CognitiveRuntimeContributor
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root.preparation import GovernedRuntimePreparation
from core.visual_context_integration import (
    IntegratedVisualContext,
    VisualIntegrationAction,
    VisualIntegrationStatus,
)

NOW = datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc)


def _context(
    *,
    owner: str = "Carlos",
    status: VisualIntegrationStatus = VisualIntegrationStatus.READY,
) -> IntegratedVisualContext:
    ready = status is VisualIntegrationStatus.READY
    scene = SimpleNamespace(
        understanding_id="scene-r1",
        dominant_scene=SimpleNamespace(value="workspace"),
        attributes=("indoor", "desk"),
    )
    objects = SimpleNamespace(
        profile_id="objects-r1",
        objects=(SimpleNamespace(label="laptop", count=1, confidence=0.96),),
    )
    attention = SimpleNamespace(
        plan_id="attention-r1",
        focus_items=(
            SimpleNamespace(
                object_ref="laptop",
                priority=SimpleNamespace(value="high"),
            ),
        ),
    )
    request = SimpleNamespace(
        owner=owner,
        visual_context=SimpleNamespace(context_id="visual-r1"),
        resolved_observation=(
            SimpleNamespace(resolution_id="resolution-r1") if ready else None
        ),
        scene_understanding=scene if ready else None,
        object_knowledge=objects if ready else None,
        attention_plan=attention if ready else None,
        integration_requested=True,
    )
    return IntegratedVisualContext(
        request=request,
        status=status,
        action=(
            VisualIntegrationAction.INTEGRATE
            if ready
            else VisualIntegrationAction.WITHHOLD
        ),
        visual_context_id="visual-r1" if ready else None,
        resolution_id="resolution-r1" if ready else None,
        scene_understanding_id="scene-r1" if ready else None,
        object_knowledge_id="objects-r1" if ready else None,
        attention_plan_id="attention-r1" if ready else None,
        observation_context_available=ready,
        resolution_available=ready,
        scene_understanding_available=ready,
        object_knowledge_available=ready,
        attention_available=ready,
        confirmation_required=False,
        pixel_access_allowed=False,
        camera_control_allowed=False,
        object_detection_allowed=False,
        object_tracking_allowed=False,
        text_extraction_allowed=False,
        product_search_allowed=False,
        place_recognition_allowed=False,
        biometric_analysis_allowed=False,
        rationale=("r1:ready" if ready else "r1:withheld",),
        created_at=NOW,
    )


def _llm_request(text: str = "Analizá el entorno") -> LLMRequest:
    return LLMRequest(prompt=text, system_prompt="Sistema ROBY")


def test_red_r1_pipeline_request_carries_integrated_visual_context_turn_scoped():
    context = _context()

    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="session-r1",
        text="Analizá el entorno",
        integrated_visual_context=context,
    )

    assert request.integrated_visual_context is context


def test_red_r1_existing_visual_bridge_consumes_turn_scoped_context_in_runtime():
    context = _context()
    runtime = CognitiveRuntimeOrchestrator((GovernedVisualCognitiveContextBridge(),))

    result = runtime.enrich(
        owner="Carlos",
        session_id="session-r1",
        text="Analizá el entorno",
        request=_llm_request(),
        now=NOW,
        integrated_visual_context=context,
    )

    visual = next(
        item for item in result.contributions if item.stage == VISUAL_CONTEXT_STAGE
    )
    assert visual.status is CognitiveRuntimeStageStatus.APPLIED
    assert context.integration_id in visual.reference_ids
    assert "visual-r1" in visual.reference_ids
    assert "scene-r1" in visual.reference_ids
    assert "objects-r1" in visual.reference_ids
    assert "attention-r1" in visual.reference_ids
    assert "no certifica verdad" in result.request.prompt


def test_red_r1_absent_visual_is_exactly_neutral_for_request():
    runtime = CognitiveRuntimeOrchestrator((GovernedVisualCognitiveContextBridge(),))
    original = _llm_request("Turno sin imagen")

    result = runtime.enrich(
        owner="Carlos",
        session_id="session-r1",
        text="Turno sin imagen",
        request=original,
        now=NOW,
        integrated_visual_context=None,
    )

    assert result.request == original
    visual = next(
        item for item in result.contributions if item.stage == VISUAL_CONTEXT_STAGE
    )
    assert visual.status is CognitiveRuntimeStageStatus.SKIPPED
    assert visual.rationale == ("visual_context:not_supplied",)


def test_red_r1_owner_mismatch_remains_fail_closed_when_transport_is_turn_scoped():
    runtime = CognitiveRuntimeOrchestrator((GovernedVisualCognitiveContextBridge(),))

    result = runtime.enrich(
        owner="Carlos",
        session_id="session-r1",
        text="Analizá el entorno",
        request=_llm_request(),
        now=NOW,
        integrated_visual_context=_context(owner="Cristina"),
    )

    visual = next(
        item for item in result.contributions if item.stage == VISUAL_CONTEXT_STAGE
    )
    assert visual.status is CognitiveRuntimeStageStatus.SKIPPED
    assert visual.rationale == ("visual_context:owner_lineage_mismatch",)
    assert result.request == _llm_request()


def test_red_r1_preparation_forwards_only_the_current_request_visual_context():
    source = inspect.getsource(GovernedRuntimePreparation.prepare)

    assert "integrated_visual_context=request.integrated_visual_context" in source
    assert "latest_visual" not in source.casefold()
    assert "visual_context_repository" not in source.casefold()


def test_red_r1_does_not_expand_common_contributor_protocol_or_visual_authority():
    signature = inspect.signature(CognitiveRuntimeContributor.contribute)
    assert "integrated_visual_context" not in signature.parameters

    bridge = GovernedVisualCognitiveContextBridge()
    with pytest.raises(AttributeError):
        getattr(bridge, "remember")
    with pytest.raises(AttributeError):
        getattr(bridge, "learn")
    with pytest.raises(AttributeError):
        getattr(bridge, "execute")
