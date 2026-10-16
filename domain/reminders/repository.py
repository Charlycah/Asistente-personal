from typing import Protocol
from uuid import UUID

from .entities import Reminder


class ReminderRepository(Protocol):
    def save(self, reminder: Reminder) -> None: ...

    def get_by_id(self, reminder_id: UUID) -> Reminder | None: ...

    def list_pending(self) -> list[Reminder]: ...

    def delete(self, reminder_id: UUID) -> None: ...
