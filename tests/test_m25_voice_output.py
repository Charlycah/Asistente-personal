import subprocess

from app.ui_adapter import UIResponse
from app.voice_output import (
    LocalCommandVoiceConfig,
    LocalCommandVoiceOutput,
    NullVoiceOutput,
    SafeVoiceOutput,
    VoiceProfile,
    VoiceResponseReader,
    build_voice_output_from_environment,
)


class RecordingVoiceOutput:
    def __init__(self):
        self.spoken = []

    def speak(self, text: str) -> None:
        self.spoken.append(text)


class FailingVoiceOutput:
    def speak(self, text: str) -> None:
        raise RuntimeError("tts failed")


def test_voice_profile_defines_roby_warm_local_voice_policy():
    profile = VoiceProfile()

    assert profile.name == "Roby warm companion voice"
    assert profile.language == "es-AR"
    assert profile.tone == "warm"
    assert profile.rate == "calm"


def test_null_voice_output_is_safe_noop():
    NullVoiceOutput().speak("hola")


def test_safe_voice_output_keeps_tts_failures_non_critical():
    SafeVoiceOutput(FailingVoiceOutput()).speak("hola")


def test_response_reader_speaks_ui_response_text():
    voice = RecordingVoiceOutput()
    reader = VoiceResponseReader(voice)

    reader.read(UIResponse(text="Hola, soy ROBY.", status="success"))

    assert voice.spoken == ["Hola, soy ROBY."]


def test_response_reader_ignores_blank_response_text():
    voice = RecordingVoiceOutput()
    reader = VoiceResponseReader(voice)

    reader.read(UIResponse(text="   ", status="success"))

    assert voice.spoken == []


def test_local_command_voice_output_invokes_configured_offline_command():
    calls = []

    def fake_runner(command, check, timeout):
        calls.append({"command": command, "check": check, "timeout": timeout})
        return subprocess.CompletedProcess(command, 0)

    output = LocalCommandVoiceOutput(
        LocalCommandVoiceConfig(command=("piper-roby", "--speak"), timeout_seconds=2),
        runner=fake_runner,
    )

    output.speak("Hola")

    assert calls == [
        {
            "command": ["piper-roby", "--speak", "Hola"],
            "check": True,
            "timeout": 2,
        }
    ]


def test_local_command_voice_output_ignores_blank_text():
    calls = []
    output = LocalCommandVoiceOutput(
        LocalCommandVoiceConfig(command=("piper-roby",)),
        runner=lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    output.speak("   ")

    assert calls == []


def test_edge_tts_voice_output_uses_argentine_male_voice():
    from app.voice_output import EdgeTTSVoiceConfig, EdgeTTSVoiceOutput

    calls = []

    def fake_runner(command, check, timeout):
        calls.append((command, check, timeout))
        return subprocess.CompletedProcess(command, 0)

    output = EdgeTTSVoiceOutput(
        EdgeTTSVoiceConfig(
            executable="edge-playback",
            voice="es-AR-TomasNeural",
            rate="-8%",
            pitch="-12Hz",
        ),
        runner=fake_runner,
    )
    output.speak("Hola, soy ROBY.")

    assert calls == [
        (
            [
                "edge-playback",
                "--voice",
                "es-AR-TomasNeural",
                "--rate=-8%",
                "--pitch=-12Hz",
                "--volume=+0%",
                "--text",
                "Hola, soy ROBY.",
            ],
            True,
            90.0,
        )
    ]


def test_edge_tts_environment_builder_degrades_when_command_is_missing(
    monkeypatch,
):
    from app.voice_output import (
        NullVoiceOutput,
        build_voice_output_from_environment,
    )

    monkeypatch.setenv("ROBY_VOICE_ENABLED", "true")
    monkeypatch.setenv("ROBY_VOICE_PROVIDER", "edge-tts")
    monkeypatch.setattr("app.voice_output.shutil.which", lambda command: None)

    assert isinstance(build_voice_output_from_environment(), NullVoiceOutput)


def test_edge_tts_environment_builder_loads_selected_voice(monkeypatch):
    from app.voice_output import (
        EdgeTTSVoiceOutput,
        build_voice_output_from_environment,
    )

    monkeypatch.setenv("ROBY_VOICE_ENABLED", "true")
    monkeypatch.setenv("ROBY_VOICE_PROVIDER", "edge-tts")
    monkeypatch.setenv("ROBY_EDGE_TTS_VOICE", "es-AR-ElenaNeural")
    monkeypatch.setattr(
        "app.voice_output.shutil.which",
        lambda command: "C:/venv/Scripts/edge-playback.exe",
    )

    output = build_voice_output_from_environment()

    assert isinstance(output, EdgeTTSVoiceOutput)
    assert output.config.voice == "es-AR-ElenaNeural"


def test_edge_tts_environment_builder_uses_warm_companion_profile(monkeypatch):
    from app.voice_output import EdgeTTSVoiceOutput, build_voice_output_from_environment

    monkeypatch.setenv("ROBY_VOICE_ENABLED", "true")
    monkeypatch.setenv("ROBY_VOICE_PROVIDER", "edge-tts")
    monkeypatch.setenv("ROBY_VOICE_PROFILE", "warm_companion")
    for name in ("ROBY_EDGE_TTS_VOICE", "ROBY_EDGE_TTS_RATE", "ROBY_EDGE_TTS_PITCH"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(
        "app.voice_output.shutil.which",
        lambda command: "C:/venv/Scripts/edge-playback.exe",
    )

    output = build_voice_output_from_environment()

    assert isinstance(output, EdgeTTSVoiceOutput)
    assert output.config.voice == "es-AR-ElenaNeural"
    assert output.config.rate == "-8%"
    assert output.config.pitch == "-1Hz"


def test_edge_tts_splits_long_forecast_into_complete_chunks():
    from app.voice_output import EdgeTTSVoiceOutput

    text = " ".join(
        f"Día {index}. La temperatura será agradable y el viento moderado."
        for index in range(1, 12)
    )
    chunks = EdgeTTSVoiceOutput._speech_chunks(text, limit=120)

    assert len(chunks) > 1
    assert all(len(chunk) <= 120 for chunk in chunks)
    assert " ".join(chunks) == text


def test_edge_tts_environment_builder_uses_warm_male_profile(monkeypatch):
    monkeypatch.setenv("ROBY_VOICE_ENABLED", "true")
    monkeypatch.setenv("ROBY_VOICE_PROVIDER", "edge-tts")
    monkeypatch.setenv("ROBY_VOICE_PROFILE", "warm_male")
    monkeypatch.delenv("ROBY_EDGE_TTS_VOICE", raising=False)
    monkeypatch.delenv("ROBY_EDGE_TTS_RATE", raising=False)
    monkeypatch.delenv("ROBY_EDGE_TTS_PITCH", raising=False)
    monkeypatch.delenv("ROBY_EDGE_TTS_VOLUME", raising=False)
    monkeypatch.setattr("app.voice_output.shutil.which", lambda _: "edge-playback")
    output = build_voice_output_from_environment()
    assert output.config.voice == "es-AR-TomasNeural"
    assert output.config.rate == "-8%"
    assert output.config.pitch == "-4Hz"
    assert output.config.volume == "+2%"
