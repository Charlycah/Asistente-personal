from app.companion_expression_policy import CompanionExpressionPolicy
from app.ui_adapter import UIResponse
from app.unified_experience_layer import UnifiedExperienceLayer
from app.voice_output import VoiceProsodyFormatter, VoiceResponseReader
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


class Recorder:
    def __init__(self):
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)


def test_expression_policy_keeps_argentine_companion_voice():
    policy = CompanionExpressionPolicy()
    assert policy.apply("Tienes dos opciones. Dime cual quieres.") == (
        "tenes dos opciones. decime cual queres."
    )


def test_expression_policy_hides_module_headings():
    policy = CompanionExpressionPolicy()
    text = "Clima:\nLlueve.\n\nRecordatorios:\nLleva paraguas."
    assert policy.apply(text) == "Llueve.\n\nLleva paraguas."


def test_prosody_formats_units_times_and_lists():
    formatter = VoiceProsodyFormatter()
    spoken = formatter.format("- 14 °C\n- Reunion 09:00\nViento 20 km/h")
    assert "14 grados" in spoken
    assert "9 horas" in spoken
    assert "20 kilómetros por hora" in spoken
    assert "Pausa" not in spoken
    assert spoken == "14 grados. Reunion 9 horas. Viento 20 kilómetros por hora"


def test_unified_experience_and_voice_share_one_expression():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text="Clima:\nTienes 14 °C. Dime si quieres mas.",
            rationale="weather",
        )
    )
    recorder = Recorder()
    VoiceResponseReader(recorder).read(UIResponse(result.response_text, "success"))
    assert result.response_text == "tenes 14 °C. decime si queres mas."
    assert recorder.spoken == ["tenes 14 grados. decime si queres mas."]


def test_expression_policy_preserves_inline_code_exactly():
    policy = CompanionExpressionPolicy()
    text = "Puedes ejecutar `python -c \"print('tienes')\"` y dime el resultado."
    assert policy.apply(text) == (
        "podes ejecutar `python -c \"print('tienes')\"` y decime el resultado."
    )


def test_expression_policy_preserves_fenced_code_exactly():
    policy = CompanionExpressionPolicy()
    text = (
        "Revisa esto:\n```text\nTenes datos. Decime cuales queres.\n```\n"
        "Decime que ves."
    )
    assert policy.apply(text) == (
        "Revisa esto:\n```text\nTenes datos. Decime cuales queres.\n```\n"
        "Decime que ves."
    )


def test_expression_snapshot_counts_each_visible_adjustment():
    policy = CompanionExpressionPolicy()
    policy.apply("Puedes elegir. Dime cual quieres.")
    assert policy.snapshot.personality_adjustments == 3


def test_expression_policy_normalizes_extended_rioplatense_voseo():
    policy = CompanionExpressionPolicy()
    text = (
        "Tú eres quien decide. Puedes venir si quieres. "
        "Dime qué prefieres y cuéntame qué tienes."
    )
    assert policy.apply(text) == (
        "vos sos quien decide. podes venir si queres. "
        "decime qué preferis y contame qué tenes."
    )


def test_expression_policy_normalizes_pronouns_and_imperatives():
    policy = CompanionExpressionPolicy()
    text = (
        "Esto es para ti. Ven conmigo, haz la prueba, pon el resultado "
        "y recuerda decírmelo."
    )
    assert policy.apply(text) == (
        "Esto es para vos. veni conmigo, hace la prueba, pone el resultado "
        "y acordate decírmelo."
    )


def test_expression_policy_does_not_change_technical_literals_with_voseo_rules():
    policy = CompanionExpressionPolicy()
    text = (
        "Puedes usar `haz --help` y revisar:\n```text\nTú eres. Dime qué quieres.\n```"
    )
    assert policy.apply(text) == (
        "podes usar `haz --help` y revisar:\n```text\nTú eres. Dime qué quieres.\n```"
    )


def test_expression_policy_expands_weather_abbreviations():
    policy = CompanionExpressionPolicy()
    text = "Hoy, en Buenos Aires:\n* Temp.: 18°C\n* Sens.: 16°C\n* Hum.: 75%"
    assert policy.apply(text) == (
        "Hoy, en Buenos Aires:\n\n- Temperatura: 18 °C\n\n"
        "- Sensación térmica: 16 °C\n\n- Humedad: 75%"
    )


def test_prosody_expands_weather_abbreviations_before_speaking():
    formatter = VoiceProsodyFormatter()
    spoken = formatter.format("Temp.: 18°C\nSens.: 16°C\nHum.: 75%")
    assert spoken == (
        "Temperatura: 18 grados. Sensación térmica: 16 grados. Humedad: 75 por ciento"
    )
    assert "Temp." not in spoken
    assert "Sens." not in spoken
    assert "Hum." not in spoken


def test_expression_policy_removes_redundant_hola_and_uses_voseo():
    policy = CompanionExpressionPolicy()
    assert policy.apply("Hola! Tú puedes elegir si quieres continuar.") == (
        "vos podes elegir si queres continuar."
    )


def test_expression_policy_preserves_greeting_only_answer():
    policy = CompanionExpressionPolicy()
    assert (
        policy.apply("Hola! ¿En qué puedo ayudarte?")
        == "Hola! ¿En qué te puedo ayudar?"
    )


def test_voice_prosody_expands_medical_abbreviations():
    spoken = VoiceProsodyFormatter().format(
        "El viernes tengo una reunión con Laura a las 15:30."
    )

    assert "reunión con Laura" in spoken
    assert "Dra" not in spoken
    assert "15 y 30" in spoken


def test_exp02b_moderates_redundant_enthusiasm():
    policy = CompanionExpressionPolicy()
    text = (
        "\u00a1Excelente! \u00a1Perfecto! "
        "\u00a1Claro que s\u00ed! Ma\u00f1ana habr\u00e1 18 grados."
    )
    assert policy.apply(text) == (
        "Claro que s\u00ed. Ma\u00f1ana habr\u00e1 18 grados."
    )


def test_exp02b_preserves_single_natural_exclamation():
    policy = CompanionExpressionPolicy()
    assert policy.apply("\u00a1Qu\u00e9 buena noticia!") == (
        "\u00a1Qu\u00e9 buena noticia!"
    )


def test_exp02b_preserves_inline_code_with_exclamations():
    policy = CompanionExpressionPolicy()
    text = (
        "\u00a1Excelente! \u00a1Perfecto! "
        "Ejecut\u00e1 `echo \"\u00a1Perfecto!\"`."
    )
    assert policy.apply(text) == (
        "Perfecto. Ejecut\u00e1 `echo \"\u00a1Perfecto!\"`."
    )


def test_exp02b_preserves_fenced_code_with_exclamations():
    policy = CompanionExpressionPolicy()
    text = (
        "\u00a1Excelente! \u00a1Perfecto! "
        "Revis\u00e1 este ejemplo:\n"
        "```text\n"
        "\u00a1Excelente! \u00a1Perfecto!\n"
        "```"
    )
    assert policy.apply(text) == (
        "Perfecto. Revis\u00e1 este ejemplo:\n"
        "```text\n"
        "\u00a1Excelente! \u00a1Perfecto!\n"
        "```"
    )
