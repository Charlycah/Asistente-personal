from pathlib import Path

import pytest

from app.governed_external_information_source_integration import (
    GovernedExternalInformationSourceIntegration,
)
from app.nasa_governed_source import NasaGovernedSourceAdapter
from app.official_conversation_gateway import OfficialConversationGateway
from core.governed_external_intelligence import (
    ExternalIntelligenceRequest,
    ExternalVerificationStatus,
    GovernedExternalIntelligenceVerifier,
)
from tests.test_m344_2_nasa_governed_source import (
    nasa_payload,
    nasa_query,
)


class Runtime:
    pass


def _gateway() -> OfficialConversationGateway:
    gateway = OfficialConversationGateway(Runtime())
    gateway._nasa_governed_source_adapter = NasaGovernedSourceAdapter(
        transport=lambda _url, _timeout: nasa_payload()
    )
    gateway.enable_nasa_governed_source()
    return gateway


def _request() -> ExternalIntelligenceRequest:
    return ExternalIntelligenceRequest(
        request_id="trace-nasa",
        owner="Carlos",
        capability="information_source",
        purpose="verify governed source execution lineage",
        target_id="nasa",
    )


def test_m400_6_executed_source_result_has_sha256_execution_id() -> None:
    result = _gateway().execute_governed_source_query(nasa_query())
    assert len(result.execution_id) == 64
    int(result.execution_id, 16)


def test_m400_6_observation_preserves_same_execution_id() -> None:
    gateway = _gateway()
    result = gateway.execute_governed_source_query(nasa_query())
    observation = gateway.governed_source_query_observations[-1]
    assert observation.execution_id == result.execution_id


def test_m400_6_prepared_query_has_no_execution_trace() -> None:
    gateway = OfficialConversationGateway(Runtime())
    result = gateway.prepare_governed_source_query(nasa_query())
    assert result.execution_id == ""


def test_m400_6_prepared_result_cannot_claim_execution_id() -> None:
    prepared = OfficialConversationGateway(Runtime()).prepare_governed_source_query(
        nasa_query()
    )
    with pytest.raises(ValueError, match="prepared governed source query"):
        type(prepared)(
            query=prepared.query,
            source=prepared.source,
            status=prepared.status,
            response=None,
            execution_id="a" * 64,
        )


def test_m400_6_traced_admission_carries_source_execution_id() -> None:
    result = _gateway().execute_governed_source_query(nasa_query())
    envelope = GovernedExternalInformationSourceIntegration().admit_traced_query_result(
        _request(),
        result,
        network_used=True,
    )
    assert envelope.provenance.trace_ids == (result.execution_id,)


def test_m400_6_traced_source_becomes_provenance_verified() -> None:
    result = _gateway().execute_governed_source_query(nasa_query())
    envelope = GovernedExternalInformationSourceIntegration().admit_traced_query_result(
        _request(),
        result,
        network_used=True,
    )
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assert verification.status is ExternalVerificationStatus.VERIFIED
    assert "source_execution_trace_is_not_available" not in verification.limitations
    assert verification.truth_certified is False


def test_m400_6_untraced_m400_4_admission_remains_limited() -> None:
    result = _gateway().execute_governed_source_query(nasa_query())
    envelope = GovernedExternalInformationSourceIntegration().admit_query_result(
        _request(),
        result,
        network_used=True,
    )
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assert verification.status is ExternalVerificationStatus.LIMITED
    assert "source_execution_trace_is_not_available" in verification.limitations


def test_m400_6_traced_admission_rejects_non_executed_result() -> None:
    prepared = OfficialConversationGateway(Runtime()).prepare_governed_source_query(
        nasa_query()
    )
    with pytest.raises(ValueError, match="source execution trace"):
        GovernedExternalInformationSourceIntegration().admit_traced_query_result(
            _request(),
            prepared,
            network_used=False,
        )


def test_m400_6_executor_keeps_existing_authority() -> None:
    gateway = _gateway()
    assert gateway.governed_source_query_executor.authority.endswith(
        ":OfficialConversationGateway"
    )
    source = Path("app/governed_source_query_executor.py").read_text(encoding="utf-8")
    assert "class GovernedSourceQueryExecutor" in source
    assert "ExternalSourceExecutionTraceManager" not in source


def test_m400_6_trace_does_not_certify_truth_or_add_authority() -> None:
    result = _gateway().execute_governed_source_query(nasa_query())
    envelope = GovernedExternalInformationSourceIntegration().admit_traced_query_result(
        _request(),
        result,
        network_used=True,
    )
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assert verification.truth_certified is False
    assert verification.cognitive_authority_granted is False


def test_m400_6_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M400_6_GOVERNED_EXTERNAL_SOURCE_EXECUTION_TRACE.md"
    ).read_text(encoding="utf-8")
    assert "execution trace ≠ verdad certificada" in document
    assert "OfficialConversationGateway" in document
    assert "execution_id" in document
    assert "admit_traced_query_result" in document
    assert "Milestone M400.6 — Governed External Source Execution Trace" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M400.6 — Governed External Source Execution Trace" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M400.6 — Regla de trace de ejecución de fuentes externas" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
