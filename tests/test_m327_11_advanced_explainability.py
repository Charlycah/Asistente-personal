from dataclasses import dataclass
from pathlib import Path

from app.audio_engine import AudioEngineState
from core.controlled_autonomy import (
    DeterministicAutonomyExplainer,
    render_autonomy_explanation,
)
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


def test_m327_11_explains_complete_governed_cycle(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(AudioSnapshot()),
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    result = runtime.diagnose_audio()

    assert result is not None
    explanation = DeterministicAutonomyExplainer().explain(result)

    assert explanation.policy_decision == "recommend"
    assert explanation.gate_decision == "authorize"
    assert explanation.execution_status == "executed"
    assert explanation.outcome_status == "succeeded"
    assert any(item.selected for item in explanation.candidates)


def test_m327_11_runtime_exposes_last_explanation(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(AudioSnapshot()),
        decision_journal_path=tmp_path / "journal.jsonl",
    )

    assert runtime.explain_last_autonomy_advanced() is None
    runtime.diagnose_audio()

    explanation = runtime.explain_last_autonomy_advanced()
    assert explanation is not None
    assert explanation.candidates[0].action == "diagnose_audio_runtime"


def test_m327_11_renderer_summarizes_decision_chain(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(AudioSnapshot()),
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    runtime.diagnose_audio()
    explanation = runtime.explain_last_autonomy_advanced()

    assert explanation is not None
    rendered = render_autonomy_explanation(explanation)
    assert "Policy decision: recommend" in rendered
    assert "autonomy gate: authorize" in rendered
    assert "Outcome: succeeded" in rendered


def test_m327_11_redacts_sensitive_observation_values(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=AudioReader(
            AudioSnapshot(error="api_key=very-secret-value")
        ),
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    runtime.diagnose_audio()
    explanation = runtime.explain_last_autonomy_advanced()

    assert explanation is not None
    assert all("very-secret-value" not in item for item in explanation.observation)
    assert any("[redacted]" in item for item in explanation.observation)
