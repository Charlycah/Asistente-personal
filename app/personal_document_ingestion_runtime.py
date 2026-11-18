from __future__ import annotations

import re
import unicodedata
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
from core.governed_operational_conversation_pipeline.response_origin import (
    ResponseConfidence,
    ResponseOrigin,
    ResponseOriginMetadata,
)
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
        self._selected_documents: dict[tuple[str, str], tuple[str, str]] = {}
        self._located_documents: dict[tuple[str, str], tuple] = {}

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        session_id = request.session_id
        normalized = request.text.strip().casefold()
        location_query = self._location_query(request.text)
        if location_query is not None:
            discovery = self.source.discover(query=location_query)
            key = (request.owner.casefold(), session_id)
            self._selected_documents.pop(key, None)
            self._located_documents[key] = discovery.candidates
            if not discovery.candidates:
                return GovernedOperationalInterception(
                    response_text=(
                        f"No encontré coincidencias para {location_query!r} "
                        "en tus Documentos."
                    ),
                    rationale="personal_document_location_no_match",
                )
            paths = "\n".join(
                f"- {candidate.relative_path}"
                for candidate in discovery.candidates
            )
            suffix = (
                "\nHay más coincidencias que las mostradas."
                if discovery.truncated else ""
            )
            return GovernedOperationalInterception(
                response_text=f"Encontré en tus Documentos:\n{paths}{suffix}",
                rationale="personal_document_location_completed",
            )
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
            record = self.source.ingest_selected(confirmation.candidate.candidate_id)
            self._located_documents.pop((request.owner.casefold(), session_id), None)
            self._selected_documents[(request.owner.casefold(), session_id)] = (
                record.document_id,
                record.metadata.title,
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
        # DG_FIX_02_DOCUMENT_CONTAINMENT
        evidence = self.located_document_content(request)
        if evidence is not None:
            status = evidence.get("status")
            messages = {
                "changed": (
                    "El documento cambi? desde que fue localizado. "
                    "No puedo citar su contenido anterior con seguridad. "
                    "Volv? a localizarlo para consultar la versi?n actual."
                ),
                "empty": (
                    "El documento localizado no contiene texto legible. "
                    "No puedo extraer ni citar su contenido."
                ),
                "unavailable": (
                    "No pude verificar el contenido del documento localizado. "
                    "No voy a inventar citas ni resultados. "
                    "Pod?s volver a localizarlo."
                ),
                "selection_required": (
                    "Hay varios documentos localizados. "
                    "Indic? cu?l quer?s consultar antes de citar su contenido."
                ),
            }
            if status in messages:
                return GovernedOperationalInterception(
                    response_text=messages[status],
                    rationale=(
                        "personal_document_content_"
                        + status
                        + "_withheld"
                    ),
                    origin=ResponseOriginMetadata(
                        origin=ResponseOrigin.LOCAL,
                        confidence=ResponseConfidence.WITHHELD,
                        freshness="unavailable",
                        verifiable=False,
                        abstained=True,
                    ),
                    network_access_performed=False,
                )
        # END_DG_FIX_02_DOCUMENT_CONTAINMENT

        if not any(marker in normalized for marker in self._INTENT_MARKERS):
            return None
        query = self._query(request.text)
        discovery = self.source.discover(query=query)
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

    def located_document_content(self, request):
        """Read the located file only when this session asks about its content."""
        candidates = self._located_documents.get(
            (request.owner.casefold(), request.session_id)
        )
        if candidates is None:
            return None
        # DG_FIX_01_DOCUMENT_REFERENCE
        text = unicodedata.normalize("NFKD", request.text.casefold())
        text = "".join(
            ch for ch in text
            if not unicodedata.combining(ch)
        )

        if re.search(
            r"\b(?:cambiemos de tema|hablemos de otra cosa|"
            r"pasemos a otro tema|ahora hablemos de)\b",
            text
        ):
            return None

        refers = re.search(
            r"\b(?:(?:ese|este|el)\s+(?:mismo\s+)?|"
            r"(?:del|al)\s+(?:mismo\s+)?|mismo\s+)"
            r"(?:documento|archivo|informe|estudio)\b",
            text
        )

        named = any(
            "".join(
                ch for ch in unicodedata.normalize(
                    "NFKD",
                    candidate.relative_path.rsplit("/", 1)[-1]
                    .rsplit(".", 1)[0].casefold()
                )
                if not unicodedata.combining(ch)
            ) in text
            for candidate in candidates
        )

        asks_content = re.search(
            r"\b(?:leer|lee|leelo|copia|copiame|decime|decirme|"
            r"indicame|indica|resultado|muestra|metodo|fecha|"
            r"analisis|contenido|resumi|resumen|explicame|"
            r"que dice|que contiene|que menciona|"
            r"cuanto mide|que indica|que informa|"
            r"menciona|hallazgos|fragmento)\b",
            text
        )

        if not (refers or named) or not asks_content:
            return None
        # END_DG_FIX_01_DOCUMENT_REFERENCE
        if len(candidates) != 1:
            return {"status": "selection_required", "candidates": [
                item.relative_path for item in candidates
            ]}
        candidate = candidates[0]
        try:
            path = self.source._validated_source(candidate.relative_path)
            refreshed = self.source._candidate_for(path)
            if refreshed is None or refreshed.candidate_id != candidate.candidate_id:
                return {"status": "changed", "source_name": candidate.relative_path}
            content = self.source.reader.read_text(path)
            if not content.strip():
                return {"status": "empty", "source_name": candidate.relative_path}
            return {"source_name": candidate.relative_path, "content": content}
        except (OSError, ValueError, RuntimeError) as error:
            return {"status": "unavailable", "error_type": type(error).__name__}

    def selected_document_ids(
        self, request: GovernedConversationPipelineRequest
    ) -> tuple[str, ...]:
        """Resolve a reference to the document confirmed in this owner/session."""
        selected = self._selected_documents.get(
            (request.owner.casefold(), request.session_id)
        )
        if selected is None:
            return ()
        document_id, title = selected
        normalized = " ".join(request.text.casefold().split())
        normalized_title = " ".join(title.casefold().split())
        refers_to_selected = normalized_title in normalized or re.search(
            r"\b(?:ese documento|este documento|el documento anterior|"
            r"el documento seleccionado|el documento ingresado|"
            r"(?:el|del) documento que (?:acabamos de ingresar|ingresamos))\b",
            normalized,
        )
        return (document_id,) if refers_to_selected else ()

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
    def _location_query(text: str) -> str | None:
        command = re.sub(
            r"^\s*(?:hola\s+)?roby\b[\s,:]*",
            "",
            text,
            count=1,
            flags=re.IGNORECASE,
        ).strip().lstrip("¿").strip()
        match = re.fullmatch(
            r"(?:(?:pod[eé]s|puedes)\s+decirme\s+si\s+)?"
            r"(?:tengo|tenemos|hay)\s+en\s+mis\s+documentos"
            r"(?:\s+personales)?\s+"
            r"(?:(?:el|un)\s+)?(?:archivo|documento)\s*[:,]?\s*"
            r"(?P<title>.+?)\s*[?!.]*",
            command,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        title = match.group("title").strip().strip('\"“”')
        return title or None

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
            "mis documentos",
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
