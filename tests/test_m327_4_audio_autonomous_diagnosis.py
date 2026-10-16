from dataclasses import dataclass
from pathlib import Path

from app.audio_engine import AudioEngineState
from core.controlled_autonomy import CapabilityRunStatus, OutcomeStatus
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
        self.calls = 0

    def diagnostic_snapshot(self) -> AudioSnapshot:
        self.calls += 1
        return self.snapshot


def test_m327_4_runtime_executes_read_only_audio_diagnosis(tmp_path: Path) -> None:
    reader = AudioReader(AudioSnapshot())
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=reader,
        decision_journal_path=tmp_path / "journal.jsonl",
    )

    result = runtime.diagnose_audio()

    assert result is not None
    assert result.status is CapabilityRunStatus.EXECUTED
    assert result.candidate is not None
    assert result.candidate.action == "diagnose_audio_runtime"
    assert result.outcome is not None
    assert result.outcome.status is OutcomeStatus.SUCCEEDED
    assert reader.calls >= 2
    assert runtime.snapshot.autonomous_cycle_count == 1


def test_m327_4_audio_error_is_reported_as_degraded(tmp_path: Path) -> None:
    reader = AudioReader(
        AudioSnapshot(
            worker_alive=False,
            stream_open=False,
            error="input device unavailable",
            state=AudioEngineState.ERROR,
        )
    )
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=reader,
        decision_journal_path=tmp_path / "journal.jsonl",
    )

    result = runtime.diagnose_audio()

    assert result is not None and result.outcome is not None
    assert result.outcome.status is OutcomeStatus.DEGRADED
    assert "error=input device unavailable" in result.outcome.evidence


def test_m327_4_audio_diagnosis_persists_governed_decision(
    tmp_path: Path,
) -> None:
    path = tmp_path / "journal.jsonl"
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(AudioSnapshot()),
        decision_journal_path=path,
    )

    result = runtime.diagnose_audio()

    assert result is not None
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "diagnose_audio_runtime" in content
    assert "audio_runtime_requires_diagnosis" in content
