from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.household_memory import (
    HouseholdMemoryCategory,
    HouseholdMemoryEntry,
    HouseholdMemoryManager,
    HouseholdMemoryOwner,
    HouseholdMemoryStatus,
)
from infrastructure.repositories.sqlite_household_memory_repository import (
    SQLiteHouseholdMemoryRepository,
)


@dataclass(frozen=True)
class HouseholdKnowledgeResult:
    handled: bool
    response_text: str = ""


class SupervisedLearningAction(str, Enum):
    STORE = "store"
    UPDATE = "update"
    ARCHIVE = "archive"


@dataclass(frozen=True)
class PendingKnowledgeChange:
    action: SupervisedLearningAction
    details: str = ""
    entry_id: str = ""
    title: str = ""


class HouseholdKnowledgeService:
    """Conversational access to ROBY's existing structured household memory."""

    _STORE_PREFIXES = (
        "guardá como conocimiento ",
        "guarda como conocimiento ",
        "recordá como dato del hogar ",
        "recorda como dato del hogar ",
        "anotá como dato del hogar ",
        "anota como dato del hogar ",
    )
    _LIST_TRIGGERS = (
        "qué sabés del hogar",
        "que sabes del hogar",
        "conocimiento del hogar",
        "datos del hogar",
    )

    def __init__(self, db_path: str) -> None:
        self.manager = HouseholdMemoryManager(SQLiteHouseholdMemoryRepository(db_path))
        self._pending: PendingKnowledgeChange | None = None

    def handle(self, text: str, *, now: datetime) -> HouseholdKnowledgeResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()

        supervised = self._handle_supervised(normalized, folded, now=now)
        if supervised is not None:
            return supervised
        for prefix in self._STORE_PREFIXES:
            if folded.startswith(prefix):
                details = normalized[len(prefix) :].strip(" .")
                if not details:
                    return HouseholdKnowledgeResult(
                        True, "Necesito el dato que querés guardar."
                    )
                category = self._category(details)
                title = self._title(details)
                entry = HouseholdMemoryEntry(
                    title=title,
                    details=details,
                    category=category,
                    owner=HouseholdMemoryOwner.SHARED,
                    source="conversation",
                    created_at=now,
                    updated_at=now,
                    tags=self._tags(details),
                )
                self.manager.remember(entry)
                return HouseholdKnowledgeResult(
                    True,
                    f"Guardé en el conocimiento del hogar: {title}.",
                )

        if any(trigger in folded for trigger in self._LIST_TRIGGERS):
            query = self._query(folded)
            entries = self.manager.recall(
                query,
                status=HouseholdMemoryStatus.ACTIVE,
            )
            if not entries:
                return HouseholdKnowledgeResult(
                    True, "No encontré datos del hogar para esa consulta."
                )
            lines = ["Conocimiento del hogar:"]
            for entry in entries[-10:]:
                lines.append(
                    f"- {entry.title}: {entry.details} "
                    f"[{entry.normalized_category.value}]"
                )
            return HouseholdKnowledgeResult(True, "\n".join(lines))

        archive_pattern = (
            r"^(?:archivá|archiva|eliminá|elimina) "
            r"(?:el dato |el conocimiento )?(?P<query>.+)$"
        )
        archive = re.match(archive_pattern, folded)
        if archive:
            matches = self.manager.recall(
                archive.group("query"), status=HouseholdMemoryStatus.ACTIVE
            )
            if not matches:
                return HouseholdKnowledgeResult(True, "No encontré ese dato del hogar.")
            entry = matches[-1]
            self.manager.archive(entry.entry_id, now=now)
            return HouseholdKnowledgeResult(True, f"Archivé: {entry.title}.")

        return HouseholdKnowledgeResult(False)

    def _handle_supervised(
        self, normalized: str, folded: str, *, now: datetime
    ) -> HouseholdKnowledgeResult | None:
        confirm_commands = {
            "confirmar aprendizaje",
            "confirmá aprendizaje",
            "confirma aprendizaje",
        }
        if folded in confirm_commands:
            return self._confirm_pending(now=now)
        cancel_commands = {
            "cancelar aprendizaje",
            "cancelá aprendizaje",
            "cancela aprendizaje",
        }
        if folded in cancel_commands:
            if self._pending is None:
                return HouseholdKnowledgeResult(
                    True, "No hay ningún aprendizaje pendiente."
                )
            self._pending = None
            return HouseholdKnowledgeResult(True, "Cancelé el aprendizaje pendiente.")
        pending_queries = {
            "qué aprendizaje está pendiente",
            "que aprendizaje esta pendiente",
        }
        if folded in pending_queries:
            if self._pending is None:
                return HouseholdKnowledgeResult(
                    True, "No hay ningún aprendizaje pendiente."
                )
            return HouseholdKnowledgeResult(True, self._pending_summary())

        learn = re.match(
            r"^(?:roby[, ]+)?(?:aprendé|aprende) que (?P<details>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if learn:
            details = learn.group("details").strip(" .")
            self._pending = PendingKnowledgeChange(
                SupervisedLearningAction.STORE, details=details
            )
            return HouseholdKnowledgeResult(
                True,
                f"Propongo aprender: {details}. "
                "Decí 'confirmar aprendizaje' para guardarlo o "
                "'cancelar aprendizaje' para descartarlo.",
            )

        correction = re.match(
            r"^(?:corregí|corregi|corrige) (?:el )?(?:dato|conocimiento) "
            r"(?P<query>.+?) (?:por|a) (?P<details>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if correction:
            matches = self.manager.recall(
                correction.group("query"), status=HouseholdMemoryStatus.ACTIVE
            )
            if not matches:
                return HouseholdKnowledgeResult(True, "No encontré ese conocimiento.")
            entry = matches[-1]
            details = correction.group("details").strip(" .")
            self._pending = PendingKnowledgeChange(
                SupervisedLearningAction.UPDATE,
                details=details,
                entry_id=entry.entry_id,
                title=entry.title,
            )
            return HouseholdKnowledgeResult(
                True,
                f"Propongo reemplazar '{entry.details}' por '{details}'. "
                "Decí 'confirmar aprendizaje' para aplicar el cambio.",
            )

        forget = re.match(
            r"^(?:olvidá|olvida) (?:el )?(?:dato|conocimiento )?(?P<query>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if forget:
            matches = self.manager.recall(
                forget.group("query"), status=HouseholdMemoryStatus.ACTIVE
            )
            if not matches:
                return HouseholdKnowledgeResult(True, "No encontré ese conocimiento.")
            entry = matches[-1]
            self._pending = PendingKnowledgeChange(
                SupervisedLearningAction.ARCHIVE,
                entry_id=entry.entry_id,
                title=entry.title,
            )
            return HouseholdKnowledgeResult(
                True,
                f"Propongo olvidar: {entry.details}. "
                "Decí 'confirmar aprendizaje' para archivarlo.",
            )
        return None

    def _confirm_pending(self, *, now: datetime) -> HouseholdKnowledgeResult:
        pending = self._pending
        if pending is None:
            return HouseholdKnowledgeResult(
                True, "No hay ningún aprendizaje pendiente."
            )
        self._pending = None
        if pending.action is SupervisedLearningAction.STORE:
            entry = HouseholdMemoryEntry(
                title=self._title(pending.details),
                details=pending.details,
                category=self._category(pending.details),
                owner=HouseholdMemoryOwner.SHARED,
                source="supervised_conversation",
                created_at=now,
                updated_at=now,
                tags=self._tags(pending.details),
            )
            self.manager.remember(entry)
            return HouseholdKnowledgeResult(
                True, f"Aprendizaje confirmado: {entry.details}."
            )
        if pending.action is SupervisedLearningAction.UPDATE:
            updated = self.manager.update(
                pending.entry_id,
                title=self._title(pending.details),
                details=pending.details,
                tags=self._tags(pending.details),
                now=now,
            )
            return HouseholdKnowledgeResult(
                True, f"Conocimiento corregido: {updated.details}."
            )
        self.manager.archive(pending.entry_id, now=now)
        return HouseholdKnowledgeResult(
            True, f"Conocimiento archivado: {pending.title}."
        )

    def _pending_summary(self) -> str:
        assert self._pending is not None
        pending = self._pending
        if pending.action is SupervisedLearningAction.STORE:
            return f"Aprendizaje pendiente: guardar '{pending.details}'."
        if pending.action is SupervisedLearningAction.UPDATE:
            return (
                "Aprendizaje pendiente: corregir "
                f"'{pending.title}' por '{pending.details}'."
            )
        return f"Aprendizaje pendiente: archivar '{pending.title}'."

    @staticmethod
    def _category(details: str) -> HouseholdMemoryCategory:
        folded = details.casefold()
        mappings = (
            (("garantía", "garantia"), HouseholdMemoryCategory.WARRANTY),
            (
                ("médico", "medico", "doctor", "teléfono", "telefono"),
                HouseholdMemoryCategory.CONTACT,
            ),
            (
                ("service", "servicio técnico", "servicio tecnico"),
                HouseholdMemoryCategory.SERVICE,
            ),
            (
                ("mantenimiento", "cambio de aceite"),
                HouseholdMemoryCategory.MAINTENANCE,
            ),
            (("vence", "vencimiento"), HouseholdMemoryCategory.DEADLINE),
            (
                ("procedimiento", "cómo se", "como se"),
                HouseholdMemoryCategory.PROCEDURE,
            ),
        )
        for keywords, category in mappings:
            if any(keyword in folded for keyword in keywords):
                return category
        return HouseholdMemoryCategory.NOTE

    @staticmethod
    def _title(details: str) -> str:
        clean = details.strip(" .")
        return clean if len(clean) <= 72 else f"{clean[:69].rstrip()}..."

    @staticmethod
    def _tags(details: str) -> tuple[str, ...]:
        words = re.findall(r"[\wáéíóúñü]+", details.casefold())
        ignored = {"para", "como", "del", "las", "los", "una", "que", "con", "por"}
        return tuple(
            dict.fromkeys(
                word for word in words if len(word) > 3 and word not in ignored
            )
        )[:8]

    @staticmethod
    def _query(folded: str) -> str:
        for prefix in (
            "qué sabés del hogar sobre ",
            "que sabes del hogar sobre ",
            "conocimiento del hogar sobre ",
            "datos del hogar sobre ",
        ):
            if folded.startswith(prefix):
                return folded[len(prefix) :].strip(" ?.")
        return ""
