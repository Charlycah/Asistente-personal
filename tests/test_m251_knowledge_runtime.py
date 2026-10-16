from datetime import datetime, timezone

from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.knowledge_source_policy import KnowledgeSourceKind


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m251",
        text=text,
    )


def test_current_information_is_classified_for_external_sources():
    need = OfficialKnowledgeRuntimeGateway().describe(
        _request("Dame las noticias actuales de hoy")
    )
    assert need.current_information_required
    assert need.internal_confidence == 0.2
    assert need.preferred_sources == (
        KnowledgeSourceKind.NEWS,
        KnowledgeSourceKind.WEB,
    )


def test_verification_is_classified_without_authorizing_network():
    need = OfficialKnowledgeRuntimeGateway().describe(
        _request("Verificá este dato con fuentes externas")
    )
    assert need.verification_required
    assert need.explicit_external_request
    assert need.preferred_sources[0] is KnowledgeSourceKind.OFFICIAL_DOCUMENTATION


def test_local_documents_are_preferred_when_explicitly_requested():
    need = OfficialKnowledgeRuntimeGateway().describe(
        _request("Revisá mis documentos locales sobre ROBY")
    )
    assert need.local_documents_available
    assert need.preferred_sources == (KnowledgeSourceKind.LOCAL_DOCUMENTS,)


def test_source_assessment_is_available_through_official_registry(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    registry = build_runtime_root().dependencies.official_capability_registry
    result = registry.intercept(
        _request("Evaluá las fuentes para: noticias actuales de ROBY"),
        now=datetime.now(timezone.utc),
    )
    assert result is not None
    assert result.rationale == "official_knowledge_source_assessment_completed"
    assert "news, web" in result.response_text
    assert "no autoriza" in result.response_text.casefold()


def test_registry_exposes_governed_knowledge_capability(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    assert "knowledge.governed_sources" in registry.capability_names
    registration = next(
        item
        for item in registry.registrations
        if item.descriptor.name == "knowledge.governed_sources"
    )
    assert root.dependencies.knowledge_need_port is registration.interceptor
    assert not root.config.retrieval_enabled
