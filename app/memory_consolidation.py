from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.memory import MemoryItem, MemoryQuery, MemoryStore
from core.memory_runtime_integration import MemoryRuntimeIntegration

if TYPE_CHECKING:
    from .approved_learning_memory_write_adapter import GovernedMemoryWriteRequest
    from .governed_knowledge_revision_request import GovernedKnowledgeRevisionRequest


@dataclass(frozen=True)
class GovernedLearningTemporalIntrospectionView:
    memory_id: int
    content: str
    category: str
    confidence: float
    created_at: str
    metadata: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class OfficialMemoryStatus:
    owner: str
    stored_count: int
    persistent: bool = True


class OfficialMemoryGateway(MemoryStore):
    """Single operational door over ROBY's official persistent memory runtime."""

    _STATUS_TRIGGERS = (
        "estado de tu memoria",
        "estado de la memoria",
        "cuántos recuerdos tenés",
        "cuantos recuerdos tenes",
        "qué recordás de mí",
        "que recordas de mi",
    )
    _REMEMBER_PREFIXES = (
        "recordá que ",
        "recorda que ",
        "recuerda que ",
    )
    _PROFILE_PREFIXES = (
        "recordá sobre ",
        "recorda sobre ",
        "recuerda sobre ",
    )
    _MEMORY_SUBJECTS = {
        "carlos": "Carlos",
        "cristina": "Cristina",
    }

    def __init__(
        self,
        runtime: MemoryRuntimeIntegration,
        *,
        owner: str,
        household_timezone: str | None = None,
    ) -> None:
        self.runtime = runtime
        self.owner = owner.strip()
        if not self.owner:
            raise ValueError("official memory owner must not be blank")
        configured_timezone = household_timezone
        if configured_timezone is None:
            configured_timezone = os.getenv(
                "ROBY_HOUSEHOLD_TIMEZONE",
                "America/Argentina/Buenos_Aires",
            )
        self.household_timezone = configured_timezone.strip()
        if not self.household_timezone:
            raise ValueError("household timezone must not be blank")

    def remember(self, item: MemoryItem) -> None:
        self.runtime.store_explicit(
            owner=self.owner,
            text=item.content,
            metadata={str(key): str(value) for key, value in item.metadata.items()},
        )

    def remember_governed_learning(
        self,
        request: GovernedMemoryWriteRequest,
    ):
        if request.writer_authority != "memory_gateway":
            raise ValueError("governed learning request targets wrong authority")
        if request.writer_component != "OfficialMemoryGateway":
            raise ValueError("governed learning request targets wrong component")
        if request.writer_method != "remember_governed_learning":
            raise ValueError("governed learning request targets wrong writer method")
        if not request.semantic_mapping_supported:
            raise ValueError("governed learning semantic mapping must be certified")
        if not request.idempotent_write_supported:
            raise ValueError("governed learning idempotency must be certified")
        if request.write_performed:
            raise ValueError("governed learning request was already marked written")

        metadata = {
            str(key): str(value) for key, value in request.memory_item.metadata.items()
        }
        metadata["write_request_id"] = request.request_id
        metadata["idempotency_key"] = request.idempotency_key
        metadata["writer_method"] = request.writer_method
        return self.runtime.store_governed_learning(
            owner=self.owner,
            text=request.memory_item.content,
            confidence=float(metadata["confidence"]),
            metadata=metadata,
            idempotency_key=request.idempotency_key,
            learning_category=request.learning_category,
        )

    def apply_governed_knowledge_revision(
        self,
        request: GovernedKnowledgeRevisionRequest,
    ) -> tuple[int, bool]:
        if request.writer_authority != "memory_gateway":
            raise ValueError("governed revision request targets wrong authority")
        if request.writer_component != "OfficialMemoryGateway":
            raise ValueError("governed revision request targets wrong component")
        if request.writer_method != "apply_governed_knowledge_revision":
            raise ValueError("governed revision request targets wrong writer method")
        if request.target_owner != self.owner:
            raise ValueError("governed revision request targets wrong owner")
        if not request.requires_official_memory_gateway:
            raise ValueError("governed revision requires official Memory gateway")
        if not request.requires_atomic_revision:
            raise ValueError("governed revision must be atomic")
        if not request.preserves_prior_version:
            raise ValueError("governed revision must preserve prior version")
        if request.write_performed or request.memory_modified:
            raise ValueError("governed revision request was already marked executed")

        return self.runtime.apply_governed_knowledge_revision(
            owner=self.owner,
            target_memory_id=request.target_memory_id,
            target_category=request.target_category,
            expected_current_content=request.expected_current_content,
            expected_target_fingerprint=request.expected_target_fingerprint,
            replacement_content=request.replacement_content,
            replacement_idempotency_key=request.replacement_idempotency_key,
            revision_request_id=request.request_id,
            revision_proposal_id=request.revision_proposal_id,
            revision_approval_id=request.revision_approval_id,
            application_proposal_id=request.application_proposal_id,
            corrective_evidence_ids=request.corrective_evidence_ids,
            revision_proposal_fingerprint=request.revision_proposal_fingerprint,
            human_approval_fingerprint=request.human_approval_fingerprint,
            application_proposal_fingerprint=(
                request.application_proposal_fingerprint
            ),
        )

    def governed_learning_temporal_introspection(
        self,
        *,
        created_at_from: str,
        created_at_before: str,
        limit: int = 20,
    ) -> tuple[GovernedLearningTemporalIntrospectionView, ...]:
        records = self.runtime.governed_learning_temporal_introspection(
            owner=self.owner,
            created_at_from=created_at_from,
            created_at_before=created_at_before,
            limit=limit,
        )
        return tuple(
            GovernedLearningTemporalIntrospectionView(
                memory_id=record.id,
                content=record.content,
                category=record.category.value,
                confidence=record.confidence,
                created_at=record.created_at,
                metadata=tuple(sorted(record.metadata.items())),
            )
            for record in records
        )

    def recall(self, query: MemoryQuery) -> list[MemoryItem]:
        records = self.runtime.search(
            owner=self.owner,
            query=query.text,
            limit=int(query.metadata.get("limit", self.runtime.config.recall_limit)),
            active_only=True,
        )
        return [
            MemoryItem(
                content=record.content,
                metadata={
                    "memory_id": record.id,
                    "category": record.category.value,
                    "confidence": record.confidence,
                },
            )
            for record in records
        ]

    def status(self) -> OfficialMemoryStatus:
        return OfficialMemoryStatus(
            owner=self.owner,
            stored_count=self.runtime.count(owner=self.owner),
        )

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        normalized = " ".join(request.text.strip().casefold().split())
        learned = self._intercept_governed_learning_temporal(
            request,
            normalized,
            now=now,
        )
        if learned is not None:
            return learned
        advanced = self._intercept_advanced(request, normalized, now=now)
        if advanced is not None:
            return advanced
        for prefix in self._REMEMBER_PREFIXES:
            if normalized.startswith(prefix):
                content = request.text.strip()[len(prefix) :].strip()
                if not content:
                    return GovernedOperationalInterception(
                        response_text="Decime qué querés que recuerde.",
                        rationale="official_memory_explicit_content_missing",
                    )
                result = self.runtime.store_explicit(
                    owner=request.owner,
                    text=content,
                    metadata={"source": "explicit_conversation"},
                )
                return GovernedOperationalInterception(
                    response_text=(
                        "Lo guardé en la memoria personal oficial."
                        if result.stored_count
                        else "No pude guardar ese recuerdo."
                    ),
                    rationale="official_memory_explicit_store_completed",
                )
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            count = self.runtime.count(owner=request.owner)
            records = self.runtime.search(owner=request.owner, query=None, limit=5)
            if not records:
                response = (
                    "La memoria personal oficial está activa y todavía no tiene "
                    "recuerdos."
                )
            else:
                lines = [
                    f"Memoria personal oficial activa. Recuerdos almacenados: {count}.",
                    "Recuerdos recientes:",
                    *(f"- {record.content}" for record in records),
                ]
                response = "\n".join(lines)
            return GovernedOperationalInterception(
                response_text=response,
                rationale="official_memory_inspection_completed",
            )
        return None

    def _intercept_governed_learning_temporal(
        self,
        request: GovernedConversationPipelineRequest,
        normalized: str,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        period = None
        if "qué aprendiste hoy" in normalized or "que aprendiste hoy" in normalized:
            period = "today"
        elif "qué aprendiste ayer" in normalized or "que aprendiste ayer" in normalized:
            period = "yesterday"
        if period is None:
            return None
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("conversation now must be timezone-aware")

        household_zone = self._household_tzinfo()
        local_now = now.astimezone(household_zone)
        local_day = local_now.date()
        if period == "yesterday":
            local_day -= timedelta(days=1)
        start_local = datetime.combine(
            local_day,
            datetime.min.time(),
            tzinfo=household_zone,
        )
        end_local = start_local + timedelta(days=1)
        created_at_from = start_local.astimezone(UTC).isoformat()
        created_at_before = end_local.astimezone(UTC).isoformat()

        records = self.runtime.governed_learning_temporal_introspection(
            owner=self.owner,
            created_at_from=created_at_from,
            created_at_before=created_at_before,
            limit=20,
        )
        rationale = (
            "governed_learning_temporal_today_inspection"
            if period == "today"
            else "governed_learning_temporal_yesterday_inspection"
        )
        label = "hoy" if period == "today" else "ayer"
        if not records:
            return GovernedOperationalInterception(
                response_text=(
                    f"No tengo aprendizajes gobernados durables registrados {label}."
                ),
                rationale=rationale,
            )

        lines = [f"Aprendizajes gobernados durables registrados {label}:"]
        lines.extend(f"- {record.content}" for record in records)
        return GovernedOperationalInterception(
            response_text="\n".join(lines),
            rationale=rationale,
        )

    def _household_tzinfo(self):
        if self.household_timezone == "UTC":
            return UTC
        if self.household_timezone == "America/Argentina/Buenos_Aires":
            return timezone(timedelta(hours=-3), name=self.household_timezone)
        try:
            return ZoneInfo(self.household_timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(
                "household timezone is unavailable in this runtime"
            ) from exc

    def _intercept_advanced(self, request, normalized: str, *, now):
        del now
        if normalized.startswith(self._PROFILE_PREFIXES):
            raw = request.text.strip()
            prefix = next(
                item for item in self._PROFILE_PREFIXES if normalized.startswith(item)
            )
            remainder = raw[len(prefix) :].strip()
            if ":" not in remainder:
                return GovernedOperationalInterception(
                    response_text=(
                        "Usá el formato: recordá sobre Cristina: prefiere té."
                    ),
                    rationale="advanced_personal_memory_format_missing",
                )
            profile, content = (part.strip() for part in remainder.split(":", 1))
            if not profile or not content:
                return GovernedOperationalInterception(
                    response_text="Indicame la persona y el recuerdo.",
                    rationale="advanced_personal_memory_content_missing",
                )
            subject = self._memory_subject(profile)
            if subject is None:
                return GovernedOperationalInterception(
                    response_text=(
                        "Solo puedo atribuir recuerdos a Carlos o a Cristina."
                    ),
                    rationale="advanced_personal_memory_subject_rejected",
                )
            result = self.runtime.store_explicit(
                owner=request.owner,
                text=content,
                metadata={
                    "source": "explicit_profile_conversation",
                    "subject": subject,
                    "recorded_by": request.owner,
                    "status": "active",
                    "recorded_at": datetime.now(UTC).isoformat(),
                },
            )
            return GovernedOperationalInterception(
                response_text=(
                    f"Lo guardé como un recuerdo sobre {subject}."
                    if result.stored_count
                    else "No pude guardar ese recuerdo."
                ),
                rationale="advanced_personal_memory_profile_store_completed",
            )

        for prefix in ("qué recordás sobre ", "que recordas sobre "):
            if normalized.startswith(prefix):
                profile = request.text.strip()[len(prefix) :].strip(" ?.!")
                subject = self._memory_subject(profile)
                if subject is None:
                    return GovernedOperationalInterception(
                        response_text=(
                            "Solo puedo consultar recuerdos atribuidos a Carlos "
                            "o a Cristina."
                        ),
                        rationale="advanced_personal_memory_subject_rejected",
                    )
                records = self.runtime.search(
                    owner=request.owner,
                    query=None,
                    limit=50,
                )
                active = [
                    item
                    for item in records
                    if item.metadata.get("status", "active") != "archived"
                    and item.metadata.get("subject", "").strip().casefold()
                    == subject.casefold()
                ]
                if not active:
                    text = f"No tengo recuerdos activos sobre {subject}."
                else:
                    lines = [f"Recuerdos activos sobre {subject}:"]
                    lines.extend(
                        f"- #{item.id}: {item.content} (origen: "
                        f"{item.metadata.get('source', 'desconocido')})"
                        for item in active
                    )
                    text = "\n".join(lines)
                return GovernedOperationalInterception(
                    response_text=text,
                    rationale="advanced_personal_memory_profile_inspection",
                )

        for prefix in ("corregí recuerdo ", "corregi recuerdo "):
            if normalized.startswith(prefix):
                remainder = request.text.strip()[len(prefix) :].strip()
                if ":" not in remainder:
                    return GovernedOperationalInterception(
                        response_text="Usá: corregí recuerdo 12: nuevo contenido.",
                        rationale="advanced_personal_memory_correction_format_missing",
                    )
                raw_id, content = (part.strip() for part in remainder.split(":", 1))
                if not raw_id.isdigit() or not content:
                    return GovernedOperationalInterception(
                        response_text="Indicame un identificador y el nuevo contenido.",
                        rationale="advanced_personal_memory_correction_invalid",
                    )
                updated = self.runtime.private_store(request.owner).update_content(
                    int(raw_id),
                    content,
                    metadata={
                        "corrected_by": request.owner,
                        "corrected_at": datetime.now(UTC).isoformat(),
                    },
                )
                return GovernedOperationalInterception(
                    response_text=(
                        "Recuerdo corregido."
                        if updated
                        else "No encontré ese recuerdo en tu memoria personal."
                    ),
                    rationale="advanced_personal_memory_correction_completed",
                )

        for prefix in ("archivá recuerdo ", "archiva recuerdo "):
            if normalized.startswith(prefix):
                raw_id = request.text.strip()[len(prefix) :].strip(" .")
                archived = raw_id.isdigit() and self.runtime.private_store(
                    request.owner
                ).archive(int(raw_id))
                return GovernedOperationalInterception(
                    response_text=(
                        "Recuerdo archivado; ya no se mostrará como activo."
                        if archived
                        else "No encontré ese recuerdo en tu memoria personal."
                    ),
                    rationale="advanced_personal_memory_archive_completed",
                )
        return None

    @classmethod
    def _memory_subject(cls, value: str) -> str | None:
        return cls._MEMORY_SUBJECTS.get(value.strip().casefold())
