from app.unified_experience_layer import UnifiedExperienceLayer
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_experience_removes_generic_chatbot_opening():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text=(
                "Me alegra que me preguntes. Ahora en Buenos Aires hay 14 grados."
            )
        )
    )
    assert result is not None
    assert result.response_text == "Ahora en Buenos Aires hay 14 grados."


def test_experience_softens_internal_failure_wording():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text="Capability unavailable: camera.capture"
        )
    )
    assert result is not None
    assert result.response_text == "Esa funcion no esta disponible ahora."


def test_experience_deduplicates_identical_sections():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text="Hoy no llueve.\n\nHoy no llueve."
        )
    )
    assert result is not None
    assert result.response_text == "Hoy no llueve."
    assert layer.snapshot.removed_repetitions == 1


def test_experience_preserves_rationale_and_clean_text():
    layer = UnifiedExperienceLayer()
    original = GovernedOperationalInterception(
        response_text="Tenes dos recordatorios.",
        rationale="resident_reminders_completed",
    )
    result = layer.present(original)
    assert result is original
    assert result.rationale == "resident_reminders_completed"
