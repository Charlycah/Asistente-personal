from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from core.governed_local_library import GovernedLocalLibraryCatalogueV1
from core.governed_local_library.initiative import (
    LOCAL_LIBRARY_READ_CAPABILITY as LOCAL_LIBRARY_READ_CAPABILITY,
)
from core.governed_local_library.initiative import (
    governed_local_library_read_descriptor,
)
from core.governed_local_library.models import (
    GovernedLibraryEntry,
    GovernedLocalLibraryConfig,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

from .cognitive_evidence_local_library_bridge import (
    GovernedCognitiveEvidenceToLocalLibraryBridgeV1,
)
from .document_reading import DocumentReadingService
from .governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
)
from .governed_local_library_conversation import (
    GovernedLocalLibraryConversationStatus,
    GovernedLocalLibraryConversationV1,
    safe_local_document_filename,
)
from .governed_roby_initiated_library_access import (
    GovernedRobyInitiatedLibraryAccessV1,
)
from .knowledge_runtime import OfficialKnowledgeRuntimeGateway
from .runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from .unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)


class GovernedLocalLibraryRuntimeProvisionStatus(str, Enum):
    NOT_PROVISIONED = "not_provisioned"
    INVALID_CONFIGURATION = "invalid_configuration"
    PROVISIONED = "provisioned"


@dataclass(frozen=True)
class GovernedLocalLibraryRuntimeWiring:
    status: GovernedLocalLibraryRuntimeProvisionStatus
    configured_root: str | None
    max_catalogue_entries: int
    library: GovernedLocalLibraryCatalogueV1 | None = None
    conversation: GovernedLocalLibraryConversationV1 | None = None
    authorization_boundary: GovernedIndependenceAuthorizationBoundaryV1 | None = None
    roby_initiated: GovernedRobyInitiatedLibraryAccessV1 | None = None
    interceptor: "GovernedLocalLibraryConversationInterceptionPort | None" = None
    cognitive_bridge: GovernedCognitiveEvidenceToLocalLibraryBridgeV1 | None = None


@dataclass(frozen=True)
class _PendingLocalLibraryFollowUp:
    requested_at: datetime
    reading_requested: bool = False
    candidates: tuple[GovernedLibraryEntry, ...] = ()


class GovernedLocalLibraryConversationInterceptionPort:
    """Expose admitted user library requests through the official registry."""

    _PREFIXES = (
        "buscá en la biblioteca",
        "busca en la biblioteca",
        "consultá la biblioteca",
        "consulta la biblioteca",
        "buscá en mis libros",
        "busca en mis libros",
        "en la biblioteca",
        "biblioteca",
    )

    _FOLLOW_UP_TTL = timedelta(seconds=300)
    _CANCEL_PHRASES = (
        "cancelá la búsqueda",
        "cancela la búsqueda",
        "cancelar la búsqueda",
    )
    _UNRELATED_QUESTION_PREFIXES = (
        "qué ",
        "que ",
        "cómo ",
        "como ",
        "cuándo ",
        "cuando ",
        "dónde ",
        "donde ",
        "por qué ",
        "por que ",
    )

    def __init__(self, conversation: GovernedLocalLibraryConversationV1) -> None:
        self.conversation = conversation
        self._pending_follow_ups: dict[str, _PendingLocalLibraryFollowUp] = {}

    @staticmethod
    def _is_library_capability_question(text: str) -> bool:
        normalized = " ".join(text.casefold().strip().split())
        normalized = normalized.replace("¿", "").rstrip("?!. ")
        # Match a bounded capability question, not a document-search request.
        return (
            re.fullmatch(
                r"(?:roby[, ]+)?(?:"
                r"(?:pod[eé]s|puedes|puede|podr[ií]as|podr[ií]a)\s+"
                r"(?:tener\s+)?acceso\s+a\s+"
                r"(?:la|mi)\s+biblioteca"
                r"|(?:pod[eé]s|puedes|puede|podr[ií]as|podr[ií]a)\s+"
                r"acceder\s+a\s+(?:la|mi)\s+biblioteca"
                r"|(?:ten[eé]s|tienes|tiene)\s+acceso\s+a\s+"
                r"(?:mis\s+libros|mi\s+biblioteca|la\s+biblioteca)"
                r")",
                normalized,
            )
            is not None
        )

    @staticmethod
    def _is_library_recommendation_request(text: str) -> bool:
        normalized = " ".join(text.casefold().strip().split())
        # Explicit search remains the canonical route, including mixed requests.
        if re.search(r"\b(?:busc[aá]|buscar|consult[aá]|encontr[aá])\b", normalized):
            return False
        return (
            re.search(r"\brecomend\w*", normalized) is not None
            and re.search(
                r"\b(?:biblioteca|mis libros|mi biblioteca)\b",
                normalized,
            )
            is not None
        )

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        if self._is_library_capability_question(request.text):
            return GovernedOperationalInterception(
                response_text=(
                    "La Biblioteca local está configurada para consultas "
                    "gobernadas en esta sesión. Puedo intentar buscar un libro "
                    "o documento si me indicás cuál; eso no confirma que "
                    "cada archivo sea legible ni que una búsqueda sea completa."
                ),
                rationale="local_library_capability_status",
            )
        if self._is_library_recommendation_request(request.text):
            return GovernedOperationalInterception(
                response_text=(
                    "Puedo ayudarte a elegir una lectura, pero todavía no "
                    "tengo evidencia suficiente del catálogo para recomendarte "
                    "un libro concreto de tu Biblioteca. Indicame un género, "
                    "autor o tema y puedo intentar buscar coincidencias; "
                    "una búsqueda parcial no garantiza cobertura completa."
                ),
                rationale="local_library_recommendation_evidence_required",
            )
        pending = self._active_follow_up(request.session_id, now=now)
        if pending is not None and self._is_cancellation(request.text):
            self._pending_follow_ups.pop(request.session_id, None)
            return GovernedOperationalInterception(
                response_text="Cancelé la búsqueda pendiente en la Biblioteca.",
                rationale="local_library_clarification_cancelled",
            )

        if pending is not None and pending.candidates:
            if self._is_candidate_confirmation(request.text):
                if len(pending.candidates) != 1:
                    return self._candidate_clarification(pending.candidates)
                if pending.reading_requested:
                    return self._candidate_clarification(pending.candidates)
                candidate = pending.candidates[0]
                try:
                    validated = self.conversation.library.validate_selected_entry(
                        entry_id=candidate.entry_id,
                        source_reference=candidate.source_reference,
                    )
                    if validated.fingerprint != candidate.fingerprint:
                        raise ValueError("stale library candidate")
                except (OSError, ValueError, PermissionError):
                    self._pending_follow_ups.pop(request.session_id, None)
                    return GovernedOperationalInterception(
                        response_text=(
                            "El documento cambi? o ya no est? disponible. "
                            "Volv? a buscarlo en la Biblioteca."
                        ),
                        rationale="local_library_location_failed",
                    )
                self._pending_follow_ups.pop(request.session_id, None)
                label = safe_local_document_filename(validated.filename)
                if label is None:
                    return GovernedOperationalInterception(
                        response_text=("Encontr? un documento en tu Biblioteca."),
                        rationale="local_library_location_completed",
                    )
                return GovernedOperationalInterception(
                    response_text=f"Encontr? en tu Biblioteca: {label}.",
                    rationale="local_library_location_completed",
                )
        assessment = self.conversation.knowledge_runtime.assess(request.text)
        admitted = assessment.need.local_documents_available
        if not admitted:
            if pending is None or not self._is_compatible_follow_up(request.text):
                return None
            query = request.text.strip()
        else:
            query = self._search_query(request.text)
        if not query:
            reading_requested = (
                pending.reading_requested
                if pending is not None and not admitted
                else not self._is_location_only(request.text)
            )
            self._remember_follow_up(
                request.session_id,
                now=now,
                reading_requested=reading_requested,
            )
            return GovernedOperationalInterception(
                response_text=(
                    "Indicame qué libro o tema querés buscar en la Biblioteca."
                ),
                rationale="local_library_query_required",
            )
        # LOCALIZAR is owned by the canonical conversation, not this adapter.
        reading_requested = (
            pending.reading_requested
            if pending is not None and not admitted
            else not self._is_location_only(request.text)
        )
        if not reading_requested:
            locate = getattr(self.conversation, "locate_admitted_request", None)
            if locate is None:
                # Historical doubles cannot establish catalogue evidence.
                # Fail closed; never fall back to document content retrieval.
                return GovernedOperationalInterception(
                    response_text=(
                        "No puedo verificar la ubicación de ese documento "
                        "con la interfaz de Biblioteca disponible."
                    ),
                    rationale="local_library_location_unavailable",
                )
            result = locate(
                owner=request.owner,
                search_query=query,
                now=now,
            )
            self._pending_follow_ups.pop(request.session_id, None)
            if result.status is GovernedLocalLibraryConversationStatus.NO_MATCH:
                if result.bounded:
                    return GovernedOperationalInterception(
                        response_text=(
                            f"La búsqueda de {query!r} en la Biblioteca autorizada "
                            "fue incompleta por un límite del catálogo. "
                            "No puedo confirmar que el documento no exista."
                        ),
                        rationale="local_library_incomplete_no_match",
                    )
                return GovernedOperationalInterception(
                    response_text=(
                        f"No encontré coincidencias para {query!r} "
                        "en la Biblioteca autorizada."
                    ),
                    rationale="local_library_no_match",
                )
            if (
                result.status
                is GovernedLocalLibraryConversationStatus.NEEDS_DISAMBIGUATION
            ):
                self._remember_follow_up(
                    request.session_id,
                    now=now,
                    reading_requested=False,
                    candidates=result.candidates,
                )
                names = "\n".join(
                    f"- {safe_local_document_filename(item.filename)}"
                    for item in result.candidates
                )
                return GovernedOperationalInterception(
                    response_text=(
                        "Encontré varias coincidencias en la Biblioteca. "
                        "Indicame cuál querés consultar:\n" + names
                    ),
                    rationale="local_library_disambiguation_required",
                )
            if result.status is GovernedLocalLibraryConversationStatus.COMPLETED:
                label = safe_local_document_filename(result.safe_source_label)
                if label is None:
                    return GovernedOperationalInterception(
                        response_text="Encontré un documento en tu Biblioteca.",
                        rationale="local_library_location_completed",
                    )
                return GovernedOperationalInterception(
                    response_text=f"Encontré en tu Biblioteca: {label}.",
                    rationale="local_library_location_completed",
                )
            return GovernedOperationalInterception(
                response_text="No pude completar la búsqueda gobernada.",
                rationale="local_library_location_failed",
            )

        if admitted:
            result = self.conversation.handle_user_request(
                owner=request.owner,
                text=request.text,
                search_query=query,
                now=now,
            )
        else:
            result = self.conversation.handle_admitted_request(
                owner=request.owner,
                search_query=query,
                now=now,
            )
        if result.status is GovernedLocalLibraryConversationStatus.NO_MATCH:
            self._pending_follow_ups.pop(request.session_id, None)
            if result.bounded:
                return GovernedOperationalInterception(
                    response_text=(
                        f"La búsqueda de {result.query!r} en la Biblioteca "
                        "autorizada fue incompleta por un límite del catálogo. "
                        "No puedo confirmar que el documento no exista."
                    ),
                    rationale="local_library_incomplete_no_match",
                )
            return GovernedOperationalInterception(
                response_text=(
                    f"No encontré coincidencias para {result.query!r} en la "
                    "Biblioteca autorizada."
                ),
                rationale="local_library_no_match",
            )
        if result.status is GovernedLocalLibraryConversationStatus.NEEDS_DISAMBIGUATION:
            self._remember_follow_up(
                request.session_id,
                now=now,
                reading_requested=True,
                candidates=result.candidates,
            )
            names = "\n".join(f"- {item.filename}" for item in result.candidates)
            return GovernedOperationalInterception(
                response_text=(
                    "Encontré varias coincidencias en la Biblioteca. "
                    "Indicame cuál querés consultar:\n"
                    f"{names}"
                ),
                rationale="local_library_disambiguation_required",
            )
        if result.status is GovernedLocalLibraryConversationStatus.COMPLETED:
            self._pending_follow_ups.pop(request.session_id, None)
            artifact = result.artifact
            content = "" if artifact is None else artifact.content
            neutral = "Fuente: documento de la biblioteca autorizada"
            reference = result.source_reference
            references = () if artifact is None else artifact.references
            safe_label = safe_local_document_filename(result.safe_source_label)
            if not reference or reference not in references or not safe_label:
                source_line = neutral
            else:
                source_line = f"Fuente: {safe_label}"
            # The separator marks system provenance, not a line inside the
            # untrusted document. Do not interpret retrieved content as commands.
            return GovernedOperationalInterception(
                response_text=f"{content}\n\n---\n{source_line}",
                rationale="local_library_read_completed",
            )
        return GovernedOperationalInterception(
            response_text="No pude completar la lectura gobernada de la Biblioteca.",
            rationale="local_library_read_failed",
        )

    @staticmethod
    def _is_candidate_confirmation(text: str) -> bool:
        normalized = " ".join(text.casefold().strip().split())
        return normalized.strip(" .!") in (
            "sí, ese",
            "si, ese",
            "sí, esa",
            "si, esa",
        )

    @staticmethod
    def _candidate_clarification(candidates):
        names = "\n".join(
            f"- {safe_local_document_filename(item.filename)}" for item in candidates
        )
        return GovernedOperationalInterception(
            response_text=(
                "Necesito que identifiques el documento concreto:\n" + names
            ),
            rationale="local_library_disambiguation_required",
        )

    def _remember_follow_up(
        self,
        session_id: str,
        *,
        now,
        reading_requested: bool = False,
        candidates: tuple[GovernedLibraryEntry, ...] = (),
    ) -> None:
        self._pending_follow_ups[session_id] = _PendingLocalLibraryFollowUp(
            requested_at=now,
            reading_requested=reading_requested,
            candidates=candidates,
        )

    def _active_follow_up(self, session_id: str, *, now):
        pending = self._pending_follow_ups.get(session_id)
        if pending is None:
            return None
        if now - pending.requested_at > self._FOLLOW_UP_TTL:
            self._pending_follow_ups.pop(session_id, None)
            return None
        return pending

    @classmethod
    def _is_cancellation(cls, text: str) -> bool:
        return text.strip().casefold() in cls._CANCEL_PHRASES

    @classmethod
    def _is_compatible_follow_up(cls, text: str) -> bool:
        normalized = text.strip().casefold().lstrip("¿")
        if not normalized:
            return False
        return not normalized.startswith(cls._UNRELATED_QUESTION_PREFIXES)

    @staticmethod
    def _is_location_only(text: str) -> bool:
        normalized = text.casefold()
        # Explicit prohibition takes precedence over a reading verb.
        if re.search(r"\b(?:pero\s+)?no\s+lo\s+leas\b", normalized):
            return True
        return not bool(
            re.search(
                r"\b(?:le[eé]|lee|leelo|léelo|narr[aá]melo|narramelo|"
                r"leer|narrar|escucharlo|resum[ií]|analiz[aá]|"
                r"revis[aá]\s+el\s+contenido)\b",
                normalized,
            )
        )

    @classmethod
    def _search_query(cls, text: str) -> str:
        query = text.strip()
        normalized = query.casefold()
        # Preserve titles in direct library searches.
        direct_search = re.fullmatch(
            r"busc(?:a|\u00e1|ame|\u00e1me)\s+(.+?)"
            r"\s+en\s+(?:(?:mi|la)\s+)?biblioteca\s*[.?!]*",
            query,
            flags=re.IGNORECASE,
        )
        if direct_search is not None:
            return direct_search.group(1).strip()
        # A direct reading command can contain a trailing library locator.
        # Extract the named book before scanning generic library prefixes.
        direct_read = re.fullmatch(
            r"(?:le[eé]|lee)\s+(?:el\s+)?libro\s+(.+?)"
            r"\s+de\s+mi\s+biblioteca\s*[.?!]*",
            query,
            flags=re.IGNORECASE,
        )
        if direct_read is not None:
            return direct_read.group(1).strip()
        for prefix in cls._PREFIXES:
            index = normalized.find(prefix)
            if index >= 0:
                query = query[index + len(prefix) :]
                break
        query = re.sub(r"^[\s:,-]+", "", query).strip()
        quoted = re.search(r'["“”]([^"“”]+)["“”]', query)
        if quoted is not None:
            return quoted.group(1).strip()
        conversational_book_query = re.fullmatch(
            r"el libro\s+(.+?)\s+y\s+decime\s+cuando\s+lo\s+encontr[aá]s",
            query,
            flags=re.IGNORECASE,
        )
        if conversational_book_query is not None:
            return conversational_book_query.group(1).strip()
        # A compound request may ask about the document after naming it.
        # Keep the document title, not the subsequent reading instruction.
        compound_document_query = re.fullmatch(
            r"(?:el\s+)?(?:documento|libro)\s+(.+?)\s+y\s+"
            r"(?:decime|dime|decir(?:me)?)\s+.+",
            query,
            flags=re.IGNORECASE,
        )
        if compound_document_query is not None:
            return compound_document_query.group(1).strip()
        # Strip compound operation and negation clauses before title matching.
        query = re.sub(
            r"\s*,?\s*pero\s+no\s+lo\s+leas\s*[.?!]*$",
            "",
            query,
            flags=re.IGNORECASE,
        )
        query = re.sub(
            r"\s+y\s+(?:leelo|léelo|narr[aá]melo|narramelo)\s*[.?!]*$",
            "",
            query,
            flags=re.IGNORECASE,
        )
        query = re.sub(
            r"^(?:le[eé]|lee|léeme|leeme)\s+(?:el\s+)?libro\s+",
            "",
            query,
            count=1,
            flags=re.IGNORECASE,
        )
        query = re.sub(
            r"\s+de\s+mi\s+biblioteca\s*[.?!]*$",
            "",
            query,
            flags=re.IGNORECASE,
        )
        # Only the residual explicit-search path needs title cleanup.
        query = re.sub(
            r"^(?:el\s+)?(?:libro|documento)\s+",
            "",
            query,
            count=1,
            flags=re.IGNORECASE,
        )
        query = re.sub(
            r"^tengo\s+(?:el\s+)?libro(?:\s*[:,]\s*|\s+)",
            "",
            query,
            count=1,
            flags=re.IGNORECASE,
        )
        return query.strip().rstrip(".?! ").strip()


def build_governed_local_library_runtime_from_environment(
    knowledge_runtime: OfficialKnowledgeRuntimeGateway,
    unified_runtime: OfficialUnifiedRetrievalExecutionRuntimeGateway,
    capability_registry: OfficialRuntimeCapabilityRegistry,
) -> GovernedLocalLibraryRuntimeWiring:
    root_value = os.getenv("ROBY_LOCAL_LIBRARY_ROOT", "").strip()
    max_entries = _max_catalogue_entries_from_environment()
    if not root_value:
        return GovernedLocalLibraryRuntimeWiring(
            status=GovernedLocalLibraryRuntimeProvisionStatus.NOT_PROVISIONED,
            configured_root=None,
            max_catalogue_entries=max_entries,
        )

    configured_root = str(Path(root_value).expanduser())
    try:
        library = GovernedLocalLibraryCatalogueV1(
            GovernedLocalLibraryConfig(
                root=Path(configured_root),
                max_catalogue_entries=max_entries,
            )
        )
    except (OSError, PermissionError, ValueError):
        return GovernedLocalLibraryRuntimeWiring(
            status=GovernedLocalLibraryRuntimeProvisionStatus.INVALID_CONFIGURATION,
            configured_root=configured_root,
            max_catalogue_entries=max_entries,
        )

    conversation = GovernedLocalLibraryConversationV1(
        knowledge_runtime=knowledge_runtime,
        library=library,
        document_reader=DocumentReadingService(),
        unified_runtime=unified_runtime,
    )
    authorization_boundary = GovernedIndependenceAuthorizationBoundaryV1(
        capability_registry.manager
    )
    roby_initiated = GovernedRobyInitiatedLibraryAccessV1(
        authorization_boundary=authorization_boundary,
        library_conversation=conversation,
    )
    cognitive_bridge = GovernedCognitiveEvidenceToLocalLibraryBridgeV1(
        knowledge_runtime=knowledge_runtime,
        roby_initiated=roby_initiated,
    )
    interceptor = GovernedLocalLibraryConversationInterceptionPort(conversation)
    capability_registry.register_descriptor(
        governed_local_library_read_descriptor(),
        interceptor=interceptor,
    )
    return GovernedLocalLibraryRuntimeWiring(
        status=GovernedLocalLibraryRuntimeProvisionStatus.PROVISIONED,
        configured_root=configured_root,
        max_catalogue_entries=max_entries,
        library=library,
        conversation=conversation,
        authorization_boundary=authorization_boundary,
        roby_initiated=roby_initiated,
        interceptor=interceptor,
        cognitive_bridge=cognitive_bridge,
    )


def _max_catalogue_entries_from_environment() -> int:
    raw = os.getenv("ROBY_LOCAL_LIBRARY_MAX_CATALOGUE_ENTRIES", "").strip()
    if not raw:
        return 10_000
    try:
        value = int(raw)
    except ValueError:
        return 10_000
    return value if value > 0 else 10_000
