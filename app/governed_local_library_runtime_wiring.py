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
from core.governed_local_library.models import GovernedLocalLibraryConfig
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

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        pending = self._active_follow_up(request.session_id, now=now)
        if pending is not None and self._is_cancellation(request.text):
            self._pending_follow_ups.pop(request.session_id, None)
            return GovernedOperationalInterception(
                response_text="Cancelé la búsqueda pendiente en la Biblioteca.",
                rationale="local_library_clarification_cancelled",
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
            self._remember_follow_up(request.session_id, now=now)
            return GovernedOperationalInterception(
                response_text=(
                    "Indicame qué libro o tema querés buscar en la Biblioteca."
                ),
                rationale="local_library_query_required",
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
            self._remember_follow_up(request.session_id, now=now)
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

    def _remember_follow_up(self, session_id: str, *, now) -> None:
        self._pending_follow_ups[session_id] = _PendingLocalLibraryFollowUp(
            requested_at=now
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

    @classmethod
    def _search_query(cls, text: str) -> str:
        query = text.strip()
        normalized = query.casefold()
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
        return query


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
