from dataclasses import dataclass
from pathlib import Path

from app.audio_engine import AudioEngineState
from core.executive_recovery_health import RecoveryHealthCoordinator
from core.executive_runtime_integration import RuntimeExecutiveIntegration


@dataclass(frozen=True)
class AudioSnapshot:
    worker_alive: bool = True
    stream_open: bool = True
    callback_frames: int = 42
    queued_audio_frames: int = 0
    queued_texts: int = 0
    device_name: str = "Test microphone"
    error: str = ""
    state: AudioEngineState = AudioEngineState.SILENCE
    level: int = 12
    silence_threshold: int = 180
    voice_threshold: int = 380


class AudioReader:
    def __init__(self, snapshot: AudioSnapshot) -> None:
        self.snapshot = snapshot

    def diagnostic_snapshot(self) -> AudioSnapshot:
        return self.snapshot


def test_m327_5_audio_success_notifies_clear_result(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(AudioSnapshot()),
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    runtime.start()

    runtime.diagnose_audio()
    notifications = runtime.drain_notifications()

    assert notifications == (
        "Diagnóstico autónomo de audio completado: el motor está "
        "operativo. No fue necesario realizar cambios.",
    )
    assert runtime.snapshot.autonomy_notification_count == 1


def test_m327_5_audio_degradation_explains_detail_and_limits(
    tmp_path: Path,
) -> None:
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(
            AudioSnapshot(
                worker_alive=False,
                stream_open=False,
                error="input device unavailable",
                state=AudioEngineState.ERROR,
            )
        ),
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    runtime.start()

    runtime.diagnose_audio()
    message = runtime.drain_notifications()[0]

    assert "detecté una degradación" in message
    assert "input device unavailable" in message
    assert "No realicé cambios automáticos" in message


def test_m327_5_component_verification_notifies_runtime_result(
    tmp_path: Path,
) -> None:
    health = RecoveryHealthCoordinator()
    runtime = RuntimeExecutiveIntegration(
        health=health,
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    runtime.start()

    runtime._record_failure("executive.coordinator", "test failure")
    message = runtime.drain_notifications()[0]

    assert "Verificación autónoma de executive.coordinator" in message
    assert "estado degraded" in message
    assert "No realicé cambios automáticos" in message
