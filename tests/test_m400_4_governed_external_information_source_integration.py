from pathlib import Path

import pytest

from app.governed_external_information_source_integration import (
    GovernedExternalInformationSourceIntegration,
)
from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryStatus
from app.nasa_governed_source import NasaGovernedSourceAdapter
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic
from core.governed_external_intelligence import (
    ExternalExecutionScope,
    ExternalIntelligenceCapability,
    ExternalIntelligenceRequest,
    ExternalIntelligenceStatus,
)
from tests.test_m344_2_nasa_governed_source import nasa_payload


class Runtime:
    pass


def _request(target_id: str = "nasa") -> ExternalIntelligenceRequest:
    return ExternalIntelligenceRequest(
        request_id=f"source-{target_id}",
        owner="Carlos",
        capability=ExternalIntelligenceCapability.INFORMATION_SOURCE,
        purpose="admit governed external information as subordinate evidence",
        target_id=target_id,
    )


def _query() -> GovernedSourceQuery:
    return GovernedSourceQuery(
        source_id="nasa",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
        query_text="Artemis",
        limit=2,
    )


def _nasa_result():
    gateway = OfficialConversationGateway(Runtime())
    gateway._nasa_governed_source_adapter = NasaGovernedSourceAdapter(
        transport=lambda _url, _timeout: nasa_payload()
    )
    gateway.enable_nasa_governed_source()
    return gateway.execute_governed_source_query(_query())


def test_m400_4_admits_successful_nasa_query_as_information_evidence() -> None:
    result = _nasa_result()
    envelope = GovernedExternalInformationSourceIntegration().admit_query_result(
        _request(),
        result,
        execution_scope=ExternalExecutionScope.REMOTE,
        network_used=True,
    )
    assert result.status is GovernedSourceQueryStatus.SUCCEEDED
    assert envelope.status is ExternalIntelligenceStatus.ACCEPTED
    assert envelope.information is not None
    assert envelope.inference is None
    assert envelope.information.source_id == "nasa"
    assert envelope.information.source_status == "succeeded"
    assert envelope.information.source_error is None
    assert envelope.information.items[0]["external_id"] == "ARTEMIS-001"
    assert envelope.provenance.actor_id == "nasa"
    assert envelope.provenance.execution_scope is ExternalExecutionScope.REMOTE
    assert envelope.provenance.network_used is True
    assert envelope.cognitive_authority_granted is False


def test_m400_4_source_integration_does_not_execute_or_enable_source() -> None:
    source = Path(
        "app/governed_external_information_source_integration.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        ".execute(",
        "enable_nasa_governed_source",
        "register_governed_source_query_adapter",
        "NasaGovernedSourceAdapter(",
        "urlopen",
        "requests.",
    ):
        assert forbidden not in source


def test_m400_4_requires_executed_query_result() -> None:
    gateway = OfficialConversationGateway(Runtime())
    prepared = gateway.prepare_governed_source_query(_query())
    with pytest.raises(ValueError, match="executed query result"):
        GovernedExternalInformationSourceIntegration().admit_query_result(
            _request(),
            prepared,
            network_used=False,
        )


def test_m400_4_rejects_target_source_mismatch() -> None:
    result = _nasa_result()
    with pytest.raises(ValueError, match="target must match governed source"):
        GovernedExternalInformationSourceIntegration().admit_query_result(
            _request("other"),
            result,
            network_used=True,
        )


def test_m400_4_requires_information_source_capability() -> None:
    result = _nasa_result()
    request = ExternalIntelligenceRequest(
        request_id="wrong-capability",
        owner="Carlos",
        capability="inference_provider",
        purpose="wrong family",
        target_id="nasa",
    )
    with pytest.raises(ValueError, match="information source capability"):
        GovernedExternalInformationSourceIntegration().admit_query_result(
            request,
            result,
            network_used=True,
        )


def test_m400_4_preserves_empty_result_without_inventing_information() -> None:
    class EmptyAdapter:
        def execute(self, _query):
            return ()

    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", EmptyAdapter())
    result = gateway.execute_governed_source_query(_query())
    envelope = GovernedExternalInformationSourceIntegration().admit_query_result(
        _request(),
        result,
        network_used=False,
    )
    assert result.status is GovernedSourceQueryStatus.EMPTY
    assert envelope.status is ExternalIntelligenceStatus.ACCEPTED
    assert envelope.information is not None
    assert envelope.information.items == ()
    assert envelope.information.source_status == "empty"
    assert envelope.information.source_error is None


def test_m400_4_preserves_failed_query_as_rejected_source_evidence() -> None:
    class FailingAdapter:
        def execute(self, _query):
            raise RuntimeError("boom")

    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", FailingAdapter())
    result = gateway.execute_governed_source_query(_query())
    envelope = GovernedExternalInformationSourceIntegration().admit_query_result(
        _request(),
        result,
        network_used=True,
    )
    assert result.status is GovernedSourceQueryStatus.FAILED
    assert envelope.status is ExternalIntelligenceStatus.REJECTED
    assert envelope.information is not None
    assert envelope.information.items == ()
    assert envelope.information.source_status == "failed"
    assert envelope.information.source_error == "adapter_failure"
    assert envelope.cognitive_authority_granted is False


def test_m400_4_network_use_remains_explicit_provenance() -> None:
    result = _nasa_result()
    envelope = GovernedExternalInformationSourceIntegration().admit_query_result(
        _request(),
        result,
        execution_scope=ExternalExecutionScope.REMOTE,
        network_used=False,
    )
    assert envelope.provenance.execution_scope is ExternalExecutionScope.REMOTE
    assert envelope.provenance.network_used is False


def test_m400_4_integration_has_no_cognitive_authority() -> None:
    integration = GovernedExternalInformationSourceIntegration()
    assert integration.integration_id == (
        "external_intelligence_information_source_integration"
    )
    assert not hasattr(integration, "authority_id")
    for forbidden in (
        "fetch",
        "execute",
        "enable_source",
        "select_source",
        "decide",
        "plan",
        "remember",
        "mutate",
    ):
        assert not hasattr(integration, forbidden)


def test_m400_4_keeps_information_source_separate_from_provider_inference() -> None:
    result = _nasa_result()
    envelope = GovernedExternalInformationSourceIntegration().admit_query_result(
        _request(),
        result,
        network_used=True,
    )
    assert envelope.request.capability is (
        ExternalIntelligenceCapability.INFORMATION_SOURCE
    )
    assert envelope.information is not None
    assert envelope.inference is None


def test_m400_4_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M400_4_GOVERNED_EXTERNAL_INFORMATION_SOURCE_INTEGRATION.md"
    ).read_text(encoding="utf-8")
    assert "source execution → external evidence envelope" in document
    assert "NASA es una fuente, no un LLM provider" in document
    assert "capacidad/evidencia externa ≠ autoridad cognitiva" in document
    assert "no ejecuta ni habilita fuentes" in document
    assert "Milestone M400.4 — Governed External Information Source Integration" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M400.4 — Governed External Information Source Integration" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M400.4 — Regla de integración gobernada de fuentes externas" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
