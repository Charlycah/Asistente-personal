from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.document_reading import DocumentReadingService
from app.personal_document_ingestion_runtime import (
    PersonalDocumentIngestionInterceptionPort,
    personal_document_ingestion_descriptor,
)
from app.personal_document_source import PersonalDocumentRootDiscoveryAdapter
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.document_inbox import (
    DocumentInboxManager,
    InMemoryDocumentRepository,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.governed_operational_conversation_pipeline.response_origin import (
    ResponseConfidence,
    ResponseDecision,
    ResponseVerification,
)
from core.runtime_composition_root.root import RuntimeCompositionRoot
from tests.test_m178_runtime_composition_root import dependencies


NOW = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)


def _runtime(tmp_path, content):
    document = tmp_path / "informe-sintetico.txt"
    document.write_text(content, encoding="utf-8")

    inbox = DocumentInboxManager(InMemoryDocumentRepository())
    source = PersonalDocumentRootDiscoveryAdapter(
        root=tmp_path,
        reader=DocumentReadingService(),
        document_inbox=inbox,
    )
    port = PersonalDocumentIngestionInterceptionPort(source)

    registry = OfficialRuntimeCapabilityRegistry()
    registry.register_descriptor(
        personal_document_ingestion_descriptor(),
        interceptor=port,
    )

    configured = replace(
        dependencies(),
        document_inbox=inbox,
        official_capability_registry=registry,
        operational_interceptor=registry,
    )
    pipeline = RuntimeCompositionRoot(configured).build()
    return pipeline, port, document, inbox


def _request(text, session="dg-fix-02"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session,
        text=text,
    )


def _locate(pipeline):
    result = pipeline.process(
        _request(
            "ROBY, tengo en mis documentos el archivo "
            "informe-sintetico.txt?"
        ),
        now=NOW,
    )
    assert result.response_path.name == "INTERCEPTOR"


def _assert_abstention(result):
    assert result.provider_call_performed is False
    assert result.response_path.name == "INTERCEPTOR"
    assert result.response_origin.abstained is True
    assert result.response_origin.confidence is ResponseConfidence.WITHHELD
    assert result.response_origin.verifiable is False

    record = result.response_origin.confidence_record
    assert record.evidence_count == 0
    assert record.verification is ResponseVerification.UNAVAILABLE
    assert record.decision is ResponseDecision.ABSTAINED


def test_changed_document_is_contained(tmp_path):
    pipeline, port, document, inbox = _runtime(
        tmp_path,
        "Primera oraci?n. Segunda oraci?n: EVIDENCIA_ANTERIOR.",
    )
    _locate(pipeline)

    document.write_text(
        "Primera oraci?n. Segunda oraci?n: EVIDENCIA_NUEVA."
        "\nCAMBIO_POSTERIOR_A_LOCALIZACION.",
        encoding="utf-8",
    )

    query = _request(
        "Del mismo documento, copia literalmente la segunda oraci?n."
    )
    assert port.located_document_content(query)["status"] == "changed"

    result = pipeline.process(query, now=NOW)
    _assert_abstention(result)
    assert len(inbox.repository.list_all()) == 0


def test_unavailable_document_is_contained(tmp_path):
    pipeline, port, document, inbox = _runtime(
        tmp_path,
        "",
    )
    _locate(pipeline)

    query = _request(
        "Del mismo documento, copia literalmente la segunda oraci?n."
    )
    assert port.located_document_content(query)["status"] == "unavailable"

    result = pipeline.process(query, now=NOW)
    _assert_abstention(result)
    assert len(inbox.repository.list_all()) == 0


def test_valid_document_reaches_provider(tmp_path):
    pipeline, port, document, inbox = _runtime(
        tmp_path,
        "Primera oraci?n. Segunda oraci?n: EVIDENCIA_VALIDA_0202.",
    )
    _locate(pipeline)

    query = _request(
        "Del mismo documento, copia literalmente la segunda oraci?n."
    )
    evidence = port.located_document_content(query)
    assert "EVIDENCIA_VALIDA_0202" in evidence["content"]

    result = pipeline.process(query, now=NOW)
    assert result.provider_call_performed is True
    assert result.response_path.name == "PROVIDER"
    assert len(inbox.repository.list_all()) == 0


@pytest.mark.parametrize(
    "text",
    (
        "Explic? qu? es una funci?n de Python.",
        "?Qu? es un documento PDF?",
        "Cambiemos de tema. Explic? los bucles de Python.",
    ),
)
def test_general_conversation_remains_available(tmp_path, text):
    pipeline, port, document, inbox = _runtime(
        tmp_path,
        "Primera oraci?n. Segunda oraci?n: EVIDENCIA_VALIDA.",
    )
    _locate(pipeline)

    result = pipeline.process(_request(text), now=NOW)
    assert result.provider_call_performed is True
    assert result.response_path.name == "PROVIDER"
    assert len(inbox.repository.list_all()) == 0
