from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from core.cognitive_runtime_orchestration import (
    AUDIO_CONTEXT_STAGE,
    VISUAL_CONTEXT_STAGE,
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
    GovernedAudioCognitiveContextBridge,
    GovernedVisualCognitiveContextBridge,
)
from core.intelligent_audio import (
    AudioEventType,
    AudioFrame,
    AudioMode,
    AudioPolicy,
    IntelligentAudioService,
)
from core.llm_provider import LLMRequest
from core.visual_context_integration import (
    IntegratedVisualContext,
    VisualIntegrationAction,
    VisualIntegrationStatus,
)

NOW = datetime(2026, 8, 24, 15, 0, tzinfo=timezone.utc)


def _frame(**changes) -> AudioFrame:
    values = {
        "observed_at": NOW,
        "transcript": "Roby la alarma está sonando",
        "speech_detected": True,
        "voice_confidence": 0.95,
        "duration_seconds": 2.0,
        "microphone_permission": True,
        "explicit_user_consent": True,
    }
    values.update(changes)
    return AudioFrame(**values)


def _ready_event():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.WAKE_WORD))
    event = service.process(_frame())
    assert event.event_type is AudioEventType.UTTERANCE_READY
    return event


def _request(text: str = "Analizá la situación") -> LLMRequest:
    return LLMRequest(prompt=text, system_prompt="Sistema ROBY")


def _visual_context() -> IntegratedVisualContext:
    scene = SimpleNamespace(
        understanding_id="scene-audio-visual",
        dominant_scene=SimpleNamespace(value="workspace"),
        attributes=("indoor",),
    )
    objects = SimpleNamespace(
        profile_id="objects-audio-visual",
        objects=(
            SimpleNamespace(label="luz roja", count=1, confidence=0.94),
        ),
    )
    attention = SimpleNamespace(
        plan_id="attention-audio-visual",
        focus_items=(
            SimpleNamespace(
                object_ref="luz-roja",
                priority=SimpleNamespace(value="high"),
            ),
        ),
    )
    request = SimpleNamespace(
        owner="Carlos",
        visual_context=SimpleNamespace(context_id="visual-audio-visual"),
        resolved_observation=SimpleNamespace(resolution_id="resolution-audio-visual"),
        scene_understanding=scene,
        object_knowledge=objects,
        attention_plan=attention,
        integration_requested=True,
    )
    return IntegratedVisualContext(
        request=request,
        status=VisualIntegrationStatus.READY,
        action=VisualIntegrationAction.INTEGRATE,
        visual_context_id="visual-audio-visual",
        resolution_id="resolution-audio-visual",
        scene_understanding_id="scene-audio-visual",
        object_knowledge_id="objects-audio-visual",
        attention_plan_id="attention-audio-visual",
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
        rationale=("challenge:ready",),
        created_at=NOW,
    )


def test_am1_ready_utterance_becomes_cognitive_contribution():
    event = _ready_event()
    result = GovernedAudioCognitiveContextBridge(event).contribute(
        owner="Carlos",
        session_id="s1",
        text="Analizá",
        request=_request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert result.stage == AUDIO_CONTEXT_STAGE
    assert any("alarma está sonando" in line for line in result.prompt_lines)


def test_am2_audio_changes_the_cognitive_request():
    bridge = GovernedAudioCognitiveContextBridge(_ready_event())
    result = CognitiveRuntimeOrchestrator((bridge,)).enrich(
        owner="Carlos",
        session_id="s1",
        text="Analizá la situación",
        request=_request(),
        now=NOW,
    )
    assert "Evidencia auditiva gobernada" in result.request.prompt
    assert "transcripción_audio=la alarma está sonando" in result.request.prompt
    assert result.request.metadata["cognitive_stages"] == AUDIO_CONTEXT_STAGE


def test_am3_text_and_audio_coexist_without_silent_truth_resolution():
    bridge = GovernedAudioCognitiveContextBridge(_ready_event())
    result = CognitiveRuntimeOrchestrator((bridge,)).enrich(
        owner="Carlos",
        session_id="s1",
        text="No hay ninguna alarma",
        request=_request("No hay ninguna alarma"),
        now=NOW,
    )
    assert "No hay ninguna alarma" in result.request.prompt
    assert "la alarma está sonando" in result.request.prompt
    assert "no certifica verdad" in result.request.prompt


def test_am4_rejected_audio_never_enters_cognition():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.WAKE_WORD))
    event = service.process(_frame(microphone_permission=False))
    result = GovernedAudioCognitiveContextBridge(event).contribute(
        owner="Carlos",
        session_id="s1",
        text="hola",
        request=_request(),
        now=NOW,
    )
    assert event.event_type is AudioEventType.REJECTED
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert not result.prompt_lines


def test_am5_ignored_or_silent_audio_never_enters_cognition():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.WAKE_WORD))
    ignored = service.process(_frame(transcript="Hoy llueve"))
    silent = service.process(_frame(speech_detected=False))
    for event in (ignored, silent):
        result = GovernedAudioCognitiveContextBridge(event).contribute(
            owner="Carlos",
            session_id="s1",
            text="hola",
            request=_request(),
            now=NOW,
        )
        assert result.status is CognitiveRuntimeStageStatus.SKIPPED


def test_am6_missing_audio_context_is_neutral():
    result = GovernedAudioCognitiveContextBridge().contribute(
        owner="Carlos",
        session_id="s1",
        text="hola",
        request=_request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == ("audio_context:not_supplied",)


def test_am7_audio_projection_preserves_event_lineage_and_no_extra_authority():
    event = _ready_event()
    result = GovernedAudioCognitiveContextBridge(event).contribute(
        owner="Carlos",
        session_id="s1",
        text="hola",
        request=_request(),
        now=NOW,
    )
    assert result.reference_ids == (event.event_id,)
    assert "audio_evidence_remains_non_authoritative" in result.rationale
    assert "no_memory_learning_or_execution_authority" in result.rationale


def test_am8_audio_and_visual_share_one_cognitive_orchestrator():
    audio = GovernedAudioCognitiveContextBridge(_ready_event())
    visual = GovernedVisualCognitiveContextBridge(_visual_context())
    result = CognitiveRuntimeOrchestrator((audio, visual)).enrich(
        owner="Carlos",
        session_id="s1",
        text="¿Qué está pasando?",
        request=_request("¿Qué está pasando?"),
        now=NOW,
    )
    assert "Evidencia auditiva gobernada" in result.request.prompt
    assert "Evidencia visual gobernada" in result.request.prompt
    stages = result.request.metadata["cognitive_stages"].split(",")
    assert stages == [AUDIO_CONTEXT_STAGE, VISUAL_CONTEXT_STAGE]
