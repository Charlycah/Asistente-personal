from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.runtime_root_factory import build_runtime_root
from core.cognitive_runtime_orchestration import (
    VISUAL_CONTEXT_STAGE,
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
    GovernedVisualCognitiveContextBridge,
)
from core.llm_provider import LLMRequest
from core.visual_context_integration import (
    IntegratedVisualContext,
    VisualIntegrationAction,
    VisualIntegrationStatus,
)

NOW = datetime(2026, 9, 19, 22, 0, tzinfo=timezone.utc)


def _productive_runtime(monkeypatch) -> CognitiveRuntimeOrchestrator:
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    composition = build_runtime_root().compose()
    runtime = composition.preparation.dependencies.cognitive_runtime
    assert isinstance(runtime, CognitiveRuntimeOrchestrator)
    return runtime


def _ready_visual(owner: str = "Carlos") -> IntegratedVisualContext:
    scene = SimpleNamespace(
        understanding_id="scene-r2p-registration",
        dominant_scene=SimpleNamespace(value="workspace"),
        attributes=("indoor", "desk"),
    )
    objects = SimpleNamespace(
        profile_id="objects-r2p-registration",
        objects=(SimpleNamespace(label="laptop", count=1, confidence=0.96),),
    )
    attention = SimpleNamespace(
        plan_id="attention-r2p-registration",
        focus_items=(
            SimpleNamespace(
                object_ref="laptop",
                priority=SimpleNamespace(value="high"),
            ),
        ),
    )
    request = SimpleNamespace(
        owner=owner,
        visual_context=SimpleNamespace(context_id="visual-r2p-registration"),
        resolved_observation=SimpleNamespace(
            resolution_id="resolution-r2p-registration"
        ),
        scene_understanding=scene,
        object_knowledge=objects,
        attention_plan=attention,
        integration_requested=True,
    )
    return IntegratedVisualContext(
        request=request,
        status=VisualIntegrationStatus.READY,
        action=VisualIntegrationAction.INTEGRATE,
        visual_context_id="visual-r2p-registration",
        resolution_id="resolution-r2p-registration",
        scene_understanding_id="scene-r2p-registration",
        object_knowledge_id="objects-r2p-registration",
        attention_plan_id="attention-r2p-registration",
        observation_context_available=True,
        resolution_available=True,
        scene_understanding_available=True,
        object_knowledge_available=True,
        attention_available=True,
        confirmation_required=False,
        pixel_access_allowed=False,
        camera_control_allowed=False,
        object_detection_allowed=False,
        object_tracking_allowed=False,
        text_extraction_allowed=False,
        product_search_allowed=False,
        place_recognition_allowed=False,
        biometric_analysis_allowed=False,
        rationale=("r2p:productive-registration-ready",),
        created_at=NOW,
    )


def _visual_contributors(runtime: CognitiveRuntimeOrchestrator):
    return tuple(
        contributor
        for contributor in runtime.contributors
        if contributor.name.strip().casefold() == VISUAL_CONTEXT_STAGE
    )


def test_red_r2p_official_runtime_registers_exactly_one_visual_bridge(monkeypatch):
    runtime = _productive_runtime(monkeypatch)

    visual = _visual_contributors(runtime)

    assert len(visual) == 1
    assert isinstance(visual[0], GovernedVisualCognitiveContextBridge)


def test_red_r2p_productive_visual_bridge_is_stateless(monkeypatch):
    runtime = _productive_runtime(monkeypatch)

    visual = _visual_contributors(runtime)

    assert len(visual) == 1
    assert visual[0].context is None


def test_red_r2p_visual_registration_preserves_existing_productive_stages(monkeypatch):
    runtime = _productive_runtime(monkeypatch)
    stages = tuple(item.name.strip().casefold() for item in runtime.contributors)

    assert stages.count(VISUAL_CONTEXT_STAGE) == 1
    assert stages.count("reasoning") == 1
    assert any("library" in stage for stage in stages)


def test_red_r2p_ready_visual_reaches_registered_bridge_in_productive_runtime(
    monkeypatch,
):
    runtime = _productive_runtime(monkeypatch)
    context = _ready_visual()

    result = runtime.enrich(
        owner="Carlos",
        session_id="r2p-registration",
        text="Analizá el entorno",
        request=LLMRequest(
            prompt="Analizá el entorno",
            system_prompt="Sistema ROBY",
        ),
        now=NOW,
        integrated_visual_context=context,
    )
    visual = tuple(
        item for item in result.contributions if item.stage == VISUAL_CONTEXT_STAGE
    )

    assert len(visual) == 1
    assert visual[0].status is CognitiveRuntimeStageStatus.APPLIED
    assert context.integration_id in visual[0].reference_ids


def test_red_r2p_registered_bridge_keeps_absent_visual_turn_neutral(monkeypatch):
    runtime = _productive_runtime(monkeypatch)

    visual = _visual_contributors(runtime)
    assert len(visual) == 1
    contribution = visual[0].build(
        None,
        owner="Carlos",
        session_id="r2p-registration-neutral",
    )
    assert contribution.status is CognitiveRuntimeStageStatus.SKIPPED
    assert contribution.prompt_lines == ()
    assert contribution.reference_ids == ()
    assert contribution.rationale == ("visual_context:not_supplied",)
