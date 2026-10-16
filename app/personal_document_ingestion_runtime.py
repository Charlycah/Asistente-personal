from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityKind,
    CapabilityRisk,
    PermissionScope,
)
from core.document_inbox import DocumentInboxManager
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

from .document_reading import DocumentReadingService
from .personal_document_source import (
    PersonalDocumentRootDiscoveryAdapter,
    PersonalDocumentSourceCandidate,
    build_personal_document_source_from_environment,
)
from .runtime_capability_registry import OfficialRuntimeCapabilityRegistry

_CAPABILITY_NAME = "personal_documents.ingest_selected"


@dataclass(frozen=True)
class _PendingSelection:
    requested_at: datetime
    candidates: tuple[PersonalDocumentSourceCandidate, ...]


@dataclass(frozen=True)
class _PendingConfirmation:
    requested_at: datetime
    candidate: PersonalDocumentSourceCandidate


class PersonalDocumentIngestionInterceptionPort:
    """Admit explicit Owner selection before confirmed Inbox ingestion."""

    _FOLLOW_UP_TTL = timedelta(minutes=5)
    _INTENT_MARKERS = (
        "mis documentos personales",
        "documentos personales",
        "d:\\documentos",
        "d:/documentos",
    )
    _CANCEL_PHRASES = frozenset(
        {
            "cancelá la ingestión",
            "cancela la ingestión",
            "cancelar la ingestión",
        }
    )
    _CONFIRM_PHRASES = frozenset(
        {
            "confirmo",
            "confirmar",
            "confirmá",
            "si, confirmo",
            "sí, confirmo",
        }
    )

    def __init__(self, source: PersonalDocumentRootDiscoveryAdapter) -> None:
        self.source = source
        self._selections: dict[str, _PendingSelection] = {}
        self._confirmations: dict[str, _PendingConfirmation] = {}

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        session_id = request.session_id
        normalized = request.text.strip().casefold()
        confirmation = self._active_confirmation(session_id, now=now)
        selection = self._active_selection(session_id, now=now)
        if normalized in self._CANCEL_PHRASES and (
            confirmation is not None or selection is not None
        ):
            self._clear(session_id)
            return GovernedOperationalInterception(
                response_text="Cancelé la ingestión pendiente.",
                rationale="personal_document_ingestion_cancelled",
            )
        if confirmation is not None:
            if normalized not in self._CONFIRM_PHRASES:
                return None
            self._clear(session_id)
            record = self.source.ingest_selected(
                confirmation.candidate.candidate_id
            )
            return GovernedOperationalInterception(
                response_text=(
                    "Documento ingresado al Inbox: "
                    f"{confirmation.candidate.relative_path} "
                    f"[document_id={record.document_id}]."
                ),
                rationale="personal_document_ingestion_confirmed",
            )
        if selection is not None:
            candidate = self._selected_candidate(request.text, selection.candidates)
            if candidate is None:
                return None
            self._selections.pop(session_id, None)
            self._confirmations[session_id] = _PendingConfirmation(
                requested_at=now,
                candidate=candidate,
            )
            return GovernedOperationalInterception(
                response_text=(
                    f"Seleccionaste {candidate.relative_path}. "
                    "Confirmá la ingestión al Inbox o cancelá la ingestión."
                ),
                rationale="personal_document_ingestion_confirmation_required",
            )
        if not any(marker in normalized for marker in self._INTENT_MARKERS):
            return None
        query = self._query(request.text)
        discovery = self.source.discover()
        matches = self._matches(discovery.candidates, query)
        if not matches:
            return GovernedOperationalInterception(
                response_text="No encontré documentos personales coincidentes.",
                rationale="personal_document_ingestion_no_match",
            )
        self._selections[session_id] = _PendingSelection(
            requested_at=now,
            candidates=matches,
        )
        return GovernedOperationalInterception(
            response_text=self._candidate_prompt(matches),
            rationale="personal_document_ingestion_selection_required",
        )

    def _active_selection(self, session_id: str, *, now: datetime):
        pending = self._selections.get(session_id)
        if pending is None:
            return None
        if now - pending.requested_at > self._FOLLOW_UP_TTL:
            self._selections.pop(session_id, None)
            return None
        return pending

    def _active_confirmation(self, session_id: str, *, now: datetime):
        pending = self._confirmations.get(session_id)
        if pending is None:
            return None
        if now - pending.requested_at > self._FOLLOW_UP_TTL:
            self._confirmations.pop(session_id, None)
            return None
        return pending

    def _clear(self, session_id: str) -> None:
        self._selections.pop(session_id, None)
        self._confirmations.pop(session_id, None)

    @staticmethod
    def _query(text: str) -> str:
        if ":" not in text:
            return ""
        return text.split(":", 1)[1].strip().casefold()

    @staticmethod
    def _matches(candidates, query: str):
        if not query:
            return tuple(candidates)
        return tuple(
            item for item in candidates if query in item.relative_path.casefold()
        )

    @staticmethod
    def _selected_candidate(text: str, candidates):
        cleaned = text.strip()
        if cleaned.isdigit():
            index = int(cleaned) - 1
            if 0 <= index < len(candidates):
                return candidates[index]
        normalized = cleaned.casefold()
        for candidate in candidates:
            if normalized == candidate.relative_path.casefold():
                return candidate
        return None

    @staticmethod
    def _candidate_prompt(candidates) -> str:
        lines = ["Encontré estos documentos personales. Indicame cuál ingresar:"]
        for index, candidate in enumerate(candidates, start=1):
            lines.append(
                f"{index}. {candidate.relative_path} "
                f"[{candidate.suffix}, {candidate.size_bytes} bytes]"
            )
        return "\n".join(lines)


def personal_document_ingestion_descriptor() -> CapabilityDescriptor:
    return CapabilityDescriptor(
        name=_CAPABILITY_NAME,
        description=(
            "Ingestión explícita y confirmada de un documento personal al Inbox."
        ),
        kind=CapabilityKind.FILES,
        risk=CapabilityRisk.MEDIUM,
        permission_scope=PermissionScope.WRITE,
        requires_confirmation=True,
        semantic_triggers=(
            "mis documentos personales",
            "documentos personales",
            "d:\\documentos",
            "d:/documentos",
        ),
        initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL,
        effect_class=CapabilityEffectClass.STATE_CHANGING,
        interaction_scope=CapabilityInteractionScope.HUMAN,
    )


def build_personal_document_ingestion_runtime_from_environment(
    registry: OfficialRuntimeCapabilityRegistry,
    *,
    document_inbox: DocumentInboxManager | None,
    reader: DocumentReadingService,
) -> PersonalDocumentIngestionInterceptionPort | None:
    if document_inbox is None:
        return None
    try:
        source = build_personal_document_source_from_environment(
            document_inbox=document_inbox,
            reader=reader,
        )
    except (OSError, PermissionError, ValueError):
        return None
    if source is None:
        return None
    port = PersonalDocumentIngestionInterceptionPort(source)
    registry.register_descriptor(
        personal_document_ingestion_descriptor(),
        interceptor=port,
    )
    return port
