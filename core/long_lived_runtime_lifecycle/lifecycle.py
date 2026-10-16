from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from core.local_runtime_bootstrap import LocalRuntimeBootstrap
from core.platform_runtime_compatibility import (
    apply_private_file_permissions,
    process_exists,
)

from .models import (
    LongLivedRuntimeConfig,
    LongLivedRuntimeState,
    LongLivedRuntimeStatus,
)
from .store import JsonLongLivedRuntimeStateStore, LongLivedRuntimeStateStore


class RuntimeLeaseError(RuntimeError):
    pass


class LongLivedRuntimeLifecycle:
    """Owns one long-lived local process around the official M179 bootstrap."""

    def __init__(
        self,
        *,
        bootstrap: LocalRuntimeBootstrap,
        config: LongLivedRuntimeConfig | None = None,
        state_store: LongLivedRuntimeStateStore | None = None,
        process_id: int | None = None,
    ) -> None:
        self.bootstrap = bootstrap
        self.config = config or LongLivedRuntimeConfig()
        self.state_store = state_store or JsonLongLivedRuntimeStateStore(
            self.config.heartbeat_path
        )
        self.process_id = process_id or os.getpid()
        self._owns_lease = False
        previous = self.state_store.load()
        generation = 1 if previous is None else previous.generation + 1
        self._state = LongLivedRuntimeState(
            owner=bootstrap.config.owner,
            session_id=bootstrap.config.session_id,
            process_id=self.process_id,
            status=LongLivedRuntimeStatus.CREATED,
            generation=generation,
        )

    @property
    def state(self) -> LongLivedRuntimeState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state.status in {
            LongLivedRuntimeStatus.RUNNING,
            LongLivedRuntimeStatus.DEGRADED,
        }

    def start(self, *, now: datetime | None = None) -> LongLivedRuntimeState:
        timestamp = self._timestamp(now)
        if self.is_running:
            return self._state
        self._acquire_lease(timestamp)
        try:
            self.bootstrap.start(now=timestamp)
            state = LongLivedRuntimeState(
                owner=self.bootstrap.config.owner,
                session_id=self.bootstrap.config.session_id,
                process_id=self.process_id,
                status=LongLivedRuntimeStatus.RUNNING,
                generation=self._state.generation,
                started_at=timestamp,
                heartbeat_at=timestamp,
                updated_at=timestamp,
            )
            self.state_store.save(state)
        except Exception as exc:
            self._release_lease()
            self._state = LongLivedRuntimeState(
                owner=self.bootstrap.config.owner,
                session_id=self.bootstrap.config.session_id,
                process_id=self.process_id,
                status=LongLivedRuntimeStatus.FAILED,
                generation=self._state.generation,
                failure=type(exc).__name__,
                updated_at=timestamp,
            )
            try:
                self.state_store.save(self._state)
            except Exception:
                pass
            raise
        self._state = state
        return state

    def heartbeat(self, *, now: datetime | None = None) -> LongLivedRuntimeState:
        timestamp = self._timestamp(now)
        if not self.is_running or not self._owns_lease:
            raise RuntimeError("long-lived runtime must be running for heartbeat")
        state = LongLivedRuntimeState(
            owner=self._state.owner,
            session_id=self._state.session_id,
            process_id=self.process_id,
            status=LongLivedRuntimeStatus.RUNNING,
            generation=self._state.generation,
            started_at=self._state.started_at,
            heartbeat_at=timestamp,
            updated_at=timestamp,
        )
        self.state_store.save(state)
        self._state = state
        return state

    def mark_degraded(
        self,
        failure: BaseException,
        *,
        now: datetime | None = None,
    ) -> LongLivedRuntimeState:
        timestamp = self._timestamp(now)
        if not self.is_running:
            raise RuntimeError("long-lived runtime must be active to degrade")
        state = LongLivedRuntimeState(
            owner=self._state.owner,
            session_id=self._state.session_id,
            process_id=self.process_id,
            status=LongLivedRuntimeStatus.DEGRADED,
            generation=self._state.generation,
            started_at=self._state.started_at,
            heartbeat_at=timestamp,
            failure=type(failure).__name__,
            updated_at=timestamp,
        )
        self.state_store.save(state)
        self._state = state
        return state

    def stop(self, *, now: datetime | None = None) -> LongLivedRuntimeState:
        timestamp = self._timestamp(now)
        if self._state.status is LongLivedRuntimeStatus.STOPPED:
            return self._state
        try:
            self.bootstrap.stop(now=timestamp)
            state = LongLivedRuntimeState(
                owner=self._state.owner,
                session_id=self._state.session_id,
                process_id=self.process_id,
                status=LongLivedRuntimeStatus.STOPPED,
                generation=self._state.generation,
                started_at=self._state.started_at,
                heartbeat_at=self._state.heartbeat_at,
                stopped_at=timestamp,
                updated_at=timestamp,
            )
            self.state_store.save(state)
            self._state = state
            return state
        finally:
            self._release_lease()

    def is_stale(self, *, now: datetime | None = None) -> bool:
        heartbeat = self._state.heartbeat_at
        if heartbeat is None:
            return False
        return self._timestamp(now) - heartbeat > self.config.stale_after

    def __enter__(self) -> LongLivedRuntimeLifecycle:
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc is not None and self.is_running:
            self.mark_degraded(exc)
        self.stop()

    def _acquire_lease(self, timestamp: datetime) -> None:
        path = Path(self.config.lease_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {
                "owner": self.bootstrap.config.owner,
                "process_id": self.process_id,
                "session_id": self.bootstrap.config.session_id,
                "started_at": timestamp.isoformat(),
            },
            sort_keys=True,
        )
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            if not self._recover_stale_lease(path, timestamp):
                raise RuntimeLeaseError("another ROBY local runtime owns the lease")
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        apply_private_file_permissions(path)
        self._owns_lease = True

    def _recover_stale_lease(self, path: Path, timestamp: datetime) -> bool:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            lease_pid = int(payload.get("process_id", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return False
        if lease_pid > 0 and self._process_exists(lease_pid):
            return False
        previous = self.state_store.load()
        if previous is None or previous.heartbeat_at is None:
            return False
        if timestamp - previous.heartbeat_at <= self.config.stale_after:
            return False
        path.unlink(missing_ok=True)
        return True

    @staticmethod
    def _process_exists(process_id: int) -> bool:
        return process_exists(process_id)

    def _release_lease(self) -> None:
        if not self._owns_lease:
            return
        try:
            Path(self.config.lease_path).unlink(missing_ok=True)
        finally:
            self._owns_lease = False

    @staticmethod
    def _timestamp(value: datetime | None) -> datetime:
        timestamp = value or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("long-lived runtime time must be timezone-aware")
        return timestamp
