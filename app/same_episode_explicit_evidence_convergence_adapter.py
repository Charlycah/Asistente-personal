from __future__ import annotations

from datetime import datetime

from core.document_inbox import DocumentInboxManager
from core.governed_reasoning.context import ReasoningQuery


class SameEpisodeExplicitEvidenceConvergenceAdapterV1:
    """Compose explicitly admitted evidence into one governed reasoning episode."""

    def __init__(
        self,
        *,
        document_inbox: DocumentInboxManager,
        reasoning_gateway: object,
    ) -> None:
        if not hasattr(reasoning_gateway, "orchestrator") or not callable(
            getattr(reasoning_gateway, "reason", None)
        ):
            raise TypeError(
                "same-episode convergence requires governed reasoning gateway"
            )
        self._document_inbox = document_inbox
        self._reasoning_gateway = reasoning_gateway

    def admit_and_reason(
        self,
        *,
        text: str,
        owner: str,
        explicit_document_ids: tuple[str, ...],
        explicit_sources: tuple[object, ...],
        explicit_evidence_references: tuple[object, ...],
        visual_context_contribution: object | None,
        now: datetime,
    ):
        """Admit bounded evidence and invoke existing Reasoning exactly once."""
        if not (
            explicit_document_ids
            or explicit_sources
            or explicit_evidence_references
        ):
            return None
        if now.tzinfo is None:
            raise ValueError(
                "same-episode convergence timestamp must be timezone-aware"
            )
        if len(explicit_document_ids) != len(set(explicit_document_ids)):
            raise ValueError("explicit document ids must be unique")

        records = []
        for document_id in explicit_document_ids:
            if not document_id.strip():
                raise ValueError("explicit document ids must not contain blanks")
            record = self._document_inbox.repository.get(document_id)
            if record is None:
                raise KeyError(document_id)
            records.append(record)

        registry = (
            self._reasoning_gateway.orchestrator.context_assembler.evidence_registry
        )
        normalized = tuple(registry.normalize(record) for record in records)
        normalized += tuple(registry.normalize(source) for source in explicit_sources)
        references = normalized + tuple(explicit_evidence_references)
        evidence_ids = tuple(reference.evidence_id for reference in references)
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("converged evidence ids must be unique")

        for reference in explicit_evidence_references:
            registry.register_reference(reference)

        query = ReasoningQuery(
            text=text,
            owner=owner,
            evidence_ids=evidence_ids,
            as_of=now,
        )
        return self._reasoning_gateway.reason(
            query,
            now=now,
            visual_context_contribution=visual_context_contribution,
        )
