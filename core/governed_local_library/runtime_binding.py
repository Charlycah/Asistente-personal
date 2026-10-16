from __future__ import annotations

from dataclasses import dataclass

from core.knowledge_retrieval_execution import KnowledgeRetrievalArtifact
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep

from .handoff import (
    GovernedLocalDocumentRetrievalRequest,
    GovernedLocalDocumentRetrieverV1,
)


@dataclass(frozen=True)
class BoundGovernedLocalDocumentRetrieverV1:
    """One-shot bridge from one explicit library selection to one retrieval step."""

    retriever: GovernedLocalDocumentRetrieverV1
    request: GovernedLocalDocumentRetrievalRequest

    def retrieve(self, step: KnowledgeRetrievalStep) -> KnowledgeRetrievalArtifact:
        bound_step = self.request.step
        if step.step_id != bound_step.step_id:
            raise ValueError("bound retrieval step does not match")
        if step.source is not bound_step.source or step.query != bound_step.query:
            raise ValueError("bound retrieval step does not match")
        return self.retriever.retrieve_selected(self.request)
