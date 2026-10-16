from __future__ import annotations

from datetime import datetime, timezone

from core.runtime_composition_root import RuntimeComposition, RuntimeCompositionRoot

from .models import (
    LocalRuntimeBootstrapConfig,
    LocalRuntimeState,
    LocalRuntimeStatus,
)
from .state_store import JsonLocalRuntimeStateStore, LocalRuntimeStateStore


class LocalRuntimeBootstrap:
    """Starts and stops ROBY's composed local runtime without cognitive work."""

    def __init__(
        self,
        *,
        root: RuntimeCompositionRoot,
        config: LocalRuntimeBootstrapConfig,
        state_store: LocalRuntimeStateStore | None = None,
    ) -> None:
        self.root = root
        self.config = config
        self.state_store = state_store or JsonLocalRuntimeStateStore(config.state_path)
        self._composition: RuntimeComposition | None = None
        self._state = self.state_store.load() or LocalRuntimeState(
            owner=config.owner,
            session_id=config.session_id,
            status=LocalRuntimeStatus.CREATED,
        )

    @property
    def composition(self) -> RuntimeComposition | None:
        return self._composition

    @property
    def state(self) -> LocalRuntimeState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state.status is LocalRuntimeStatus.RUNNING

    def start(self, *, now: datetime | None = None) -> RuntimeComposition:
        timestamp = self._timestamp(now)
        if self.is_running:
            if self._composition is None:
                self._composition = self.root.compose()
            return self._composition
        try:
            composition = self.root.compose()
            state = LocalRuntimeState(
                owner=self.config.owner,
                session_id=self.config.session_id,
                status=LocalRuntimeStatus.RUNNING,
                started_at=timestamp,
                updated_at=timestamp,
            )
            self.state_store.save(state)
        except Exception as exc:
            failed = LocalRuntimeState(
                owner=self.config.owner,
                session_id=self.config.session_id,
                status=LocalRuntimeStatus.FAILED,
                failure=f"{type(exc).__name__}: {exc}",
                updated_at=timestamp,
            )
            self._state = failed
            try:
                self.state_store.save(failed)
            except Exception:
                pass
            raise
        self._composition = composition
        self._state = state
        return composition

    def stop(self, *, now: datetime | None = None) -> LocalRuntimeState:
        timestamp = self._timestamp(now)
        if self._state.status is LocalRuntimeStatus.STOPPED:
            return self._state
        state = LocalRuntimeState(
            owner=self.config.owner,
            session_id=self.config.session_id,
            status=LocalRuntimeStatus.STOPPED,
            started_at=self._state.started_at,
            stopped_at=timestamp,
            updated_at=timestamp,
        )
        self.state_store.save(state)
        self._state = state
        return state

    def __enter__(self) -> LocalRuntimeBootstrap:
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.stop()

    @staticmethod
    def _timestamp(value: datetime | None) -> datetime:
        timestamp = value or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("local runtime lifecycle time must be timezone-aware")
        return timestamp
