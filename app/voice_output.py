from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable, Protocol

from app.ui_adapter import UIResponse
from core.adaptive_personality import (
    AdaptiveDeliveryTone,
    AdaptiveResponseDetail,
    AdaptiveResponseStructure,
)


class VoiceOutput(Protocol):
    def speak(self, text: str) -> None: ...


@dataclass(frozen=True)
class VoiceProfile:
    name: str = "Roby warm companion voice"
    language: str = "es-AR"
    tone: str = "warm"
    rate: str = "calm"


VOICE_PRESETS: dict[str, "EdgeTTSVoiceConfig"] = {}


class NullVoiceOutput:
    def speak(self, text: str) -> None:
        return None


class SafeVoiceOutput:
    def __init__(self, voice_output: VoiceOutput) -> None:
        self.voice_output = voice_output

    def speak(self, text: str) -> None:
        try:
            self.voice_output.speak(text)
        except Exception:
            return None


@dataclass(frozen=True)
class LocalCommandVoiceConfig:
    command: tuple[str, ...]
    timeout_seconds: float = 30.0


class LocalCommandVoiceOutput:
    def __init__(
        self,
        config: LocalCommandVoiceConfig,
        runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    ) -> None:
        self.config = config
        self.runner = runner

    def speak(self, text: str) -> None:
        normalized_text = text.strip()
        if not normalized_text:
            return None

        self.runner(
            [*self.config.command, normalized_text],
            check=True,
            timeout=self.config.timeout_seconds,
        )
        return None


@dataclass(frozen=True)
class EdgeTTSVoiceConfig:
    voice: str = "es-AR-TomasNeural"
    rate: str = "-8%"
    pitch: str = "-12Hz"
    volume: str = "+0%"
    timeout_seconds: float = 90.0
    executable: str = "edge-playback"


VOICE_PRESETS.update(
    {
        "warm_companion": EdgeTTSVoiceConfig(
            voice="es-AR-ElenaNeural",
            rate="-8%",
            pitch="-1Hz",
            volume="+2%",
        ),
        "warm_male": EdgeTTSVoiceConfig(
            voice="es-AR-TomasNeural",
            rate="-8%",
            pitch="-4Hz",
            volume="+2%",
        ),
        "casual_female": EdgeTTSVoiceConfig(
            voice="es-AR-ElenaNeural",
            rate="+3%",
            pitch="+2Hz",
            volume="+1%",
        ),
        "classic_roby": EdgeTTSVoiceConfig(
            voice="es-AR-TomasNeural",
            rate="-8%",
            pitch="-12Hz",
            volume="+0%",
        ),
        "clear_neutral": EdgeTTSVoiceConfig(
            voice="es-AR-ElenaNeural",
            rate="-4%",
            pitch="+0Hz",
            volume="+0%",
        ),
        "night": EdgeTTSVoiceConfig(
            voice="es-AR-ElenaNeural",
            rate="-18%",
            pitch="-4Hz",
            volume="-5%",
        ),
    }
)


class EdgeTTSVoiceOutput:
    """Speak through Microsoft Edge online TTS using edge-playback."""

    def __init__(
        self,
        config: EdgeTTSVoiceConfig | None = None,
        runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    ) -> None:
        self.config = config or EdgeTTSVoiceConfig()
        self.runner = runner

    def speak(self, text: str) -> None:
        normalized_text = text.strip()
        if not normalized_text:
            return None
        for chunk in self._speech_chunks(normalized_text):
            self.runner(
                [
                    self.config.executable,
                    "--voice",
                    self.config.voice,
                    f"--rate={self.config.rate}",
                    f"--pitch={self.config.pitch}",
                    f"--volume={self.config.volume}",
                    "--text",
                    chunk,
                ],
                check=True,
                timeout=self.config.timeout_seconds,
            )
        return None

    @staticmethod
    def _speech_chunks(text: str, *, limit: int = 360) -> tuple[str, ...]:
        normalized = text.strip()
        if not normalized:
            return ()

        # A weather summary should be spoken in one playback process. Starting
        # edge-playback once per short sentence produces artificial silences.
        # Long forecasts remain separated by day/paragraph for intelligibility.
        paragraphs = tuple(
            block.strip() for block in re.split(r"\n\s*\n", normalized) if block.strip()
        )
        if len(paragraphs) > 1:
            chunks: list[str] = []
            for paragraph in paragraphs:
                chunks.extend(
                    EdgeTTSVoiceOutput._split_long_text(paragraph, limit=limit)
                )
            return tuple(chunks)
        return EdgeTTSVoiceOutput._split_long_text(normalized, limit=limit)

    @staticmethod
    def _split_long_text(text: str, *, limit: int) -> tuple[str, ...]:
        if len(text) <= limit:
            return (text,)
        sentences = tuple(
            part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()
        )
        chunks: list[str] = []
        current = ""
        for sentence in sentences:
            candidate = f"{current} {sentence}".strip()
            if current and len(candidate) > limit:
                chunks.append(current)
                current = sentence
            else:
                current = candidate
        if current:
            chunks.append(current)
        return tuple(chunks) or (text,)


def build_voice_output_from_environment() -> VoiceOutput:
    enabled = os.getenv("ROBY_VOICE_ENABLED", "true").strip().casefold() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if not enabled:
        return NullVoiceOutput()

    provider = os.getenv("ROBY_VOICE_PROVIDER", "edge-tts").strip().casefold()
    if provider not in {"edge", "edge-tts", "edge_tts"}:
        return NullVoiceOutput()

    executable = os.getenv("ROBY_EDGE_TTS_EXECUTABLE", "edge-playback").strip()
    if not executable or shutil.which(executable) is None:
        return NullVoiceOutput()

    profile_name = os.getenv("ROBY_VOICE_PROFILE", "casual_female").strip().casefold()
    preset = VOICE_PRESETS.get(profile_name, VOICE_PRESETS["casual_female"])
    output = EdgeTTSVoiceOutput(
        EdgeTTSVoiceConfig(
            executable=executable,
            voice=os.getenv("ROBY_EDGE_TTS_VOICE", preset.voice).strip(),
            rate=os.getenv("ROBY_EDGE_TTS_RATE", preset.rate).strip(),
            pitch=os.getenv("ROBY_EDGE_TTS_PITCH", preset.pitch).strip(),
            volume=os.getenv("ROBY_EDGE_TTS_VOLUME", preset.volume).strip(),
            timeout_seconds=float(os.getenv("ROBY_EDGE_TTS_TIMEOUT_SECONDS", "90")),
        )
    )
    return output


class VoiceResponseReader:
    def __init__(
        self,
        voice_output: VoiceOutput | None = None,
        prosody_formatter: VoiceProsodyFormatter | None = None,
    ) -> None:
        self.voice_output = voice_output or NullVoiceOutput()
        self.prosody_formatter = prosody_formatter or VoiceProsodyFormatter()

    def read(
        self,
        response: UIResponse,
        delivery_tone: AdaptiveDeliveryTone | None = None,
        response_detail: AdaptiveResponseDetail | None = None,
        response_structure: AdaptiveResponseStructure | None = None,
    ) -> None:
        format_kwargs: dict[str, object] = {"delivery_tone": delivery_tone}
        if response_detail is not None:
            format_kwargs["response_detail"] = response_detail
        if response_structure is not None:
            format_kwargs["response_structure"] = response_structure
        spoken = self.prosody_formatter.format(response.text, **format_kwargs)
        if not spoken:
            return
        try:
            self.voice_output.speak(spoken)
        except Exception:
            return


class VoiceProsodyFormatter:
    """Prepare visible text for calm, intelligible spoken delivery."""

    def format(
        self,
        text: str,
        delivery_tone: AdaptiveDeliveryTone | None = None,
        response_detail: AdaptiveResponseDetail | None = None,
        response_structure: AdaptiveResponseStructure | None = None,
    ) -> str:
        spoken = text.strip()
        if not spoken:
            return ""
        spoken = re.sub(r"(?im)^\s*temp\.?\s*:\s*", "Temperatura: ", spoken)
        spoken = re.sub(r"(?im)^\s*sens\.?\s*:\s*", "Sensación térmica: ", spoken)
        spoken = re.sub(r"(?im)^\s*hum\.?\s*:\s*", "Humedad: ", spoken)
        spoken = re.sub(r"(?i)\bdra\.?(?=\s|$)", "doctora", spoken)
        spoken = re.sub(r"(?i)\bdr\.?(?=\s|$)", "doctor", spoken)
        # Weather metrics should flow as one natural thought instead of sounding
        # like isolated form fields with a long pause after every line.
        spoken = re.sub(r"(?i)(humedad[^\n]*?)\.\s*\n+(el viento)", r"\1, \2", spoken)
        spoken = re.sub(r"(?i)(viento[^\n]*?)\.\s*\n+(la presión)", r"\1, y \2", spoken)
        spoken = re.sub(
            r"(?i)(temperatura[^\n]*?)\.\s*\n+(se siente)", r"\1; \2", spoken
        )
        spoken = spoken.replace("°C", " grados")
        spoken = spoken.replace("%", " por ciento")
        spoken = spoken.replace("km/h", " kilómetros por hora")
        spoken = spoken.replace("hPa", " hectopascales")
        spoken = spoken.replace("km", " kilometros")
        spoken = re.sub(r"\b(\d{1,2}):(\d{2})\b", self._time, spoken)
        # Lists and visual spacing must sound like natural sentence boundaries.
        # Never pronounce implementation markers such as "Pausa".
        spoken = re.sub(r"^[-*]\s+", "", spoken, flags=re.MULTILINE)
        spoken = re.sub(r"(?<![.!?])\n+", ". ", spoken)
        spoken = re.sub(r"\n+", " ", spoken)
        spoken = re.sub(r"\s+", " ", spoken)
        spoken = re.sub(r"\.{2,}", ".", spoken)
        spoken = self._project_delivery_tone(spoken, delivery_tone)
        spoken = self._project_response_structure(spoken, response_structure)
        spoken = self._project_response_detail(spoken, response_detail)
        return spoken.strip()

    @staticmethod
    def _project_response_structure(
        spoken: str,
        response_structure: AdaptiveResponseStructure | None,
    ) -> str:
        if response_structure in {None, AdaptiveResponseStructure.PLAIN}:
            return spoken
        if response_structure is AdaptiveResponseStructure.BULLETED:
            return spoken.replace("; ", ". ")
        if response_structure is AdaptiveResponseStructure.STEPWISE:
            return spoken.replace("; ", ".  ")
        return spoken

    @staticmethod
    def _project_response_detail(
        spoken: str,
        response_detail: AdaptiveResponseDetail | None,
    ) -> str:
        if response_detail in {None, AdaptiveResponseDetail.BALANCED}:
            return spoken
        if response_detail is AdaptiveResponseDetail.BRIEF:
            return spoken.replace("; ", ". ")
        if response_detail is AdaptiveResponseDetail.DETAILED:
            return spoken.replace(". ", ".  ")
        return spoken

    @staticmethod
    def _project_delivery_tone(
        spoken: str,
        delivery_tone: AdaptiveDeliveryTone | None,
    ) -> str:
        if delivery_tone in {None, AdaptiveDeliveryTone.NEUTRAL}:
            return spoken
        if delivery_tone is AdaptiveDeliveryTone.WARM:
            return spoken.replace(". ", ", ")
        if delivery_tone is AdaptiveDeliveryTone.CAREFUL:
            return spoken.replace(". ", "; ")
        if delivery_tone is AdaptiveDeliveryTone.REPAIRING:
            return spoken.replace(". ", ": ")
        if delivery_tone is AdaptiveDeliveryTone.DIRECT:
            return spoken.replace(". ", "! ")
        return spoken

    @staticmethod
    def _time(match: re.Match[str]) -> str:
        hour = int(match.group(1))
        minute = int(match.group(2))
        if minute == 0:
            return f"{hour} horas"
        return f"{hour} y {minute}"
