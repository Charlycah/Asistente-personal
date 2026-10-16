from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

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

NOW = datetime(2026, 8, 24, 14, 0, tzinfo=timezone.utc)


def _context(
    *,
    owner: str = "Carlos",
    status: VisualIntegrationStatus = VisualIntegrationStatus.READY,
) -> IntegratedVisualContext:
    ready = status is VisualIntegrationStatus.READY
    scene = SimpleNamespace(
        understanding_id="scene-1",
        dominant_scene=SimpleNamespace(value="workspace"),
        attributes=("indoor", "desk"),
    )
    objects = SimpleNamespace(
        profile_id="objects-1",
        objects=(
            SimpleNamespace(label="laptop", count=1, confidence=0.96),
            SimpleNamespace(label="taza", count=1, confidence=0.89),
        ),
    )
    attention = SimpleNamespace(
        plan_id="attention-1",
        focus_items=(
            SimpleNamespace(
                object_ref="laptop",
                priority=SimpleNamespace(value="high"),
            ),
        ),
    )
    request = SimpleNamespace(
        owner=owner,
        visual_context=SimpleNamespace(context_id="visual-1"),
        resolved_observation=SimpleNamespace(resolution_id="resolution-1"),
        scene_understanding=scene,
        object_knowledge=objects,
        attention_plan=attention,
        integration_requested=True,
    )
    if not ready:
        request = SimpleNamespace(
            owner=owner,
            visual_context=SimpleNamespace(context_id="visual-1"),
            resolved_observation=None,
            scene_understanding=None,
            object_knowledge=None,
            attention_plan=None,
            integration_requested=True,
        )
    action = (
        VisualIntegrationAction.INTEGRATE
        if ready
        else VisualIntegrationAction.WITHHOLD
    )
    return IntegratedVisualContext(
        request=request,
        status=status,
        action=action,
        visual_context_id="visual-1" if ready else None,
        resolution_id="resolution-1" if ready else None,
        scene_understanding_id="scene-1" if ready else None,
        object_knowledge_id="objects-1" if ready else None,
        attention_plan_id="attention-1" if ready else None,
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
        rationale=("challenge:ready" if ready else "challenge:withheld",),
        created_at=NOW,
    )


def _request(text: str = "¿Qué ves?") -> LLMRequest:
    return LLMRequest(prompt=text, system_prompt="Sistema ROBY")


def test_vm1_ready_visual_context_becomes_cognitive_contribution():
    result = GovernedVisualCognitiveContextBridge(_context()).build(
        _context(), owner="Carlos", session_id="s1"
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert result.stage == VISUAL_CONTEXT_STAGE
    assert any("escena=workspace" in line for line in result.prompt_lines)
    assert any("laptop" in line for line in result.prompt_lines)


def test_vm2_visual_context_changes_the_cognitive_request():
    bridge = GovernedVisualCognitiveContextBridge(_context())
    result = CognitiveRuntimeOrchestrator((bridge,)).enrich(
        owner="Carlos",
        session_id="s1",
        text="Analizá el entorno",
        request=_request("Analizá el entorno"),
        now=NOW,
    )
    assert result.request.prompt != "Analizá el entorno"
    assert "[Contexto cognitivo gobernado]" in result.request.prompt
    assert "Evidencia visual gobernada" in result.request.prompt
    assert result.request.metadata["cognitive_stages"] == VISUAL_CONTEXT_STAGE


def test_vm3_text_and_visual_evidence_coexist_without_silent_resolution():
    bridge = GovernedVisualCognitiveContextBridge(_context())
    result = CognitiveRuntimeOrchestrator((bridge,)).enrich(
        owner="Carlos",
        session_id="s1",
        text="El escritorio está vacío",
        request=_request("El escritorio está vacío"),
        now=NOW,
    )
    assert "El escritorio está vacío" in result.request.prompt
    assert "laptop" in result.request.prompt
    assert "no certifica verdad" in result.request.prompt


def test_vm4_owner_mismatch_fails_closed():
    bridge = GovernedVisualCognitiveContextBridge(_context(owner="Cristina"))
    result = bridge.contribute(
        owner="Carlos",
        session_id="s1",
        text="hola",
        request=_request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == ("visual_context:owner_lineage_mismatch",)


def test_vm5_blocked_visual_context_never_enters_cognition():
    bridge = GovernedVisualCognitiveContextBridge(
        _context(status=VisualIntegrationStatus.BLOCKED)
    )
    result = bridge.contribute(
        owner="Carlos",
        session_id="s1",
        text="hola",
        request=_request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert not result.prompt_lines


def test_vm6_review_required_visual_context_is_not_silently_admitted():
    context = _context(status=VisualIntegrationStatus.BLOCKED)
    object.__setattr__(context, "status", VisualIntegrationStatus.REVIEW_REQUIRED)
    bridge = GovernedVisualCognitiveContextBridge(context)
    result = bridge.contribute(
        owner="Carlos",
        session_id="s1",
        text="hola",
        request=_request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED


def test_vm7_missing_visual_context_is_neutral():
    bridge = GovernedVisualCognitiveContextBridge()
    result = bridge.contribute(
        owner="Carlos",
        session_id="s1",
        text="hola",
        request=_request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == ("visual_context:not_supplied",)


def test_vm8_projection_preserves_lineage_and_grants_no_extra_authority():
    context = _context()
    result = GovernedVisualCognitiveContextBridge(context).contribute(
        owner="Carlos",
        session_id="s1",
        text="hola",
        request=_request(),
        now=NOW,
    )
    assert context.integration_id in result.reference_ids
    assert "visual-1" in result.reference_ids
    assert "scene-1" in result.reference_ids
    assert "objects-1" in result.reference_ids
    assert "attention-1" in result.reference_ids
    assert "visual_evidence_remains_non_authoritative" in result.rationale
    assert "no_memory_learning_or_execution_authority" in result.rationale
