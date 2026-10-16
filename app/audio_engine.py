from __future__ import annotations

import math
import queue
import threading
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

import numpy as np

from app.speech_backend import (
    SpeechRecognitionBackend,
    VoskSpeechRecognitionBackend,
)


class AudioEngineState(str, Enum):
    INACTIVE = "inactive"
    STARTING = "starting"
    SILENCE = "silence"
    VOICE = "voice"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass(frozen=True)
class AudioEngineEvent:
    state: AudioEngineState
    level: int = 0
    device_name: str = ""
    text: str = ""
    detail: str = ""


AudioEventSink = Callable[[AudioEngineEvent], None]


@dataclass(frozen=True)
class AudioDiagnosticSnapshot:
    worker_alive: bool
    stream_open: bool
    callback_frames: int
    queued_audio_frames: int
    queued_texts: int
    device_name: str
    error: str
    state: AudioEngineState
    level: int
    silence_threshold: int
    voice_threshold: int


@dataclass(frozen=True)
class VoskAudioEngineConfig:
    model_path: Path
    sample_rate: int = 16000
    block_size: int = 3200
    device: int | str | None = None
    silence_threshold: int = 180
    voice_threshold: int = 380
    auto_calibrate: bool = True
    calibration_seconds: float = 1.5
    noise_multiplier: float = 2.2
    normalize_audio: bool = True
    target_peak: int = 14000
    max_gain: float = 4.0
    partial_results: bool = True
    partial_finalize_ms: int = 1200
    vad_enabled: bool = True
    vad_aggressiveness: int = 2
    pre_roll_ms: int = 300
    end_silence_ms: int = 650
    min_speech_ms: int = 250
    max_utterance_seconds: float = 12.0
    recalibration_silence_seconds: float = 5.0
    zcr_min: float = 0.005
    zcr_max: float = 0.35
    diagnostic_mode: bool = False


@dataclass(frozen=True)
class _AudioFrame:
    data: bytes
    rms: int
    speech_hint: bool


class VoskAudioEngine:
    """Persistent local microphone stream with segmented offline transcription."""

    def __init__(
        self,
        config: VoskAudioEngineConfig,
        backend: SpeechRecognitionBackend | None = None,
    ) -> None:
        self.config = config
        self.backend = backend or VoskSpeechRecognitionBackend(config.model_path)
        self._audio_queue: queue.Queue[_AudioFrame] = queue.Queue(maxsize=64)
        self._text_queue: queue.Queue[str] = queue.Queue()
        self._stop = threading.Event()
        self._paused = threading.Event()
        self._started = threading.Event()
        self._worker: threading.Thread | None = None
        self._stream = None
        self._sink: AudioEventSink | None = None
        self._last_state: AudioEngineState | None = None
        self._last_level = -1
        self._device_name = ""
        self._error = ""
        self._callback_frames = 0
        self._noise_samples: list[int] = []
        self._calibration_blocks = max(
            1,
            round(
                self.config.calibration_seconds
                * self.config.sample_rate
                / max(self.config.block_size, 1)
            ),
        )
        self._adaptive_silence_threshold = self.config.silence_threshold
        self._adaptive_voice_threshold = self.config.voice_threshold
        self._silence_blocks_for_recalibration = max(
            1,
            round(
                self.config.recalibration_silence_seconds
                * self.config.sample_rate
                / max(self.config.block_size, 1)
            ),
        )
        self._recent_silence: deque[int] = deque(
            maxlen=self._silence_blocks_for_recalibration
        )
        self._webrtc_vad = self._build_webrtc_vad()

    @property
    def available(self) -> bool:
        return self.backend.available

    @property
    def error(self) -> str:
        return self._error

    def set_event_sink(self, sink: AudioEventSink | None) -> None:
        self._sink = sink

    def diagnostic_snapshot(self) -> AudioDiagnosticSnapshot:
        worker = self._worker
        return AudioDiagnosticSnapshot(
            worker_alive=bool(worker is not None and worker.is_alive()),
            stream_open=self._stream is not None,
            callback_frames=self._callback_frames,
            queued_audio_frames=self._audio_queue.qsize(),
            queued_texts=self._text_queue.qsize(),
            device_name=self._device_name,
            error=self._error,
            state=self._last_state or AudioEngineState.INACTIVE,
            level=max(0, self._last_level),
            silence_threshold=self._adaptive_silence_threshold,
            voice_threshold=self._adaptive_voice_threshold,
        )

    def start(self) -> None:
        if self._worker is not None and self._worker.is_alive():
            return
        self._stop.clear()
        self._started.clear()
        self._worker = threading.Thread(
            target=self._run,
            name="roby-audio-engine",
            daemon=True,
        )
        self._worker.start()
        self._started.wait(timeout=3.0)

    def stop(self) -> None:
        self._stop.set()
        stream = self._stream
        if stream is not None:
            try:
                stream.abort()
            except Exception:
                pass
        worker = self._worker
        if worker is not None and worker.is_alive():
            worker.join(timeout=2.0)
        self._emit(AudioEngineState.STOPPED, detail="Motor de audio detenido")

    def set_paused(self, paused: bool) -> None:
        if paused:
            self._paused.set()
            self._clear_queue(self._audio_queue)
            self._clear_queue(self._text_queue)
        else:
            self._clear_queue(self._audio_queue)
            self._clear_queue(self._text_queue)
            self._paused.clear()

    @staticmethod
    def _clear_queue(target: queue.Queue) -> None:
        while True:
            try:
                target.get_nowait()
            except queue.Empty:
                return

    def transcribe(self) -> str:
        self.start()
        while not self._stop.is_set():
            try:
                return self._text_queue.get(timeout=0.25)
            except queue.Empty:
                if self._error:
                    return ""
        return ""

    def _callback(self, indata, _frames, _time_info, status) -> None:
        self._callback_frames += 1
        if status:
            self._emit(
                AudioEngineState.ERROR,
                detail=f"Advertencia del dispositivo de audio: {status}",
            )
        if self._paused.is_set():
            return
        data = bytes(indata)
        rms = self._rms_from_pcm16(data)
        self._observe_noise_floor(rms)
        speech_hint = self._is_probable_speech(data, rms)
        frame = _AudioFrame(data=data, rms=rms, speech_hint=speech_hint)
        try:
            self._audio_queue.put_nowait(frame)
        except queue.Full:
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._audio_queue.put_nowait(frame)
            except queue.Full:
                pass
        level = self._level_from_rms(rms)
        state = AudioEngineState.VOICE if speech_hint else AudioEngineState.SILENCE
        detail = ""
        if self.config.diagnostic_mode:
            verdict = "voz" if speech_hint else "silencio"
            detail = (
                f"DIAG · RMS {rms} · voz ≥ "
                f"{self._adaptive_voice_threshold} · VAD {verdict}"
            )
        self._emit(state, level=level, detail=detail)

    def _run(self) -> None:
        self._emit(AudioEngineState.STARTING, detail="Inicializando micrófono…")
        try:
            import sounddevice as sd

            if not self.backend.available:
                raise FileNotFoundError(
                    f"Backend de voz no disponible: {self.backend.name}"
                )
            device_info = sd.query_devices(self.config.device, "input")
            self._device_name = str(device_info.get("name", "Micrófono"))
            def new_recognizer():
                return self.backend.create_session(self.config.sample_rate)

            recognizer = new_recognizer()
            block_ms = self.config.block_size * 1000 / self.config.sample_rate
            pre_roll_blocks = max(1, math.ceil(self.config.pre_roll_ms / block_ms))
            end_silence_blocks = max(
                1, math.ceil(self.config.end_silence_ms / block_ms)
            )
            partial_finalize_blocks = max(
                1, math.ceil(self.config.partial_finalize_ms / block_ms)
            )
            min_speech_blocks = max(1, math.ceil(self.config.min_speech_ms / block_ms))
            max_utterance_blocks = max(
                min_speech_blocks,
                math.ceil(self.config.max_utterance_seconds * 1000 / block_ms),
            )
            pre_roll: deque[bytes] = deque(maxlen=pre_roll_blocks)
            speaking = False
            utterance_blocks = 0
            speech_blocks = 0
            trailing_silence = 0
            last_partial_text = ""
            stable_partial_blocks = 0

            with sd.RawInputStream(
                samplerate=self.config.sample_rate,
                blocksize=self.config.block_size,
                device=self.config.device,
                dtype="int16",
                channels=1,
                callback=self._callback,
            ) as stream:
                self._stream = stream
                self._started.set()
                vad_name = (
                    "WebRTC VAD"
                    if self._webrtc_vad is not None
                    else "VAD adaptativo"
                )
                self._emit(
                    AudioEngineState.SILENCE,
                    level=0,
                    detail=f"Micrófono abierto · {vad_name}",
                )
                while not self._stop.is_set():
                    if self._paused.is_set():
                        speaking = False
                        utterance_blocks = 0
                        speech_blocks = 0
                        trailing_silence = 0
                        last_partial_text = ""
                        stable_partial_blocks = 0
                        pre_roll.clear()
                        recognizer = new_recognizer()
                        self._clear_queue(self._audio_queue)
                        self._stop.wait(0.05)
                        continue
                    try:
                        frame = self._audio_queue.get(timeout=0.25)
                    except queue.Empty:
                        continue

                    if not speaking:
                        if not frame.speech_hint:
                            pre_roll.append(frame.data)
                            self._observe_long_silence(frame.rms)
                            continue
                        speaking = True
                        utterance_blocks = 0
                        speech_blocks = 0
                        trailing_silence = 0
                        last_partial_text = ""
                        stable_partial_blocks = 0
                        recognizer = new_recognizer()
                        for buffered in pre_roll:
                            recognizer.accept_audio(self._prepare_pcm16(buffered))
                        pre_roll.clear()

                    utterance_blocks += 1
                    if frame.speech_hint:
                        speech_blocks += 1

                    # Starting speech needs the stricter VAD decision. Ending an
                    # utterance must not depend on that same decision because room
                    # noise can keep WebRTC VAD positive indefinitely. Once speech
                    # has started, use the measured level to count trailing silence.
                    if self._is_trailing_silence(frame):
                        trailing_silence += 1
                    else:
                        trailing_silence = 0
                    recognizer.accept_audio(self._prepare_pcm16(frame.data))

                    if self.config.partial_results:
                        partial_text = recognizer.partial_text().strip()
                        if partial_text:
                            if partial_text == last_partial_text:
                                stable_partial_blocks += 1
                            else:
                                last_partial_text = partial_text
                                stable_partial_blocks = 0
                            self._emit(
                                AudioEngineState.VOICE,
                                level=max(self._last_level, 4),
                                text=partial_text,
                                detail=f"Entendiendo: {partial_text}",
                            )
                        else:
                            stable_partial_blocks = 0

                    should_finish = (
                        trailing_silence >= end_silence_blocks
                        or self._stable_partial_should_finalize(
                            last_partial_text,
                            stable_partial_blocks,
                            partial_finalize_blocks,
                        )
                        or utterance_blocks >= max_utterance_blocks
                    )
                    if not should_finish:
                        continue

                    final_text = recognizer.final_text()
                    text = self._select_recognized_text(final_text, last_partial_text)
                    # A short command such as "hola Roby" may occupy only one
                    # 200 ms block according to VAD. If Vosk produced real text,
                    # accepting it is safer than discarding it solely because the
                    # coarse block counter did not reach min_speech_ms.
                    if text and speech_blocks >= 1:
                        self._text_queue.put(text)
                        self._emit(
                            AudioEngineState.VOICE,
                            level=max(self._last_level, 6),
                            text=text,
                            detail="Frase reconocida",
                        )
                    elif self.config.diagnostic_mode:
                        self._emit(
                            AudioEngineState.SILENCE,
                            level=0,
                            detail=(
                                f"DIAG · {self.backend.name} sin texto final · "
                                f"bloques de voz {speech_blocks}/"
                                f"{min_speech_blocks} · parcial "
                                f"{last_partial_text or '-'}"
                            ),
                        )
                    speaking = False
                    utterance_blocks = 0
                    speech_blocks = 0
                    trailing_silence = 0
                    last_partial_text = ""
                    stable_partial_blocks = 0
                    recognizer = new_recognizer()
        except Exception as exc:
            self._error = str(exc)
            self._started.set()
            self._emit(AudioEngineState.ERROR, detail=self._error)
        finally:
            self._stream = None


    def _is_trailing_silence(self, frame: _AudioFrame) -> bool:
        """Close speech when either VAD or measured level reports silence.

        Some Windows microphone drivers keep the RMS above the adaptive threshold
        because of gain or room noise. In that situation Vosk can produce useful
        partial text forever, but the utterance never reaches the conversation
        queue. Once an utterance has started, a negative VAD decision is enough
        to count a trailing-silence block; a low RMS remains the fallback for
        environments where WebRTC VAD is unavailable.
        """
        return (
            not frame.speech_hint
            or frame.rms < self._adaptive_voice_threshold
        )

    @staticmethod
    def _stable_partial_should_finalize(
        partial_text: str,
        stable_blocks: int,
        required_blocks: int,
    ) -> bool:
        """Finalize a useful partial that stopped changing.

        This is a fallback for microphones whose gain or ambient noise prevents
        both WebRTC VAD and the RMS threshold from reporting clean silence.
        """
        return bool(partial_text.strip()) and stable_blocks >= required_blocks

    @staticmethod
    def _select_recognized_text(final_text: str, partial_text: str) -> str:
        """Prefer the final Vosk result and retain a stable partial as fallback."""
        final = final_text.strip().lower()
        if final:
            return final
        return partial_text.strip().lower()

    @staticmethod
    def _rms_from_pcm16(data: bytes) -> int:
        if not data:
            return 0
        usable_size = len(data) - (len(data) % 2)
        if usable_size <= 0:
            return 0
        samples = np.frombuffer(data[:usable_size], dtype="<i2")
        if samples.size == 0:
            return 0
        float_samples = samples.astype(np.float64, copy=False)
        return int(np.sqrt(np.mean(np.square(float_samples))))

    @staticmethod
    def _zero_crossing_rate(data: bytes) -> float:
        usable_size = len(data) - (len(data) % 2)
        if usable_size <= 2:
            return 0.0
        samples = np.frombuffer(data[:usable_size], dtype="<i2")
        if samples.size <= 1:
            return 0.0
        signs = np.signbit(samples)
        return float(np.count_nonzero(signs[1:] != signs[:-1]) / (samples.size - 1))

    def _build_webrtc_vad(self):
        if not self.config.vad_enabled:
            return None
        try:
            import webrtcvad

            aggressiveness = max(0, min(3, int(self.config.vad_aggressiveness)))
            return webrtcvad.Vad(aggressiveness)
        except ImportError:
            return None

    def _webrtc_speech_ratio(self, data: bytes) -> float | None:
        valid_rates = {8000, 16000, 32000, 48000}
        if self._webrtc_vad is None or self.config.sample_rate not in valid_rates:
            return None
        frame_samples = self.config.sample_rate // 50  # 20 ms
        frame_bytes = frame_samples * 2
        if frame_bytes <= 0 or len(data) < frame_bytes:
            return None
        decisions = []
        for offset in range(0, len(data) - frame_bytes + 1, frame_bytes):
            chunk = data[offset : offset + frame_bytes]
            decisions.append(self._webrtc_vad.is_speech(chunk, self.config.sample_rate))
        if not decisions:
            return None
        return sum(decisions) / len(decisions)

    def _is_probable_speech(self, data: bytes, rms: int) -> bool:
        if rms < self._adaptive_silence_threshold:
            return False
        ratio = self._webrtc_speech_ratio(data)
        if ratio is not None:
            # A full audio block can contain speech plus trailing silence. Requiring
            # 30% of all 20 ms slices to be positive caused real utterances to be
            # discarded before Vosk ever received them. A 10% ratio still rejects
            # steady background noise while allowing short words and soft speech.
            return rms >= self._adaptive_voice_threshold and ratio >= 0.10
        zcr = self._zero_crossing_rate(data)
        return (
            rms >= self._adaptive_voice_threshold
            and self.config.zcr_min <= zcr <= self.config.zcr_max
        )

    def _observe_noise_floor(self, rms: int) -> None:
        if (
            not self.config.auto_calibrate
            or len(self._noise_samples) >= self._calibration_blocks
        ):
            return
        self._noise_samples.append(max(0, rms))
        if len(self._noise_samples) < self._calibration_blocks:
            return
        self._apply_noise_samples(self._noise_samples, announce=True)

    def _observe_long_silence(self, rms: int) -> None:
        if not self.config.auto_calibrate:
            return
        self._recent_silence.append(max(0, rms))
        if len(self._recent_silence) < self._recent_silence.maxlen:
            return
        self._apply_noise_samples(list(self._recent_silence), announce=False)

    def _apply_noise_samples(self, samples: list[int], *, announce: bool) -> None:
        ordered = sorted(samples)
        quiet_count = max(1, round(len(ordered) * 0.6))
        noise_floor = int(sum(ordered[:quiet_count]) / quiet_count)
        self._adaptive_silence_threshold = max(
            80,
            min(self.config.silence_threshold, round(noise_floor * 1.35)),
        )
        self._adaptive_voice_threshold = max(
            self.config.voice_threshold,
            round(noise_floor * self.config.noise_multiplier),
            self._adaptive_silence_threshold + 120,
        )
        if announce:
            self._emit(
                AudioEngineState.SILENCE,
                level=0,
                detail=(
                    "Audio calibrado "
                    f"(ruido {noise_floor}, voz {self._adaptive_voice_threshold})"
                ),
            )

    def _prepare_pcm16(self, data: bytes) -> bytes:
        if not self.config.normalize_audio or not data:
            return data
        usable_size = len(data) - (len(data) % 2)
        if usable_size <= 0:
            return data
        samples = np.frombuffer(data[:usable_size], dtype="<i2").astype(np.float64)
        if samples.size == 0:
            return data
        samples -= float(np.mean(samples))
        peak = float(np.max(np.abs(samples)))
        if peak <= 0:
            return np.zeros(samples.size, dtype="<i2").tobytes()
        gain = min(self.config.max_gain, self.config.target_peak / peak)
        gain = max(1.0, gain)
        prepared = np.clip(samples * gain, -32768, 32767).astype("<i2")
        return prepared.tobytes()

    def _level_from_rms(self, rms: int) -> int:
        threshold = max(self._adaptive_silence_threshold, 1)
        if rms <= threshold:
            return 0
        normalized = math.log10(max(rms, 1) / threshold + 1)
        return max(1, min(10, round(normalized * 8)))

    def _emit(
        self,
        state: AudioEngineState,
        *,
        level: int | None = None,
        text: str = "",
        detail: str = "",
    ) -> None:
        actual_level = self._last_level if level is None else max(0, min(10, level))
        if (
            state == self._last_state
            and actual_level == self._last_level
            and not text
            and not detail
        ):
            return
        self._last_state = state
        self._last_level = actual_level
        sink = self._sink
        if sink is not None:
            sink(
                AudioEngineEvent(
                    state=state,
                    level=actual_level,
                    device_name=self._device_name,
                    text=text,
                    detail=detail,
                )
            )
