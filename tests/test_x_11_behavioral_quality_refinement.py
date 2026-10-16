from app.behavioral_response_refinement import BehavioralResponseRefinement
from app.unified_experience_layer import UnifiedExperienceLayer
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="household-main",
        text=text,
    )


def test_concise_request_collapses_operational_detail():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text=(
                "Manana llueve. La minima sera de 8 grados. "
                "Tenes dos recordatorios pendientes."
            ),
            rationale="coordinated_response_completed",
        ),
        request=_request("Decime breve como viene manana"),
    )
    assert result is not None
    assert result.response_text == ("Manana llueve. La minima sera de 8 grados.")


def test_refinement_removes_internal_module_label():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text="Runtime weather.household: Ahora hay 14 grados."
        ),
        request=_request("como esta el clima"),
    )
    assert result is not None
    assert result.response_text == "Ahora hay 14 grados."


def test_refinement_removes_redundant_assistant_closing():
    refinement = BehavioralResponseRefinement()
    result = refinement.refine(
        _request("que tengo hoy"),
        GovernedOperationalInterception(
            response_text=("Tenes una reunion a las 10. Decime si necesitas algo mas.")
        ),
    )
    assert result.response_text == "Tenes una reunion a las 10."
    assert refinement.snapshot.redundant_closings_removed == 1


def test_detailed_request_keeps_full_useful_answer():
    layer = UnifiedExperienceLayer()
    original = GovernedOperationalInterception(
        response_text=(
            "Manana llueve. La minima sera de 8 grados. "
            "Tenes dos recordatorios pendientes."
        ),
        rationale="coordinated_response_completed",
    )
    result = layer.present(
        original,
        request=_request("Dame todos los detalles de manana"),
    )
    assert result is original


def test_refinement_removes_stacked_generic_openers_before_useful_content():
    refinement = BehavioralResponseRefinement()
    result = refinement.refine(
        _request("que tengo hoy"),
        GovernedOperationalInterception(
            response_text="Claro. Sí. Por supuesto. Tenés una reunión a las 10."
        ),
    )
    assert result.response_text == "Tenés una reunión a las 10."
    assert refinement.snapshot.stacked_openers_removed == 3


def test_refinement_keeps_a_standalone_acknowledgement():
    refinement = BehavioralResponseRefinement()
    result = refinement.refine(
        _request("entendiste"),
        GovernedOperationalInterception(response_text="Claro."),
    )
    assert result.response_text == "Claro."
    assert refinement.snapshot.stacked_openers_removed == 0


def test_refinement_removes_only_adjacent_repeated_sentences():
    refinement = BehavioralResponseRefinement()
    result = refinement.refine(
        _request("como viene el clima"),
        GovernedOperationalInterception(
            response_text="Mañana llueve. Mañana llueve. Llevá paraguas."
        ),
    )
    assert result.response_text == "Mañana llueve. Llevá paraguas."
    assert refinement.snapshot.repeated_sentences_removed == 1


def test_refinement_preserves_repetition_inside_technical_literals():
    refinement = BehavioralResponseRefinement()
    text = (
        "Claro. Revisá `Sí. Sí.` y este bloque:\n"
        "```text\nMañana llueve. Mañana llueve.\n```"
    )
    result = refinement.refine(
        _request("revisa el ejemplo"),
        GovernedOperationalInterception(response_text=text),
    )
    assert result.response_text == (
        "Revisá `Sí. Sí.` y este bloque:\n```text\nMañana llueve. Mañana llueve.\n```"
    )


def test_refinement_varies_consecutive_repeated_transitions():
    refinement = BehavioralResponseRefinement()
    result = refinement.refine(
        _request("contame todo"),
        GovernedOperationalInterception(
            response_text=(
                "Además, mañana llueve. Además, tenés una reunión. "
                "Además, vence una factura."
            )
        ),
    )
    assert result.response_text == (
        "Además, mañana llueve. También, tenés una reunión. Además, vence una factura."
    )
    assert refinement.snapshot.repeated_transitions_varied == 1


def test_refinement_keeps_distinct_transitions():
    refinement = BehavioralResponseRefinement()
    text = "Además, mañana llueve. También, tenés una reunión."
    result = refinement.refine(
        _request("contame todo"),
        GovernedOperationalInterception(response_text=text),
    )
    assert result.response_text == text
    assert refinement.snapshot.repeated_transitions_varied == 0


def test_refinement_collapses_only_excessive_blank_lines():
    refinement = BehavioralResponseRefinement()
    result = refinement.refine(
        _request("contame todo"),
        GovernedOperationalInterception(
            response_text="Mañana llueve.\n\n\n\nTenés una reunión."
        ),
    )
    assert result.response_text == "Mañana llueve.\n\nTenés una reunión."
    assert refinement.snapshot.excessive_blank_lines_removed == 1


def test_flow_refinement_preserves_code_layout_and_transitions():
    refinement = BehavioralResponseRefinement()
    text = (
        "Revisá esto:\n```text\nAdemás, uno. Además, dos.\n\n\n\nfin\n```\n"
        "Además, afuera uno. Además, afuera dos."
    )
    result = refinement.refine(
        _request("revisa el ejemplo"),
        GovernedOperationalInterception(response_text=text),
    )
    assert result.response_text == (
        "Revisá esto:\n```text\nAdemás, uno. Además, dos.\n\n\n\nfin\n```\n"
        "Además, afuera uno. También, afuera dos."
    )
