from app.audio_engine import AudioEngineEvent, AudioEngineState
from app.voice_input import SafeVoiceInput


class _LifecycleVoiceInput:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.paused = None
        self.sink = None
        self.error = ""

    def transcribe(self) -> str:
        return "hola roby"

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def set_paused(self, paused: bool) -> None:
        self.paused = paused

    def set_event_sink(self, sink) -> None:
        self.sink = sink


def test_m306_safe_voice_input_preserves_audio_engine_lifecycle():
    engine = _LifecycleVoiceInput()
    voice_input = SafeVoiceInput(engine)
    events: list[AudioEngineEvent] = []

    voice_input.set_event_sink(events.append)
    voice_input.start()
    voice_input.set_paused(True)
    assert engine.sink is not None
    engine.sink(AudioEngineEvent(AudioEngineState.SILENCE, detail="abierto"))
    voice_input.stop()

    assert voice_input.transcribe() == "hola roby"
    assert engine.started is True
    assert engine.paused is True
    assert engine.stopped is True
    assert events[0].detail == "abierto"
    assert voice_input.error == ""
