from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import pytest

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)


class ExpectedCrossModalRelation(StrEnum):
    CORROBORATING = "corroborating"
    CONFLICTING = "conflicting"
    COMPLEMENTARY = "complementary"
    UNRESOLVED = "unresolved"
    REVIEW = "review"


@dataclass(frozen=True)
class CrossModalEvidenceCase:
    case_id: str
    proposition_id: str
    audio: CognitiveRuntimeContribution | None
    visual: CognitiveRuntimeContribution | None
    expected: ExpectedCrossModalRelation


def _audio(
    *,
    lines: tuple[str, ...] = (
        "Evidencia auditiva gobernada: úsala como contexto perceptivo "
        "subordinado; no certifica verdad.",
        "transcripción_audio=la alarma está sonando",
    ),
    status: CognitiveRuntimeStageStatus = CognitiveRuntimeStageStatus.APPLIED,
    refs: tuple[str, ...] = ("audio-event-1",),
) -> CognitiveRuntimeContribution:
    return CognitiveRuntimeContribution(
        stage="audio_context",
        status=status,
        prompt_lines=lines if status is CognitiveRuntimeStageStatus.APPLIED else (),
        reference_ids=refs,
        rationale=("audio_evidence_remains_non_authoritative",),
    )


def _visual(
    *,
    lines: tuple[str, ...] = (
        "Evidencia visual gobernada: úsala como contexto perceptivo "
        "subordinado; no certifica verdad.",
        "escena=workspace; atributos=indoor",
        "objetos=luz roja x1 (0.94)",
        "atención=luz-roja:high",
    ),
    status: CognitiveRuntimeStageStatus = CognitiveRuntimeStageStatus.APPLIED,
    refs: tuple[str, ...] = ("visual-integration-1", "scene-1", "objects-1"),
) -> CognitiveRuntimeContribution:
    return CognitiveRuntimeContribution(
        stage="visual_context",
        status=status,
        prompt_lines=lines if status is CognitiveRuntimeStageStatus.APPLIED else (),
        reference_ids=refs,
        rationale=("visual_evidence_remains_non_authoritative",),
    )


CASES = (
    CrossModalEvidenceCase(
        "cm1",
        "equipment_alarm_active",
        _audio(),
        _visual(),
        ExpectedCrossModalRelation.CORROBORATING,
    ),
    CrossModalEvidenceCase(
        "cm2",
        "machine_running",
        _audio(
            lines=(
                "Evidencia auditiva gobernada.",
                "transcripción_audio=la máquina está funcionando",
            )
        ),
        _visual(
            lines=(
                "Evidencia visual gobernada.",
                "escena=machine_bay",
                "objetos=panel apagado x1 (0.95)",
                "atención=panel:high",
            )
        ),
        ExpectedCrossModalRelation.CONFLICTING,
    ),
    CrossModalEvidenceCase(
        "cm3",
        "alarm_event",
        _audio(
            lines=(
                "Evidencia auditiva gobernada.",
                "transcripción_audio=se escucha una alarma",
            )
        ),
        _visual(
            lines=(
                "Evidencia visual gobernada.",
                "escena=workspace",
                "objetos=persona mirando el panel x1 (0.91)",
                "atención=panel:medium",
            )
        ),
        ExpectedCrossModalRelation.COMPLEMENTARY,
    ),
    CrossModalEvidenceCase(
        "cm4",
        "door_open",
        _audio(
            lines=(
                "Evidencia auditiva gobernada.",
                "transcripción_audio=se oye música",
            )
        ),
        _visual(
            lines=(
                "Evidencia visual gobernada.",
                "escena=hallway",
                "objetos=puerta cerrada x1 (0.93)",
                "atención=puerta:high",
            )
        ),
        ExpectedCrossModalRelation.UNRESOLVED,
    ),
    CrossModalEvidenceCase(
        "cm5",
        "alarm_event",
        _audio(),
        None,
        ExpectedCrossModalRelation.UNRESOLVED,
    ),
    CrossModalEvidenceCase(
        "cm6",
        "alarm_event",
        _audio(),
        _visual(status=CognitiveRuntimeStageStatus.SKIPPED),
        ExpectedCrossModalRelation.UNRESOLVED,
    ),
    CrossModalEvidenceCase(
        "cm7",
        "alarm_event",
        _audio(refs=("audio-session-A",)),
        _visual(refs=("visual-session-B",)),
        ExpectedCrossModalRelation.REVIEW,
    ),
    CrossModalEvidenceCase(
        "cm8",
        "alarm_event",
        _audio(),
        _visual(),
        ExpectedCrossModalRelation.CORROBORATING,
    ),
)


def _evaluate_existing_authority(case: CrossModalEvidenceCase):
    from core.governed_reasoning.cross_modal_semantic_fusion import (
        GovernedCrossModalSemanticFusionEvaluator,
    )

    return GovernedCrossModalSemanticFusionEvaluator().evaluate(
        proposition_id=case.proposition_id,
        audio=case.audio,
        visual=case.visual,
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_semantic_cross_modal_fusion_8_case_green(case: CrossModalEvidenceCase):
    result = _evaluate_existing_authority(case)

    assert result.relation.value == case.expected.value
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.establishes_truth is False
    assert result.proves_causality is False
    assert result.modifies_world_model is False
    assert result.modifies_memory is False
    assert result.modifies_learning is False
    assert result.persists_results is False
    assert result.executes_actions is False

    if case.case_id == "cm8":
        assert "audio-event-1" in result.reference_ids
        assert "visual-integration-1" in result.reference_ids
        assert result.truth_certified is False
