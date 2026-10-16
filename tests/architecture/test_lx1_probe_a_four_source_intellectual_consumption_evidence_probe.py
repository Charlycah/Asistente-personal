from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

from app.same_episode_explicit_evidence_convergence_adapter import (
    SameEpisodeExplicitEvidenceConvergenceAdapterV1,
)
from core.governed_reasoning.context import ReasoningQuery


@dataclass(frozen=True)
class _Reference:
    evidence_id: str


class _Repository:
    def __init__(self, document: object) -> None:
        self.document = document
        self.get_calls: list[str] = []

    def get(self, document_id: str) -> object | None:
        self.get_calls.append(document_id)
        if document_id == "explicit-document":
            return self.document
        return None


class _Registry:
    def __init__(self, mapping: dict[object, _Reference]) -> None:
        self.mapping = mapping
        self.registered: list[_Reference] = []

    def normalize(self, source: object) -> _Reference:
        return self.mapping[source]

    def register_reference(
        self,
        reference: _Reference,
        *,
        source: object | None = None,
    ) -> _Reference:
        self.registered.append(reference)
        return reference


class _ReasoningGateway:
    def __init__(self, registry: _Registry) -> None:
        self.orchestrator = SimpleNamespace(
            context_assembler=SimpleNamespace(evidence_registry=registry)
        )
        self.calls: list[tuple[ReasoningQuery, dict[str, object]]] = []

    def reason(self, query: ReasoningQuery, **kwargs: object) -> object:
        self.calls.append((query, kwargs))
        return SimpleNamespace(query=query, kwargs=kwargs)


def test_probe_a_four_sources_are_consumed_by_one_reasoning_deliberation() -> None:
    document = object()
    governed_source = object()
    visual_context = object()
    document_reference = _Reference("document-evidence")
    source_reference = _Reference("source-evidence")
    explicit_reference = _Reference("reference-evidence")
    registry = _Registry(
        {
            document: document_reference,
            governed_source: source_reference,
        }
    )
    repository = _Repository(document)
    gateway = _ReasoningGateway(registry)
    adapter = SameEpisodeExplicitEvidenceConvergenceAdapterV1(
        document_inbox=SimpleNamespace(repository=repository),
        reasoning_gateway=gateway,
    )

    result = adapter.admit_and_reason(
        text="Compare the four admitted evidence channels in one answer.",
        owner="Carlos",
        explicit_document_ids=("explicit-document",),
        explicit_sources=(governed_source,),
        explicit_evidence_references=(explicit_reference,),
        visual_context_contribution=visual_context,
        now=datetime(2026, 10, 3, 17, 45, tzinfo=timezone.utc),
    )

    assert result is not None
    assert repository.get_calls == ["explicit-document"]
    assert registry.registered == [explicit_reference]
    assert len(gateway.calls) == 1
    query, kwargs = gateway.calls[0]
    assert query.evidence_ids == (
        "document-evidence",
        "source-evidence",
        "reference-evidence",
    )
    assert kwargs["visual_context_contribution"] is visual_context
