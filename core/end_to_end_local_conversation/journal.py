from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from core.platform_runtime_compatibility import apply_private_file_permissions

from .models import LocalConversationTurn


@runtime_checkable
class LocalConversationJournal(Protocol):
    def append(self, turn: LocalConversationTurn) -> None: ...
    def list_for_session(
        self, owner: str, session_id: str
    ) -> tuple[LocalConversationTurn, ...]: ...


class JsonLinesLocalConversationJournal:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def append(self, turn: LocalConversationTurn) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "created_at": turn.created_at.isoformat(),
            "network_access_performed": turn.network_access_performed,
            "operational_response_id": turn.operational_response_id,
            "owner": turn.owner,
            "pipeline_result_id": turn.pipeline_result_id,
            "provider_call_performed": turn.provider_call_performed,
            "rationale": list(turn.rationale),
            "response_path": turn.response_path.value,
            "degradation_reason": turn.degradation_reason.value,
            "response_text": turn.response_text,
            "retrieval_performed": turn.retrieval_performed,
            "sequence": turn.sequence,
            "session_id": turn.session_id,
            "status": turn.status.value,
            "turn_id": turn.turn_id,
            "user_text": turn.user_text,
        }
        line = json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
        descriptor = os.open(
            self.path,
            os.O_APPEND | os.O_CREAT | os.O_WRONLY,
            0o600,
        )
        try:
            os.write(descriptor, line.encode("utf-8"))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        apply_private_file_permissions(self.path)

    def list_for_session(
        self, owner: str, session_id: str
    ) -> tuple[LocalConversationTurn, ...]:
        if not self.path.exists():
            return ()
        turns = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            payload["created_at"] = datetime.fromisoformat(payload["created_at"])
            turn = LocalConversationTurn(**payload)
            if (
                turn.owner.casefold() == owner.strip().casefold()
                and turn.session_id == session_id.strip()
            ):
                turns.append(turn)
        return tuple(sorted(turns, key=lambda item: item.sequence))
