from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from hashlib import sha256
from time import perf_counter
from types import SimpleNamespace
from typing import Protocol

from core.governed_local_library import GovernedLocalLibraryCatalogueV1
from core.governed_local_library.conversation_selection import (
    GovernedLibraryConversationalSelectionV1,
    GovernedLibrarySelectionDisposition,
)
from core.governed_local_library.handoff import (
    GovernedLocalDocumentRetrievalRequest,
    GovernedLocalDocumentRetrieverV1,
)
from core.governed_local_library.models import GovernedLibraryEntry
from core.governed_local_library.runtime_binding import (
    BoundGovernedLocalDocumentRetrieverV1,
)
from core.governed_provider_routing import ProviderRouteStatus
from core.knowledge_retrieval_execution import (
    KnowledgeRetrievalArtifact,
    KnowledgeRetrievalExecution,
    KnowledgeRetrievalExecutionRequest,
)
from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalOrchestrator,
    KnowledgeRetrievalRequest,
)
from core.knowledge_source_policy import (
    KnowledgeSourceKind,
    KnowledgeSourceNeed,
    KnowledgeSourcePolicy,
    KnowledgeSourcePolicyRequest,
)

from .knowledge_runtime import OfficialKnowledgeRuntimeGateway
from .unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)


class _DocumentReader(Protocol):
    def read_text(self, path): ...


class GovernedLocalLibraryConversationStatus(str, Enum):
    COMPLETED = "completed"
    NO_MATCH = "no_match"
    NEEDS_DISAMBIGUATION = "needs_disambiguation"
    FAILED = "failed"


@dataclass(frozen=True)
class GovernedLocalLibraryConversationResult:
    status: GovernedLocalLibraryConversationStatus
    query: str
    candidates: tuple[GovernedLibraryEntry, ...] = ()
    bounded: bool = False
    source_reference: str | None = None
    artifact: KnowledgeRetrievalArtifact | None = None
    execution: KnowledgeRetrievalExecution | None = None
    safe_source_label: str | None = None
    last_completed_stage: str | None = None
    stage_elapsed_ms: tuple[tuple[str, float], ...] = ()


class GovernedLocalLibraryConversationV1:
    """User-initiated local-library access over existing Knowledge authorities."""

    def __init__(
        self,
        *,
        knowledge_runtime: OfficialKnowledgeRuntimeGateway,
        library: GovernedLocalLibraryCatalogueV1,
        document_reader: _DocumentReader,
        unified_runtime: OfficialUnifiedRetrievalExecutionRuntimeGateway,
        max_results: int = 5,
    ) -> None:
        if max_results <= 0:
            raise ValueError("library conversational max results must be positive")
        self.knowledge_runtime = knowledge_runtime
        self.library = library
        self.document_reader = document_reader
        self.unified_runtime = unified_runtime
        self.max_results = max_results
        self._selector = GovernedLibraryConversationalSelectionV1()

    def locate_admitted_request(
        self,
        *,
        owner: str,
        search_query: str,
        now: datetime,
    ) -> GovernedLocalLibraryConversationResult:
        """Locate via the existing catalogue/selector; never read content."""
        if now.tzinfo is None:
            raise ValueError("library conversation time must be timezone-aware")
        query = search_query.strip()
        if not query:
            raise ValueError("library search query must not be blank")
        if "/" in query or "\\" in query:
            entry = self.library.lookup_explicit_relative_path(query)
            decision = self._selector.decide_explicit(query=query, entry=entry)
            candidates = (entry,) if entry is not None else ()
        else:
            search = self.library.search(query, max_results=self.max_results)
            decision = self._selector.decide(search)
            candidates = search.matches
        if decision.disposition is GovernedLibrarySelectionDisposition.NO_MATCH:
            return GovernedLocalLibraryConversationResult(
                status=GovernedLocalLibraryConversationStatus.NO_MATCH,
                query=query,
                bounded=decision.bounded,
                last_completed_stage="selection",
            )
        if (
            decision.disposition
            is GovernedLibrarySelectionDisposition.NEEDS_DISAMBIGUATION
        ):
            return GovernedLocalLibraryConversationResult(
                status=GovernedLocalLibraryConversationStatus.NEEDS_DISAMBIGUATION,
                query=query,
                candidates=decision.candidates,
                bounded=decision.bounded,
                last_completed_stage="selection",
            )
        selection = decision.selection
        if selection is None:
            raise RuntimeError("selected library disposition requires a selection")
        entry = next(
            (
                item
                for item in candidates
                if item is not None
                and item.entry_id == selection.entry_id
                and item.source_reference == selection.source_reference
            ),
            None,
        )
        if entry is None:
            raise RuntimeError("canonical library selection lost entry identity")
        return GovernedLocalLibraryConversationResult(
            status=GovernedLocalLibraryConversationStatus.COMPLETED,
            query=query,
            source_reference=selection.source_reference,
            safe_source_label=safe_local_document_filename(entry.filename),
            last_completed_stage="selection",
        )

    def handle_user_request(
        self,
        *,
        owner: str,
        text: str,
        search_query: str,
        now: datetime,
    ) -> GovernedLocalLibraryConversationResult:
        if now.tzinfo is None:
            raise ValueError("library conversation time must be timezone-aware")
        assessment = self.knowledge_runtime.assess(text)
        if not assessment.need.local_documents_available:
            raise ValueError("conversation does not request the local library")
        return self.handle_admitted_request(
            owner=owner,
            search_query=search_query,
            now=now,
        )

    def handle_admitted_request(
        self,
        owner: str,
        search_query: str,
        now: datetime,
    ) -> GovernedLocalLibraryConversationResult:
        """Execute one already-admitted local-library request through canonical
        paths."""
        if now.tzinfo is None:
            raise ValueError("library conversation time must be timezone-aware")
        query = search_query.strip()
        if not query:
            raise ValueError("library search query must not be blank")
        need = KnowledgeSourceNeed(
            query=query,
            internal_confidence=0.0,
            local_documents_available=True,
            preferred_sources=(KnowledgeSourceKind.LOCAL_DOCUMENTS,),
        )
        search_started = perf_counter()
        # Only an unambiguous nested POSIX path takes the direct governed path.
        # Invalid path traversal must fail closed rather than become a title search.
        explicit_path = "/" in query or "\\" in query
        if explicit_path:
            entry = self.library.lookup_explicit_relative_path(query)
            search_elapsed_ms = max(0.0, (perf_counter() - search_started) * 1000)
            selection_started = perf_counter()
            selection_result = self._selector.decide_explicit(query=query, entry=entry)
            selection_elapsed_ms = max(
                0.0, (perf_counter() - selection_started) * 1000
            )
            stages = (
                ("catalogue_scan", 0.0),
                ("matching", 0.0),
                ("search", search_elapsed_ms),
                ("selection", selection_elapsed_ms),
            )
            selected_entry = entry
        else:
            search = self.library.search(query, max_results=self.max_results)
            search_elapsed_ms = max(0.0, (perf_counter() - search_started) * 1000)
            selection_started = perf_counter()
            selection_result = self._selector.decide(search)
            selection_elapsed_ms = max(
                0.0, (perf_counter() - selection_started) * 1000
            )
            stages = (
                ("catalogue_scan", search.catalogue_scan_elapsed_ms),
                ("matching", search.matching_elapsed_ms),
                ("search", search_elapsed_ms),
                ("selection", selection_elapsed_ms),
            )
            selected_entry = search.matches[0] if selection_result.selection else None
        if selection_result.disposition is GovernedLibrarySelectionDisposition.NO_MATCH:
            return GovernedLocalLibraryConversationResult(
                status=GovernedLocalLibraryConversationStatus.NO_MATCH,
                query=query,
                bounded=selection_result.bounded,
                last_completed_stage="selection",
                stage_elapsed_ms=stages,
            )
        if (
            selection_result.disposition
            is GovernedLibrarySelectionDisposition.NEEDS_DISAMBIGUATION
        ):
            return GovernedLocalLibraryConversationResult(
                status=GovernedLocalLibraryConversationStatus.NEEDS_DISAMBIGUATION,
                query=query,
                candidates=selection_result.candidates,
                bounded=selection_result.bounded,
                last_completed_stage="selection",
                stage_elapsed_ms=stages,
            )
        selection = selection_result.selection
        if selection is None:
            raise RuntimeError("selected library disposition requires a selection")
        planning_started = perf_counter()
        plan = self._build_local_plan(
            owner=owner,
            query=query,
            need=need,
            now=now,
        )
        if len(plan.steps) != 1:
            raise ValueError("local library conversation requires exactly one step")
        step = plan.steps[0]
        request = GovernedLocalDocumentRetrievalRequest(
            step=step,
            selection=selection,
        )
        retriever = GovernedLocalDocumentRetrieverV1(
            library=self.library,
            document_reader=self.document_reader,
        )
        bound = BoundGovernedLocalDocumentRetrieverV1(
            retriever=retriever,
            request=request,
        )
        planning_elapsed_ms = max(0.0, (perf_counter() - planning_started) * 1000)
        retrieval_started = perf_counter()
        execution = self.unified_runtime.execute(
            KnowledgeRetrievalExecutionRequest(owner=owner, plan=plan),
            now=now,
            execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
        )
        retrieval_elapsed_ms = max(0.0, (perf_counter() - retrieval_started) * 1000)
        stages += (
            ("planning", planning_elapsed_ms),
            ("retrieval", retrieval_elapsed_ms),
        )
        artifact = execution.steps[0].artifact if execution.steps else None
        status = (
            GovernedLocalLibraryConversationStatus.COMPLETED
            if artifact is not None
            else GovernedLocalLibraryConversationStatus.FAILED
        )
        # The single selected catalogue entry is the same identity handed to
        # the canonical retriever, which validates it before reading.
        label = None
        if (
            artifact is not None
            and selected_entry is not None
            and selected_entry.entry_id == selection.entry_id
            and selected_entry.source_reference == selection.source_reference
            and selection.source_reference in artifact.references
        ):
            label = safe_local_document_filename(selected_entry.filename)
        return GovernedLocalLibraryConversationResult(
            status=status,
            query=query,
            source_reference=selection.source_reference,
            artifact=artifact,
            execution=execution,
            safe_source_label=label,
            last_completed_stage="retrieval",
            stage_elapsed_ms=stages,
        )

    @staticmethod
    def _build_local_plan(*, owner: str, query: str, need, now: datetime):
        # Local documents require no provider route. This context exists only to
        # let the existing KnowledgeSourcePolicy remain the source authority.
        route_request = SimpleNamespace(owner=owner)
        route = SimpleNamespace(
            request=route_request,
            status=ProviderRouteStatus.NO_PROVIDER_REQUIRED,
            route_id=sha256(f"local-library|{owner.casefold()}".encode()).hexdigest(),
        )
        local_need = replace(
            need,
            query=query,
            explicit_external_request=False,
            local_documents_available=True,
            preferred_sources=(KnowledgeSourceKind.LOCAL_DOCUMENTS,),
        )
        source = KnowledgeSourcePolicy().decide(
            KnowledgeSourcePolicyRequest(
                owner=owner,
                provider_route=route,
                need=local_need,
            ),
            now=now,
        )
        return KnowledgeRetrievalOrchestrator().orchestrate(
            KnowledgeRetrievalRequest(owner=owner, source_decision=source),
            now=now,
        )


def safe_local_document_filename(filename: str | None) -> str | None:
    """Conservative display-only label; never derive from a technical reference."""
    if not isinstance(filename, str) or not filename or len(filename) > 160:
        return None
    if filename != filename.strip() or filename in {".", ".."}:
        return None
    if any(
        unicodedata.category(character).startswith("C") or character in '/\\<>|:*?"`'
        for character in filename
    ):
        return None
    if re.search(r"[\r\n]", filename):
        return None
    return filename
