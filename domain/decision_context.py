from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DecisionContext:
    """
    Representa el estado del mundo observado por ROBY en el instante
    en que debe tomar una decisión.

    Es construido exclusivamente por ContextBuilder y consumido por
    DecisionEngine y Planner.
    """

    current_time: datetime
    conversation_state: str = "idle"
    last_user_message: str | None = None
    last_roby_response: str | None = None
    system_state: str = "ready"
    active_plan: str | None = None
