from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from app.audio_engine import VoskAudioEngine, VoskAudioEngineConfig

logger = logging.getLogger(__name__)


class VoiceInput(Protocol):
    def transcribe(self) -> str: ...


@dataclass(frozen=True)
class VoiceInputProfile:
    name: str = "Roby local speech input"
    language: str = "es"
    mode: str = "offline"


class NullVoiceInput:
    def transcribe(self) -> str:
        return ""


class SafeVoiceInput:
    """Protect voice transcription while preserving engine lifecycle controls."""

    def __init__(self, voice_input: VoiceInput) -> None:
        self.voice_input = voice_input

    def transcribe(self) -> str:
        try:
            return self.voice_input.transcribe()
        except Exception:
            logger.exception("Falló la entrada de voz")
            return ""

    def start(self) -> None:
        start = getattr(self.voice_input, "start", None)
        if callable(start):
            start()

    def stop(self) -> None:
        stop = getattr(self.voice_input, "stop", None)
        if callable(stop):
            stop()

    def set_paused(self, paused: bool) -> None:
        set_paused = getattr(self.voice_input, "set_paused", None)
        if callable(set_paused):
            set_paused(paused)

    def set_event_sink(self, sink) -> None:
        set_event_sink = getattr(self.voice_input, "set_event_sink", None)
        if callable(set_event_sink):
            set_event_sink(sink)

    @property
    def error(self) -> str:
        return str(getattr(self.voice_input, "error", ""))

    def diagnostic_snapshot(self):
        snapshot = getattr(self.voice_input, "diagnostic_snapshot", None)
        return snapshot() if callable(snapshot) else None


@dataclass(frozen=True)
class LocalCommandVoiceInputConfig:
    command: tuple[str, ...]
    timeout_seconds: float = 30.0


class LocalCommandVoiceInput:
    def __init__(
        self,
        config: LocalCommandVoiceInputConfig,
        runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    ) -> None:
        self.config = config
        self.runner = runner

    def transcribe(self) -> str:
        result = self.runner(
            [*self.config.command],
            check=True,
            timeout=self.config.timeout_seconds,
            capture_output=True,
            text=True,
        )
        return str(result.stdout).strip()


class VoiceRequestTranscriber:
    def __init__(self, voice_input: VoiceInput | None = None) -> None:
        self.voice_input = voice_input or NullVoiceInput()

    def transcribe(self) -> str:
        try:
            return self.voice_input.transcribe().strip()
        except Exception:
            return ""


def build_voice_input_from_environment() -> VoiceInput:
    """Build the configured local speech input without uploading microphone audio.

    ``.roby/config.json`` is activated before this function is called.  This
    intentionally follows the same environment-driven path that is known to
    work when the three audio variables are set manually in PowerShell.
    """
    import os

    from app.roby_config import activate_roby_config, resolve_roby_config_path

    # Materialize the canonical JSON settings into the exact process variables
    # used by the audio path that was verified manually on Windows.
    activate_roby_config(resolve_roby_config_path(), override_existing=True)

    enabled = os.getenv(
        "ROBY_CONTINUOUS_LISTENING_ENABLED", ""
    ).strip().casefold() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if not enabled:
        return NullVoiceInput()

    backend = os.getenv("ROBY_AUDIO_BACKEND", "powershell").strip().casefold()
    if backend == "vosk":
        project_root = Path(__file__).resolve().parent.parent
        configured_model = os.getenv("ROBY_VOSK_MODEL_PATH", "").strip()
        model_path = (
            Path(configured_model).expanduser()
            if configured_model
            else project_root / ".roby" / "models" / "vosk-es"
        )
        if not model_path.is_absolute():
            model_path = project_root / model_path

        device_text = os.getenv("ROBY_AUDIO_INPUT_DEVICE", "").strip()
        device: int | str | None
        if not device_text:
            device = None
        else:
            try:
                device = int(device_text)
            except ValueError:
                device = device_text

        return VoskAudioEngine(
            VoskAudioEngineConfig(
                model_path=model_path,
                sample_rate=int(os.getenv("ROBY_AUDIO_SAMPLE_RATE", "16000")),
                block_size=int(os.getenv("ROBY_AUDIO_BLOCK_SIZE", "3200")),
                device=device,
                silence_threshold=int(
                    os.getenv("ROBY_AUDIO_SILENCE_THRESHOLD", "180")
                ),
                voice_threshold=int(os.getenv("ROBY_AUDIO_VOICE_THRESHOLD", "380")),
                auto_calibrate=os.getenv(
                    "ROBY_AUDIO_AUTO_CALIBRATE", "true"
                ).strip().casefold() in {"1", "true", "yes", "on"},
                calibration_seconds=float(
                    os.getenv("ROBY_AUDIO_CALIBRATION_SECONDS", "1.5")
                ),
                noise_multiplier=float(
                    os.getenv("ROBY_AUDIO_NOISE_MULTIPLIER", "2.2")
                ),
                normalize_audio=os.getenv(
                    "ROBY_AUDIO_NORMALIZE", "true"
                ).strip().casefold() in {"1", "true", "yes", "on"},
                target_peak=int(os.getenv("ROBY_AUDIO_TARGET_PEAK", "14000")),
                max_gain=float(os.getenv("ROBY_AUDIO_MAX_GAIN", "4.0")),
                partial_results=os.getenv(
                    "ROBY_AUDIO_PARTIAL_RESULTS", "true"
                ).strip().casefold() in {"1", "true", "yes", "on"},
                partial_finalize_ms=int(
                    os.getenv("ROBY_AUDIO_PARTIAL_FINALIZE_MS", "1200")
                ),
                vad_enabled=os.getenv(
                    "ROBY_AUDIO_VAD_ENABLED", "true"
                ).strip().casefold() in {"1", "true", "yes", "on"},
                vad_aggressiveness=int(
                    os.getenv("ROBY_AUDIO_VAD_AGGRESSIVENESS", "2")
                ),
                pre_roll_ms=int(os.getenv("ROBY_AUDIO_PRE_ROLL_MS", "300")),
                end_silence_ms=int(
                    os.getenv("ROBY_AUDIO_END_SILENCE_MS", "650")
                ),
                min_speech_ms=int(os.getenv("ROBY_AUDIO_MIN_SPEECH_MS", "250")),
                max_utterance_seconds=float(
                    os.getenv("ROBY_AUDIO_MAX_UTTERANCE_SECONDS", "12")
                ),
                recalibration_silence_seconds=float(
                    os.getenv("ROBY_AUDIO_RECALIBRATION_SILENCE_SECONDS", "5")
                ),
                zcr_min=float(os.getenv("ROBY_AUDIO_ZCR_MIN", "0.005")),
                zcr_max=float(os.getenv("ROBY_AUDIO_ZCR_MAX", "0.35")),
                diagnostic_mode=os.getenv(
                    "ROBY_AUDIO_DIAGNOSTIC_MODE", "false"
                ).strip().casefold() in {"1", "true", "yes", "on"},
            )
        )

    script = Path(__file__).resolve().parent.parent / "scripts" / "roby_listen_once.ps1"
    if not script.exists():
        return NullVoiceInput()
    language = os.getenv("ROBY_SPEECH_LANGUAGE", "es-AR").strip() or "es-AR"
    timeout = os.getenv("ROBY_LISTEN_UTTERANCE_TIMEOUT_SECONDS", "8").strip() or "8"
    return SafeVoiceInput(
        LocalCommandVoiceInput(
            LocalCommandVoiceInputConfig(
                command=(
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-Language",
                    language,
                    "-TimeoutSeconds",
                    timeout,
                ),
                timeout_seconds=max(float(timeout) + 5.0, 12.0),
            )
        )
    )
