from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.document_reading import DocumentReadingService
from app.personal_document_source import PersonalDocumentRootDiscoveryAdapter
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import (
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    PermissionScope,
)
from core.document_inbox import (
    DocumentInboxManager,
    InMemoryDocumentRepository,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

MODULE = "app.personal_document_ingestion_runtime"
CAPABILITY = "personal_documents.ingest_selected"
NOW = datetime(2026, 10, 4, 18, 0, tzinfo=timezone.utc)


def _runtime_module():
    return importlib.import_module(MODULE)


def _request(text: str, session_id: str = "owner-session"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        text=text,
        session_id=session_id,
    )


def _source(tmp_path: Path):
    inbox = DocumentInboxManager(InMemoryDocumentRepository())
    reader = DocumentReadingService()
    source = PersonalDocumentRootDiscoveryAdapter(
        root=tmp_path,
        reader=reader,
        document_inbox=inbox,
    )
    return source, inbox


def test_contract_exports_port_builder_and_descriptor():
    module = _runtime_module()
    assert module.PersonalDocumentIngestionInterceptionPort
    assert module.build_personal_document_ingestion_runtime_from_environment
    assert module.personal_document_ingestion_descriptor


def test_descriptor_declares_confirmed_human_state_change():
    descriptor = _runtime_module().personal_document_ingestion_descriptor()
    assert descriptor.name == CAPABILITY
    assert descriptor.permission_scope == PermissionScope.WRITE
    assert descriptor.effect_class == CapabilityEffectClass.STATE_CHANGING
    assert descriptor.interaction_scope == CapabilityInteractionScope.HUMAN
    assert descriptor.initiation_policy == CapabilityInitiationPolicy.HUMAN_APPROVAL
    assert descriptor.requires_confirmation is True


def test_only_explicit_personal_document_source_intent_is_admitted(tmp_path):
    module = _runtime_module()
    (tmp_path / "plan.md").write_text("owner plan", encoding="utf-8")
    source, _ = _source(tmp_path)
    port = module.PersonalDocumentIngestionInterceptionPort(source)
    assert port.intercept(_request("buscá un documento"), now=NOW) is None
    assert port.intercept(_request("buscá archivos de ROBY"), now=NOW) is None
    admitted = port.intercept(
        _request("consultá mis documentos personales: plan"),
        now=NOW,
    )
    assert admitted is not None


def test_discovery_and_selection_do_not_ingest_before_confirmation(tmp_path):
    module = _runtime_module()
    (tmp_path / "plan-a.md").write_text("alpha", encoding="utf-8")
    (tmp_path / "plan-b.md").write_text("beta", encoding="utf-8")
    source, inbox = _source(tmp_path)
    port = module.PersonalDocumentIngestionInterceptionPort(source)
    first = port.intercept(
        _request("consultá mis documentos personales: plan"),
        now=NOW,
    )
    assert first is not None
    assert inbox.repository.list_all() == ()
    selected = port.intercept(_request("2"), now=NOW)
    assert selected is not None
    assert "confirm" in selected.response_text.casefold()
    assert inbox.repository.list_all() == ()


def test_confirmation_is_session_scoped_and_one_shot(tmp_path):
    module = _runtime_module()
    (tmp_path / "plan.md").write_text("owner plan", encoding="utf-8")
    source, inbox = _source(tmp_path)
    port = module.PersonalDocumentIngestionInterceptionPort(source)
    port.intercept(
        _request("consultá mis documentos personales: plan"),
        now=NOW,
    )
    port.intercept(_request("1"), now=NOW)
    assert port.intercept(_request("confirmo", "other"), now=NOW) is None
    confirmed = port.intercept(_request("confirmo"), now=NOW)
    assert confirmed is not None
    assert len(inbox.repository.list_all()) == 1
    assert port.intercept(_request("confirmo"), now=NOW) is None
    assert len(inbox.repository.list_all()) == 1


def test_confirmation_expires_and_can_be_cancelled(tmp_path):
    module = _runtime_module()
    (tmp_path / "plan.md").write_text("owner plan", encoding="utf-8")
    source, inbox = _source(tmp_path)
    port = module.PersonalDocumentIngestionInterceptionPort(source)
    port.intercept(
        _request("consultá mis documentos personales: plan"),
        now=NOW,
    )
    port.intercept(_request("1"), now=NOW)
    cancelled = port.intercept(_request("cancelá la ingestión"), now=NOW)
    assert cancelled is not None
    assert port.intercept(_request("confirmo"), now=NOW) is None
    port.intercept(
        _request("consultá mis documentos personales: plan"),
        now=NOW,
    )
    port.intercept(_request("1"), now=NOW)
    late = NOW + timedelta(minutes=6)
    assert port.intercept(_request("confirmo"), now=late) is None
    assert inbox.repository.list_all() == ()


def test_presentation_exposes_safe_relative_metadata_only(tmp_path):
    module = _runtime_module()
    nested = tmp_path / "private"
    nested.mkdir()
    (nested / "plan.md").write_text("secret body", encoding="utf-8")
    source, _ = _source(tmp_path)
    port = module.PersonalDocumentIngestionInterceptionPort(source)
    response = port.intercept(
        _request("consultá mis documentos personales: plan"),
        now=NOW,
    )
    assert response is not None
    assert "private/plan.md" in response.response_text
    assert str(tmp_path) not in response.response_text
    assert "personal-document:" not in response.response_text
    assert "secret body" not in response.response_text


def test_builder_registers_only_when_personal_documents_root_is_configured(
    tmp_path,
    monkeypatch,
):
    module = _runtime_module()
    registry = OfficialRuntimeCapabilityRegistry()
    inbox = DocumentInboxManager(InMemoryDocumentRepository())
    reader = DocumentReadingService()
    monkeypatch.delenv("ROBY_PERSONAL_DOCUMENTS_ROOT", raising=False)
    assert (
        module.build_personal_document_ingestion_runtime_from_environment(
            registry,
            document_inbox=inbox,
            reader=reader,
        )
        is None
    )
    assert CAPABILITY not in registry.capability_names
    monkeypatch.setenv("ROBY_PERSONAL_DOCUMENTS_ROOT", str(tmp_path))
    runtime = module.build_personal_document_ingestion_runtime_from_environment(
        registry,
        document_inbox=inbox,
        reader=reader,
    )
    assert runtime is not None
    assert CAPABILITY in registry.capability_names
    assert runtime.source.document_inbox is inbox


def test_runtime_root_wires_same_canonical_document_inbox_instance():
    module = _runtime_module()
    import app.runtime_root_factory as root_factory

    source = inspect.getsource(root_factory.build_runtime_root)
    assert "build_personal_document_ingestion_runtime_from_environment" in source
    assert "document_inbox=document_inbox" in source
    assert module.personal_document_ingestion_descriptor().name in CAPABILITY


def test_guardrail_source_remains_only_ingestion_handoff_owner():
    import app.personal_document_source as source_module

    source = inspect.getsource(source_module.PersonalDocumentRootDiscoveryAdapter)
    assert "self.document_inbox.ingest_text" in source
    assert "Reasoning" not in source
    assert "KnowledgeRuntime" not in source
    assert "proposal_generation" not in source


def test_guardrail_reasoning_admission_still_requires_explicit_document_ids():
    import app.personal_document_reasoning_admission_adapter as admission_module

    source = inspect.getsource(admission_module)
    assert "explicit_document_ids" in source


def test_guardrail_official_registry_remains_the_interception_authority():
    import app.runtime_capability_registry as registry_module

    source = inspect.getsource(registry_module.OfficialRuntimeCapabilityRegistry)
    assert "def register_descriptor" in source
    assert "def intercept" in source
