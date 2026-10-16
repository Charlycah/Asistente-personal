from datetime import timedelta
from pathlib import Path

import pytest

from app.audio_engine import AudioEngineState
from core.controlled_autonomy import JsonExperienceMemory
from core.executive_runtime_integration import RuntimeExecutiveIntegration


class AudioSnapshot:
    worker_alive = True
    stream_open = True
    callback_frames = 12
    queued_audio_frames = 0
    queued_texts = 0
    device_name = "Memory microphone"
    error = ""
    state = AudioEngineState.SILENCE
    level = 10
    silence_threshold = 180
    voice_threshold = 380


class AudioReader:
    def diagnostic_snapshot(self) -> AudioSnapshot:
        return AudioSnapshot()


def test_m327_7_experience_survives_runtime_restart(tmp_path: Path) -> None:
    journal_path = tmp_path / "journal.jsonl"
    memory_path = tmp_path / "experience.json"
    first = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(),
        decision_journal_path=journal_path,
        experience_memory_path=memory_path,
    )

    first.diagnose_audio()
    restored = RuntimeExecutiveIntegration(
        decision_journal_path=journal_path,
        experience_memory_path=memory_path,
    )

    snapshot = restored.experience_memory.snapshot()
    assert snapshot.total_occurrences == 1
    assert len(snapshot.patterns) == 1
    assert snapshot.patterns[0].action == "diagnose_audio_runtime"
    assert snapshot.patterns[0].succeeded == 1


def test_m327_7_repeated_outcomes_are_aggregated(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(),
        autonomy_deduplication_window=timedelta(0),
        decision_journal_path=tmp_path / "journal.jsonl",
        experience_memory_path=tmp_path / "experience.json",
    )

    runtime.diagnose_audio()
    runtime.diagnose_audio()

    snapshot = runtime.snapshot
    pattern = runtime.experience_memory.snapshot().patterns[0]
    assert snapshot.autonomy_experience_count == 2
    assert snapshot.autonomy_experience_pattern_count == 1
    assert pattern.occurrences == 2
    assert pattern.succeeded == 2


def test_m327_7_corrupt_experience_memory_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "experience.json"
    path.write_text('{"schema_version":1,"patterns":[', encoding="utf-8")

    with pytest.raises(ValueError, match="invalid experience memory file"):
        JsonExperienceMemory(path)
