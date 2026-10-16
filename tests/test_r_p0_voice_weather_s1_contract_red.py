"""R-P0-VOICE-WEATHER-S1: RED contractual, no production changes.

Run from the ROBY XI.2 project root with pytest -q on this file.
"""


import pytest

from app.voice_output import (
    EdgeTTSVoiceOutput,
    build_voice_output_from_environment,
)
from app.voice_session_gate import VoiceSessionGate
from app.weather_conversation_runtime import WeatherConversationInterceptionPort


def test_voice_factory_preserves_m25_provider_contract(monkeypatch):
    monkeypatch.setenv("ROBY_VOICE_ENABLED", "true")
    monkeypatch.setenv("ROBY_VOICE_PROVIDER", "edge-tts")
    monkeypatch.setenv("ROBY_EDGE_TTS_EXECUTABLE", "edge-playback")
    monkeypatch.setattr("app.voice_output.shutil.which", lambda _: "edge-playback")

    output = build_voice_output_from_environment()

    assert isinstance(output, EdgeTTSVoiceOutput)


def test_desktop_bootstrap_protects_voice_output():
    import ast
    from pathlib import Path

    source = Path("app/desktop_bootstrap.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    builders = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "build_unified_desktop_app"
    ]
    assert len(builders) == 1

    protected = False
    for node in ast.walk(builders[0]):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "ROBYDesktopApp":
            continue

        for keyword in node.keywords:
            if keyword.arg != "voice_output":
                continue
            value = keyword.value
            protected = (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id == "SafeVoiceOutput"
                and len(value.args) == 1
                and isinstance(value.args[0], ast.Call)
                and isinstance(value.args[0].func, ast.Name)
                and value.args[0].func.id
                == "build_voice_output_from_environment"
            )

    assert protected, "Desktop voice output must use SafeVoiceOutput"


@pytest.mark.parametrize(
    "phrase",
    ["me decís el clima", "cómo viene el clima esta semana"],
)
def test_weather_natural_language_reaches_canonical_intent(phrase):
    assert WeatherConversationInterceptionPort.is_weather_request(phrase)


def test_listening_requires_address_outside_active_window():
    now = [100.0]
    gate = VoiceSessionGate(
        wake_aliases=("roby", "robi"),
        require_wake_word=True,
        clock=lambda: now[0],
    )
    assert not gate.evaluate("qué hora es").accepted
    assert gate.evaluate("Roby, qué hora es").accepted
    now[0] += 31.0
    assert not gate.evaluate("qué hora es").accepted
