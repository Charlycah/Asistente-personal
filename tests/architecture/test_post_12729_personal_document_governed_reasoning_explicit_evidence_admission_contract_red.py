from __future__ import annotations

import hashlib
import importlib
from datetime import datetime, timezone
from pathlib import Path

from core.document_inbox import DocumentInboxManager, InMemoryDocumentRepository
from core.governed_reasoning.context import ReasoningQuery
from core.governed_reasoning.evidence import EvidenceRegistry, EvidenceSourceType

ROOT = Path(__file__).resolve().parents[2]
CONVERSATION_GATEWAY = ROOT / "app" / "official_conversation_gateway.py"
REASONING_RUNTIME = ROOT / "app" / "governed_reasoning_runtime.py"
REASONING_RUNTIME_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)
ADAPTER_MODULE = "app.personal_document_reasoning_admission_adapter"


def _adapter_class():
    try:
        module = importlib.import_module(ADAPTER_MODULE)
    except ModuleNotFoundError as exc:
        raise AssertionError(
            "POST-12.729 protected-surface RED: bounded Personal Document reasoning "
            "admission adapter is not implemented outside protected runtimes"
        ) from exc
    return module.PersonalDocumentReasoningAdmissionAdapterV1


class _ContextAssembler:
    def __init__(self, evidence_registry: EvidenceRegistry) -> None:
        self.evidence_registry = evidence_registry


class _Orchestrator:
    def __init__(self, evidence_registry: EvidenceRegistry) -> None:
        self.context_assembler = _ContextAssembler(evidence_registry)


class _ReasoningGateway:
    def __init__(self, evidence_registry: EvidenceRegistry) -> None:
        self.orchestrator = _Orchestrator(evidence_registry)
        self.queries: list[ReasoningQuery] = []

    def reason(self, query: ReasoningQuery, *, now=None):
        self.queries.append(query)
        return query


class _ExactOnlyRepository(InMemoryDocumentRepository):
    def __init__(self) -> None:
        super().__init__()
        self.requested_ids: list[str] = []
        self.bulk_reads = 0

    def get(self, document_id: str):
        self.requested_ids.append(document_id)
        return super().get(document_id)

    def list_all(self):
        self.bulk_reads += 1
        raise AssertionError(
            "explicit document admission must never bulk-read documents"
        )


def _fixture():
    repository = _ExactOnlyRepository()
    inbox = DocumentInboxManager(repository=repository)
    document = inbox.ingest_text(
        "contenido documental seleccionado explícitamente",
        title="Documento seleccionado",
        now=datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc),
    )
    registry = EvidenceRegistry()
    gateway = _ReasoningGateway(registry)
    return repository, inbox, document, registry, gateway


def test_post_12729_protected_runtime_surfaces_remain_byte_identical() -> None:
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source
    assert hashlib.sha256(REASONING_RUNTIME.read_bytes()).hexdigest() == (
        REASONING_RUNTIME_SHA256
    )


def test_post_12729_bounded_external_admission_adapter_exists() -> None:
    adapter = _adapter_class()
    assert adapter.__module__ == ADAPTER_MODULE


def test_post_12729_explicit_selection_uses_exact_document_lookup_only() -> None:
    adapter_type = _adapter_class()
    repository, inbox, document, _, gateway = _fixture()
    adapter = adapter_type(document_inbox=inbox, reasoning_gateway=gateway)

    adapter.admit_and_reason(
        text="razoná con este documento",
        owner="Carlos",
        explicit_document_ids=(document.document_id,),
        now=datetime(2026, 9, 20, 12, 1, tzinfo=timezone.utc),
    )

    assert repository.requested_ids == [document.document_id]
    assert repository.bulk_reads == 0


def test_post_12729_selected_document_uses_canonical_registry_normalization() -> None:
    adapter_type = _adapter_class()
    _, inbox, document, registry, gateway = _fixture()
    adapter = adapter_type(document_inbox=inbox, reasoning_gateway=gateway)

    adapter.admit_and_reason(
        text="razoná con este documento",
        owner="Carlos",
        explicit_document_ids=(document.document_id,),
        now=datetime(2026, 9, 20, 12, 1, tzinfo=timezone.utc),
    )

    references = registry.list_all()
    assert len(references) == 1
    assert references[0].normalized_source_type is EvidenceSourceType.DOCUMENT
    assert references[0].source_id == document.document_id


def test_post_12729_reasoning_query_carries_only_admitted_evidence_ids() -> None:
    adapter_type = _adapter_class()
    _, inbox, document, registry, gateway = _fixture()
    adapter = adapter_type(document_inbox=inbox, reasoning_gateway=gateway)

    adapter.admit_and_reason(
        text="razoná con este documento",
        owner="Carlos",
        explicit_document_ids=(document.document_id,),
        now=datetime(2026, 9, 20, 12, 1, tzinfo=timezone.utc),
    )

    reference = registry.list_all()[0]
    assert len(gateway.queries) == 1
    assert gateway.queries[0].evidence_ids == (reference.evidence_id,)
    assert gateway.queries[0].text == "razoná con este documento"


def test_post_12729_absent_selection_does_not_admit_or_reason() -> None:
    adapter_type = _adapter_class()
    repository, inbox, _, registry, gateway = _fixture()
    repository.requested_ids.clear()
    adapter = adapter_type(document_inbox=inbox, reasoning_gateway=gateway)

    result = adapter.admit_and_reason(
        text="conversación ordinaria",
        owner="Carlos",
        explicit_document_ids=(),
        now=datetime(2026, 9, 20, 12, 1, tzinfo=timezone.utc),
    )

    assert result is None
    assert repository.requested_ids == []
    assert repository.bulk_reads == 0
    assert registry.list_all() == ()
    assert gateway.queries == []


def test_post_12729_unknown_explicit_document_is_rejected_without_reasoning() -> None:
    adapter_type = _adapter_class()
    repository, inbox, _, registry, gateway = _fixture()
    repository.requested_ids.clear()
    adapter = adapter_type(document_inbox=inbox, reasoning_gateway=gateway)

    try:
        adapter.admit_and_reason(
            text="razoná con este documento",
            owner="Carlos",
            explicit_document_ids=("documento-inexistente",),
            now=datetime(2026, 9, 20, 12, 1, tzinfo=timezone.utc),
        )
    except (KeyError, ValueError):
        pass
    else:
        raise AssertionError("unknown explicit document id must be rejected")

    assert repository.requested_ids == ["documento-inexistente"]
    assert repository.bulk_reads == 0
    assert registry.list_all() == ()
    assert gateway.queries == []
