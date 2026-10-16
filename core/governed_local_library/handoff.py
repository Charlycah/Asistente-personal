from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core.knowledge_retrieval_execution import KnowledgeRetrievalArtifact
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep
from core.knowledge_source_policy import KnowledgeSourceKind

from .catalogue import GovernedLocalLibraryCatalogueV1
from .models import GovernedLibraryEntry


class _DocumentReader(Protocol):
    def read_text(self, path: Path) -> str: ...


@dataclass(frozen=True)
class GovernedLibrarySelection:
    """Explicit, provenance-preserving selection from a library search result."""

    query: str
    entry_id: str
    source_reference: str
    catalogue_fingerprint: str = ""
    explicit_entry_fingerprint: str = ""

    def __post_init__(self) -> None:
        query = self.query.strip()
        entry_id = self.entry_id.strip()
        source_reference = self.source_reference.strip()
        catalogue_fingerprint = self.catalogue_fingerprint.strip()
        explicit_entry_fingerprint = self.explicit_entry_fingerprint.strip()
        if not query:
            raise ValueError("library selection query must not be blank")
        if not entry_id:
            raise ValueError("library selection entry id must not be blank")
        if not source_reference:
            raise ValueError("library selection source reference must not be blank")
        if bool(catalogue_fingerprint) == bool(explicit_entry_fingerprint):
            raise ValueError("selection requires exactly one provenance fingerprint")
        object.__setattr__(self, "query", query)
        object.__setattr__(self, "entry_id", entry_id)
        object.__setattr__(self, "source_reference", source_reference)
        object.__setattr__(self, "catalogue_fingerprint", catalogue_fingerprint)
        object.__setattr__(
            self, "explicit_entry_fingerprint", explicit_entry_fingerprint
        )


@dataclass(frozen=True)
class GovernedLocalDocumentRetrievalRequest:
    """Joins one canonical retrieval step to one explicit library selection."""

    step: KnowledgeRetrievalStep
    selection: GovernedLibrarySelection

    def __post_init__(self) -> None:
        if self.step.source is not KnowledgeSourceKind.LOCAL_DOCUMENTS:
            raise ValueError("local document handoff requires LOCAL_DOCUMENTS")
        if self.step.query != self.selection.query:
            raise ValueError("library selection query must match retrieval step query")


class GovernedLocalDocumentRetrieverV1:
    """Acquire one explicitly selected local document as a Knowledge artifact."""

    def __init__(
        self,
        *,
        library: GovernedLocalLibraryCatalogueV1,
        document_reader: _DocumentReader,
    ) -> None:
        self._library = library
        self._document_reader = document_reader

    def retrieve_selected(
        self,
        request: GovernedLocalDocumentRetrievalRequest,
    ) -> KnowledgeRetrievalArtifact:
        entry = self._validate_selection(request.selection)
        if (
            request.selection.explicit_entry_fingerprint
            and entry.fingerprint != request.selection.explicit_entry_fingerprint
        ):
            raise ValueError("explicit library selection identity is stale")
        path = self._library.resolve_entry(entry.relative_path)
        content = self._document_reader.read_text(path)
        return KnowledgeRetrievalArtifact(
            source=KnowledgeSourceKind.LOCAL_DOCUMENTS,
            query=request.step.query,
            content=content,
            references=(entry.source_reference,),
        )

    def _validate_selection(
        self,
        selection: GovernedLibrarySelection,
    ) -> GovernedLibraryEntry:
        validator = getattr(self._library, "validate_selected_entry", None)
        if validator is None:
            delegate = getattr(self._library, "delegate", None)
            if isinstance(delegate, GovernedLocalLibraryCatalogueV1):
                validator = delegate.validate_selected_entry
        if validator is None:
            raise TypeError("library collaborator does not expose canonical validation")
        return validator(
            entry_id=selection.entry_id,
            source_reference=selection.source_reference,
        )
