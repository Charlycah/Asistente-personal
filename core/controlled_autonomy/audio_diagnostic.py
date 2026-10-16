from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from .contracts import (
    ActionCandidate,
    AutonomyDecision,
    DecisionDisposition,
    DecisionOutcome,
    OutcomeStatus,
)
from .situation_assessment import ObservationSeverity, RuntimeObservation


@runtime_checkable
class AudioDiagnosticSnapshot(Protocol):
    worker_alive: bool
    stream_open: bool
    callback_frames: int
    queued_audio_frames: int
    queued_texts: int
    device_name: str
    error: str
    state: object
    level: int
    silence_threshold: int
    voice_threshold: int


@runtime_checkable
class AudioDiagnosticReader(Protocol):
    def diagnostic_snapshot(self) -> AudioDiagnosticSnapshot | None: ...


class DiagnoseAudioRuntimeCapability:
    """Read-only diagnosis of the active local audio runtime."""

    action = "diagnose_audio_runtime"

    def __init__(self, reader: AudioDiagnosticReader) -> None:
        self._reader = reader

    def execute(
        self,
        decision: AutonomyDecision,
        candidate: ActionCandidate,
    ) -> DecisionOutcome:
        if decision.disposition is not DecisionDisposition.AUTHORIZE:
            raise ValueError("capability execution requires authorization")
        if candidate.candidate_id != decision.candidate_id:
            raise ValueError("candidate must match the authorized decision")
        if candidate.action != self.action:
            raise ValueError("unsupported capability action")
        try:
            snapshot = self._reader.diagnostic_snapshot()
        except Exception as exc:
            return _failed_outcome(decision, exc)
        if snapshot is None:
            return DecisionOutcome(
                decision_id=decision.decision_id,
                status=OutcomeStatus.UNKNOWN,
                observed_at=datetime.now(timezone.utc),
                summary="Audio diagnostic snapshot is unavailable",
                evidence=("snapshot=none",),
            )
        state = getattr(snapshot.state, "value", str(snapshot.state))
        healthy = snapshot.worker_alive and snapshot.stream_open and not snapshot.error
        status = OutcomeStatus.SUCCEEDED if healthy else OutcomeStatus.DEGRADED
        return DecisionOutcome(
            decision_id=decision.decision_id,
            status=status,
            observed_at=datetime.now(timezone.utc),
            summary=(
                "Audio runtime is operational"
                if healthy
                else "Audio runtime diagnosis found a degraded condition"
            ),
            evidence=(
                f"worker_alive={snapshot.worker_alive}",
                f"stream_open={snapshot.stream_open}",
                f"callback_frames={snapshot.callback_frames}",
                f"queued_audio_frames={snapshot.queued_audio_frames}",
                f"queued_texts={snapshot.queued_texts}",
                f"device_name={snapshot.device_name or 'unknown'}",
                f"state={state}",
                f"level={snapshot.level}",
                f"silence_threshold={snapshot.silence_threshold}",
                f"voice_threshold={snapshot.voice_threshold}",
                f"error={snapshot.error or 'none'}",
            ),
        )


def observation_from_audio_error(
    reader: AudioDiagnosticReader,
) -> RuntimeObservation:
    try:
        snapshot = reader.diagnostic_snapshot()
    except Exception as exc:
        facts = (f"snapshot_error={type(exc).__name__}: {exc}",)
        attributes = {"audio_state": "unknown"}
    else:
        if snapshot is None:
            facts = ("snapshot=none",)
            attributes = {"audio_state": "unknown"}
        else:
            state = getattr(snapshot.state, "value", str(snapshot.state))
            facts = (
                f"worker_alive={snapshot.worker_alive}",
                f"stream_open={snapshot.stream_open}",
                f"audio_state={state}",
                f"error={snapshot.error or 'none'}",
            )
            attributes = {"audio_state": state}
    return RuntimeObservation(
        kind="audio_runtime.error",
        source="audio_runtime.local_microphone",
        observed_at=datetime.now(timezone.utc),
        facts=facts,
        severity=ObservationSeverity.WARNING,
        confidence=1.0,
        attributes=attributes,
    )


def _failed_outcome(
    decision: AutonomyDecision,
    error: Exception,
) -> DecisionOutcome:
    return DecisionOutcome(
        decision_id=decision.decision_id,
        status=OutcomeStatus.FAILED,
        observed_at=datetime.now(timezone.utc),
        summary="Audio runtime diagnosis failed",
        evidence=(f"error={type(error).__name__}: {error}",),
    )


__all__ = [
    "AudioDiagnosticReader",
    "AudioDiagnosticSnapshot",
    "DiagnoseAudioRuntimeCapability",
    "observation_from_audio_error",
]
