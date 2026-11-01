from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import CancelledError, Executor, Future
from dataclasses import dataclass, replace
from hashlib import sha256
from threading import RLock
from typing import Protocol

from app.desktop_governed_image_preview_decoder import (
    decode_governed_jpeg_preview,
)


class PreviewViewer(Protocol):
    def open(self, artifacts: tuple[object, ...]) -> None: ...

    def render_preview(
        self,
        artifact: object,
        payload: bytes,
        content_type: str,
    ) -> bool: ...


class VICPreviewViewer(PreviewViewer, Protocol):
    def render_preview_vic(
        self,
        artifact: object,
        payload: bytes,
        content_type: str,
        *,
        visible_ordinal: int,
    ) -> bool: ...


class PreviewDispatcher(Protocol):
    def post(self, callback: Callable[[], None]) -> None: ...


class PreviewArtifact(Protocol):
    @property
    def preview_url(self) -> str: ...


PreviewFetcher = Callable[[str, float, int], tuple[bytes, str]]


@dataclass(frozen=True)
class PreviewSlotResult:
    """Coordination evidence only; not a VIC or E2 acceptance receipt."""

    presentation_id: int
    slot_id: int
    artifact_id: int
    visible_ordinal: int
    generation_token: int
    attempt_id: int
    state: str
    reason: str | None = None


@dataclass(frozen=True)
class VisualCommitReceipt:
    """Evidence of a complete individual image-and-ordinal UI unit."""

    presentation_id: int
    slot_id: int
    artifact_id: int
    visible_ordinal: int
    generation_token: int
    attempt_id: int


class GovernedImagePreviewCoordinator:
    """Reserve per-occurrence previews and deliver only current UI callbacks."""

    _TERMINAL = frozenset({
        "DELIVERED", "REJECTED", "FAILED", "CANCELLED", "SUPERSEDED",
    })

    def __init__(
        self,
        *,
        viewer: PreviewViewer,
        dispatcher: PreviewDispatcher,
        fetcher: PreviewFetcher,
        executor: Executor,
        timeout: float = 5.0,
        max_bytes: int = 1_000_000,
        vic_enabled: bool = False,
    ) -> None:
        self._vic_enabled = vic_enabled
        self._viewer = viewer
        self._dispatcher = dispatcher
        self._fetcher = fetcher
        self._executor = executor
        self._timeout = timeout
        self._max_bytes = max_bytes
        self._generation = 0
        self._shutdown = False
        self._lock = RLock()
        self._slots: dict[int, PreviewSlotResult] = {}
        self._history: list[PreviewSlotResult] = []
        self._vic_receipts: list[VisualCommitReceipt] = []
        self._compensation_events: list[tuple[tuple[int, ...], str, int, str]] = []
        self._compensation_recovering: set[tuple[int, ...]] = set()
        self._duplicate_events: list[tuple[int, int, str]] = []
        self._delivery_signatures: dict[tuple[int, int, int], tuple[str, str]] = {}
        self._artifacts: dict[int, PreviewArtifact] = {}
        self._next_attempt = 0

    @property
    def results(self) -> tuple[PreviewSlotResult, ...]:
        """Immutable snapshots in original presentation/ordinal order."""
        with self._lock:
            return tuple(self._history) + tuple(self._slots.values())

    @property
    def vic_receipts(self) -> tuple[VisualCommitReceipt, ...]:
        """Historical individual VIC evidence, including superseded presentations."""
        with self._lock:
            return tuple(self._vic_receipts)

    def recover_compensation(
        self,
        unit_key: tuple[int, ...],
    ) -> bool:
        """Reintentar una compensacion VIC individual no confirmada.

        Debe invocarse en el hilo UI. No modifica slots ni recibos VIC.
        """
        if (
            not isinstance(unit_key, tuple)
            or len(unit_key) != 6
            or any(
                type(value) is not int
                for value in unit_key
            )
        ):
            return False

        with self._lock:
            if unit_key in self._compensation_recovering:
                return False

            events = [
                event
                for event in self._compensation_events
                if event[0] == unit_key
            ]

            if not events:
                return False

            _, previous_status, previous_attempt, _ = events[-1]

            if previous_status not in (
                "COMPENSATION_PENDING",
                "COMPENSATION_ERROR",
            ):
                return False

            self._compensation_recovering.add(unit_key)

        try:
            discard = getattr(
                self._viewer,
                "discard_preview_vic",
                None,
            )

            if not callable(discard):
                status = "COMPENSATION_ERROR"
                outcome = "DiscardUnavailable"
                recovered = False
            else:
                try:
                    recovered = discard(unit_key) is True
                except Exception as exc:
                    status = "COMPENSATION_ERROR"
                    outcome = type(exc).__name__
                    recovered = False
                else:
                    status = (
                        "RECOVERED"
                        if recovered
                        else "COMPENSATION_PENDING"
                    )
                    outcome = (
                        "TRUE"
                        if recovered
                        else "FALSE"
                    )

            with self._lock:
                self._compensation_events.append(
                    (
                        unit_key,
                        status,
                        previous_attempt + 1,
                        outcome,
                    )
                )

            return recovered

        finally:
            with self._lock:
                self._compensation_recovering.discard(unit_key)

    @property
    def compensation_events(
        self,
    ) -> tuple[tuple[tuple[int, ...], str, int, str], ...]:
        """Historial inmutable de resultados de compensacion VIC."""
        with self._lock:
            return tuple(self._compensation_events)

    @property
    def active_vic_receipts(self) -> tuple[VisualCommitReceipt, ...]:
        """VIC evidence belonging to the currently active generation."""
        with self._lock:
            return tuple(
                receipt for receipt in self._vic_receipts
                if receipt.generation_token == self._generation
                and not self._shutdown
            )

    @property
    def duplicate_events(self) -> tuple[tuple[int, int, str], ...]:
        """(slot_id, attempt_id, classification) for rejected duplicate callbacks."""
        with self._lock:
            return tuple(self._duplicate_events)

    def _supersede(self, state: str) -> None:
        for slot_id, record in tuple(self._slots.items()):
            if record.state not in self._TERMINAL:
                self._slots[slot_id] = replace(record, state=state)

    def cancel(self) -> None:
        """Invalidate pending callbacks without touching Tk from workers."""
        with self._lock:
            self._supersede("CANCELLED")
            self._generation += 1

    def shutdown(self) -> None:
        """Invalidate work and request nonblocking executor shutdown."""
        with self._lock:
            if self._shutdown:
                return
            self._shutdown = True
            self._supersede("CANCELLED")
            self._generation += 1
        self._executor.shutdown(wait=False, cancel_futures=True)

    def present(self, artifacts: Sequence[PreviewArtifact]) -> None:
        """Reserve every occurrence before scheduling asynchronous work."""
        supplied = tuple(artifacts)
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Preview coordinator is shut down")
            self._supersede("SUPERSEDED")
            self._history.extend(self._slots.values())
            self._generation += 1
            generation = self._generation
            self._slots = {}
            self._artifacts = {}
            for index, artifact in enumerate(supplied, start=1):
                self._next_attempt += 1
                self._slots[index] = PreviewSlotResult(
                    presentation_id=generation,
                    slot_id=index,
                    artifact_id=id(artifact),
                    visible_ordinal=index,
                    generation_token=generation,
                    attempt_id=self._next_attempt,
                    state="RESERVED",
                )
                self._artifacts[index] = artifact

        if not supplied:
            return
        try:
            self._viewer.open(supplied)
        except Exception:
            with self._lock:
                for slot_id, record in tuple(self._slots.items()):
                    if record.generation_token == generation and record.state == "RESERVED":
                        self._slots[slot_id] = replace(
                            record, state="FAILED", reason="viewer_open_failed",
                        )
            raise
        for slot_id in range(1, len(supplied) + 1):
            self._submit(slot_id, generation)

    def retry(self, slot_id: int) -> bool:
        """Explicitly retry a failed occurrence; never retry automatically."""
        with self._lock:
            record = self._slots.get(slot_id)
            if (
                self._shutdown or record is None
                or record.generation_token != self._generation
                or record.state not in {"FAILED", "REJECTED"}
            ):
                return False
            self._next_attempt += 1
            self._slots[slot_id] = replace(
                record, attempt_id=self._next_attempt,
                state="RESERVED", reason=None,
            )
            generation = self._generation
        self._submit(slot_id, generation)
        return True

    def _update(
        self,
        slot_id: int,
        generation: int,
        attempt_id: int,
        expected: frozenset[str],
        state: str,
        reason: str | None = None,
    ) -> bool:
        with self._lock:
            record = self._slots.get(slot_id)
            if (
                self._shutdown or generation != self._generation
                or record is None or record.attempt_id != attempt_id
                or record.state not in expected
            ):
                return False
            self._slots[slot_id] = replace(record, state=state, reason=reason)
            return True

    def _submit(self, slot_id: int, generation: int) -> None:
        with self._lock:
            record = self._slots.get(slot_id)
            if record is None or record.generation_token != generation:
                return
            attempt_id = record.attempt_id
            artifact = self._artifacts[slot_id]
            if not self._update(
                slot_id, generation, attempt_id,
                frozenset({"RESERVED"}), "FETCH_PENDING",
            ):
                return
        try:
            future = self._executor.submit(
                self._fetch_and_prepare,
                artifact.preview_url,
                self._timeout,
                self._max_bytes,
            )
            future.add_done_callback(
                lambda completed, slot=slot_id, token=generation, attempt=attempt_id: (
                    self._schedule_result(completed, slot, token, attempt)
                )
            )
        except Exception:
            self._update(
                slot_id, generation, attempt_id,
                frozenset({"FETCH_PENDING"}), "FAILED", "submit_failed",
            )

    def _fetch_and_prepare(
        self,
        url: str,
        timeout: float,
        max_bytes: int,
    ) -> tuple[bytes, str] | None:
        payload, content_type = self._fetcher(url, timeout, max_bytes)
        if content_type.casefold() != "image/jpeg":
            return payload, content_type
        converted = decode_governed_jpeg_preview(payload, content_type)
        if converted is None:
            return None
        return converted, "image/png"

    def _schedule_result(
        self,
        future: Future[tuple[bytes, str] | None],
        slot_id: int,
        generation: int,
        attempt_id: int,
    ) -> None:
        try:
            result = future.result()
        except Exception:
            self._update(
                slot_id, generation, attempt_id,
                frozenset({"FETCH_PENDING"}), "FAILED", "fetch_failed",
            )
            return
        if result is None:
            self._update(
                slot_id, generation, attempt_id,
                frozenset({"FETCH_PENDING"}), "REJECTED", "decode_rejected",
            )
            return
        payload, content_type = result
        signature = (sha256(payload).hexdigest(), content_type.casefold())
        if not self._update(
            slot_id, generation, attempt_id,
            frozenset({"FETCH_PENDING"}), "DELIVERY_PENDING",
        ):
            with self._lock:
                record = self._slots.get(slot_id)
                if (record is not None and record.generation_token == generation
                        and record.attempt_id == attempt_id
                        and record.state in {"DELIVERY_PENDING", "DELIVERED"}):
                    prior = self._delivery_signatures.get(
                        (generation, slot_id, attempt_id)
                    )
                    classification = ("duplicate_equivalent" if prior == signature
                                      else "duplicate_conflict")
                    self._duplicate_events.append(
                        (slot_id, attempt_id, classification)
                    )
            return
        with self._lock:
            self._delivery_signatures[(generation, slot_id, attempt_id)] = signature
        try:
            self._dispatcher.post(
                lambda: self._deliver(
                    slot_id, payload, content_type, generation, attempt_id,
                )
            )
        except Exception:
            self._update(
                slot_id, generation, attempt_id,
                frozenset({"DELIVERY_PENDING"}), "FAILED", "dispatch_failed",
            )

    def _deliver(
        self,
        slot_id: int,
        payload: bytes,
        content_type: str,
        generation: int,
        attempt_id: int,
    ) -> None:
        # Ejecucion despachada al hilo UI.
        with self._lock:
            record = self._slots.get(slot_id)
            if (
                self._shutdown
                or generation != self._generation
                or record is None
                or record.attempt_id != attempt_id
                or record.state != "DELIVERY_PENDING"
            ):
                return

            artifact = self._artifacts[slot_id]
            unit_key = (
                record.presentation_id,
                record.slot_id,
                record.artifact_id,
                record.visible_ordinal,
                record.generation_token,
                record.attempt_id,
            )

        if not any(
            item is artifact for item in self._viewer.artifacts
        ):
            self._update(
                slot_id, generation, attempt_id,
                frozenset({"DELIVERY_PENDING"}),
                "CANCELLED", "viewer_closed",
            )
            return

        identified = False
        discard = None

        try:
            if self._vic_enabled:
                render_identified = getattr(
                    self._viewer,
                    "render_preview_vic_identified",
                    None,
                )
                discard_candidate = getattr(
                    self._viewer,
                    "discard_preview_vic",
                    None,
                )

                identified = (
                    callable(render_identified)
                    and callable(discard_candidate)
                )

                if identified:
                    discard = discard_candidate
                    accepted = render_identified(
                        artifact,
                        payload,
                        content_type,
                        visible_ordinal=record.visible_ordinal,
                        unit_key=unit_key,
                    )
                else:
                    render_vic = getattr(
                        self._viewer,
                        "render_preview_vic",
                        None,
                    )
                    if not callable(render_vic):
                        raise RuntimeError(
                            "VIC viewer operation unavailable"
                        )
                    accepted = render_vic(
                        artifact,
                        payload,
                        content_type,
                        visible_ordinal=record.visible_ordinal,
                    )
            else:
                accepted = self._viewer.render_preview(
                    artifact, payload, content_type,
                )

        except Exception:
            self._update(
                slot_id, generation, attempt_id,
                frozenset({"DELIVERY_PENDING"}),
                "FAILED", "render_failed",
            )
            return

        if self._vic_enabled and accepted:
            with self._lock:
                current = self._slots.get(slot_id)
                invalidated = (
                    self._shutdown
                    or generation != self._generation
                    or current is None
                    or current.generation_token != generation
                    or current.attempt_id != attempt_id
                    or current.state != "DELIVERY_PENDING"
                )

                if not invalidated:
                    receipt = VisualCommitReceipt(
                        presentation_id=current.presentation_id,
                        slot_id=current.slot_id,
                        artifact_id=current.artifact_id,
                        visible_ordinal=current.visible_ordinal,
                        generation_token=current.generation_token,
                        attempt_id=current.attempt_id,
                    )
                    self._vic_receipts.append(receipt)
                    self._slots[slot_id] = replace(
                        current, state="DELIVERED", reason=None,
                    )

            if invalidated:
                # Compensacion fuera del bloqueo del coordinador.
                if identified and discard is not None:
                    try:
                        discarded = discard(unit_key)
                    except Exception as exc:
                        status = "COMPENSATION_ERROR"
                        outcome = type(exc).__name__
                    else:
                        status = (
                            "COMPENSATED"
                            if discarded is True
                            else "COMPENSATION_PENDING"
                        )
                        outcome = (
                            "TRUE"
                            if discarded is True
                            else "FALSE"
                        )

                    with self._lock:
                        attempt = 1 + sum(
                            1
                            for key, _, _, _ in self._compensation_events
                            if key == unit_key
                        )
                        self._compensation_events.append(
                            (unit_key, status, attempt, outcome)
                        )
                return

            return

        self._update(
            slot_id, generation, attempt_id,
            frozenset({"DELIVERY_PENDING"}),
            "DELIVERED" if accepted else "REJECTED",
            None if accepted else "render_rejected",
        )
