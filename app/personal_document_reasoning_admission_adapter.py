from __future__ import annotations

from datetime import datetime

from core.document_inbox import DocumentInboxManager
from core.governed_reasoning.context import ReasoningQuery


class PersonalDocumentReasoningAdmissionAdapterV1:
    """Admit explicitly selected Personal Documents into governed Reasoning."""

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
                "personal document admission requires governed reasoning gateway"
            )
        self._document_inbox = document_inbox
        self._reasoning_gateway = reasoning_gateway

    def admit_and_reason(
        self,
        *,
        text: str,
        owner: str,
        explicit_document_ids: tuple[str, ...],
        now: datetime,
    ):
        """Normalize only explicitly selected documents and reason once with them."""
        if not explicit_document_ids:
            return None
        if now.tzinfo is None:
            raise ValueError(
                "personal document admission timestamp must be timezone-aware"
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
        references = tuple(registry.normalize(record) for record in records)
        query = ReasoningQuery(
            text=text,
            owner=owner,
            evidence_ids=tuple(reference.evidence_id for reference in references),
            as_of=now,
        )
        return self._reasoning_gateway.reason(query, now=now)
