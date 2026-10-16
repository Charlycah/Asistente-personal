from datetime import datetime, timezone

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
    ConversationalGroundingRuntimeContributor,
    ConversationGroundingState,
)
from core.conversational_repair_intelligence import ConversationalRepairIntelligence
from core.llm_provider import LLMRequest

NOW = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
GUIDANCE_PREFIX = "Grounding epistémico:"


def _contribution(text: str):
    repair = ConversationalRepairIntelligence()
    grounding = ConversationalGroundingIntelligence(repair)
    return ConversationalGroundingRuntimeContributor(grounding).contribute(
        owner="Carlos",
        session_id="main",
        text=text,
        request=LLMRequest(prompt="base"),
        now=NOW,
    )


def _epistemic_lines(text: str) -> tuple[str, ...]:
    contribution = _contribution(text)
    return tuple(
        line for line in contribution.prompt_lines if line.startswith(GUIDANCE_PREFIX)
    )


def _count_prefix(contribution, prefix: str) -> int:
    return sum(line.startswith(prefix) for line in contribution.prompt_lines)


def test_aligned_turn_projects_one_evidence_bounded_grounding_line() -> None:
    lines = _epistemic_lines("La cámara muestra a una persona golpeándola.")
    assert len(lines) == 1
    line = lines[0]
    assert "no presentar como hechos" in line
    assert "inferencia o posibilidad" in line
    assert "preguntar cuando falte información" in line


def test_guidance_is_general_and_not_patch_by_example() -> None:
    line = _epistemic_lines("Juan está en Rosario.")[0].casefold()
    for forbidden in ("marta", "juan", "barrio", "ventana", "tipo peligroso"):
        assert forbidden not in line


def test_confirmed_turn_keeps_state_and_projects_epistemic_guidance() -> None:
    intelligence = ConversationalGroundingIntelligence()
    assessment = intelligence.assess(
        owner="Carlos",
        session_id="main",
        text="Correcto, seguimos.",
        now=NOW,
    )
    contribution = ConversationalGroundingRuntimeContributor(intelligence).contribute(
        owner="Carlos",
        session_id="main",
        text="Correcto, seguimos.",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert assessment.state is ConversationGroundingState.EXPLICITLY_CONFIRMED
    assert _count_prefix(contribution, GUIDANCE_PREFIX) == 1


def test_corrected_scope_keeps_existing_grounding_and_adds_guidance() -> None:
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    grounding = ConversationalGroundingIntelligence(repair)
    adaptive.assess(
        owner="Carlos", session_id="main", text="La caja está en el garaje.", now=NOW
    )
    text = "No, corrección: la caja está en el dormitorio."
    adaptive.assess(owner="Carlos", session_id="main", text=text, now=NOW)
    repair.assess(owner="Carlos", session_id="main", text=text, now=NOW)
    contribution = ConversationalGroundingRuntimeContributor(grounding).contribute(
        owner="Carlos",
        session_id="main",
        text=text,
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert any(
        "adoptar la corrección más reciente" in line
        for line in contribution.prompt_lines
    )
    assert _count_prefix(contribution, GUIDANCE_PREFIX) == 1


def test_clarification_boundary_keeps_missing_details_rule_and_adds_guidance() -> None:
    contribution = _contribution("Ponelo ahí.")
    assert any(
        "No completar detalles ausentes" in line for line in contribution.prompt_lines
    )
    assert _count_prefix(contribution, GUIDANCE_PREFIX) == 1


def test_person_role_grounding_composes_with_epistemic_grounding_once_each() -> None:
    contribution = _contribution("Marta compró un libro y Elena una lámpara.")
    assert _count_prefix(contribution, GUIDANCE_PREFIX) == 1
    assert _count_prefix(contribution, "Grounding referencial:") == 1


def test_productive_projection_does_not_change_canonical_m198_prompt_lines() -> None:
    intelligence = ConversationalGroundingIntelligence()
    assessment = intelligence.assess(
        owner="Carlos",
        session_id="main",
        text="La cámara muestra a una persona golpeándola.",
        now=NOW,
    )
    assert assessment.state is ConversationGroundingState.ALIGNED
    assert all(not line.startswith(GUIDANCE_PREFIX) for line in assessment.prompt_lines)
    contribution = ConversationalGroundingRuntimeContributor(intelligence).contribute(
        owner="Carlos",
        session_id="main",
        text="La cámara muestra a una persona golpeándola.",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert "evidence_bounded_elaboration" in contribution.rationale
