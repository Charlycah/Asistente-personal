from __future__ import annotations

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState


def _value(item: object | None) -> str:
    return str(getattr(item, "value", item or "missing")).strip().casefold()


class TextPerceptionEvidenceAdapter:
    """Translate interactive text reception into content-free evidence."""

    NODE_ID = "perception_and_evidence"
    CERTIFIED_TEXT_ORIGINS = frozenset(("internal", "desktop_text"))

    def observe_input(
        self,
        *,
        text: object,
        origin: object,
    ) -> CognitiveCycleNodeRecord:
        text_present = isinstance(text, str) and bool(text.strip())
        normalized_origin = _value(origin)
        if not text_present:
            return CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("perception:origin_declared",),
                reason_codes=("perception:empty_text",),
            )
        if normalized_origin in self.CERTIFIED_TEXT_ORIGINS:
            return CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=(
                    "perception:text_received",
                    "perception:origin_declared",
                    "perception:interactive_submission",
                ),
            )
        return CognitiveCycleNodeRecord(
            node_id=self.NODE_ID,
            state=CognitiveCycleNodeState.DEGRADED,
            evidence_codes=(
                "perception:text_payload_present",
                "perception:origin_declared",
            ),
            reason_codes=("perception:source_channel_not_certified",),
        )
