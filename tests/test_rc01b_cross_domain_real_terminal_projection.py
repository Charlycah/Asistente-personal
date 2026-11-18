"""Real executor projection tests; no producer authentication is claimed."""

from dataclasses import replace

import pytest

from app.cross_domain_governed_terminal_evidence import (
    GovernedTerminalStatus,
    terminal_evidence_from_result,
)
from app.governed_conversational_query import (
    GovernedConversationalQuery,
    GovernedConversationalQueryStatus,
)
from app.governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryStatus,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


class SuccessfulAdapter:
    def execute(self, query):
        return (
            {
                "external_id": "ARTEMIS-001",
                "title": "Artemis",
            },
        )


class EmptyAdapter:
    def execute(self, query):
        return ()


class FailedAdapter:
    def execute(self, query):
        raise RuntimeError("local adapter failure")


class InvalidItemAdapter:
    def execute(self, query):
        return ({"external_id": "missing-title"},)


def query(*, topics=None):
    return GovernedSourceQuery(
        source_id="nasa",
        topics=(
            frozenset({InterestTopic.NASA_MISSIONS})
            if topics is None
            else topics
        ),
        query_text="Artemis",
    )


def gateway(adapter=None):
    instance = OfficialConversationGateway(Runtime())
    if adapter is not None:
        instance.register_governed_source_query_adapter("nasa", adapter)
    return instance


def test_real_success_projection():
    instance = gateway(SuccessfulAdapter())
    result = instance.execute_governed_source_query(query())

    assert result.status is GovernedSourceQueryStatus.SUCCEEDED
    assert result.response is not None

    evidence = terminal_evidence_from_result(result)
    assert evidence is not None
    assert evidence.status is GovernedTerminalStatus.SUCCEEDED
    assert evidence.source_id == "nasa"
    assert evidence.execution_id == result.execution_id
    assert len(evidence.execution_id) == 64
    assert evidence.item_count == 1
    assert evidence.response_present is True
    assert evidence.producer_verified is False


def test_real_empty_projection():
    instance = gateway(EmptyAdapter())
    result = instance.execute_governed_source_query(query())

    assert result.status is GovernedSourceQueryStatus.EMPTY
    evidence = terminal_evidence_from_result(result)

    assert evidence is not None
    assert evidence.status is GovernedTerminalStatus.EMPTY
    assert evidence.item_count == 0
    assert evidence.execution_id == result.execution_id
    assert evidence.producer_verified is False


def test_real_adapter_failure_projection():
    instance = gateway(FailedAdapter())
    result = instance.execute_governed_source_query(query())

    assert result.status is GovernedSourceQueryStatus.FAILED
    evidence = terminal_evidence_from_result(result)

    assert evidence is not None
    assert evidence.status is GovernedTerminalStatus.FAILED
    assert evidence.item_count == 0
    assert evidence.producer_verified is False


def test_unregistered_adapter_failure_projection():
    instance = gateway()
    result = instance.execute_governed_source_query(query())

    assert result.status is GovernedSourceQueryStatus.FAILED
    evidence = terminal_evidence_from_result(result)

    assert evidence is not None
    assert evidence.status is GovernedTerminalStatus.FAILED
    assert evidence.item_count == 0
    assert evidence.producer_verified is False


def test_contract_rejection_does_not_return_terminal_result():
    instance = gateway(SuccessfulAdapter())
    invalid_query = query(
        topics=frozenset({InterestTopic.BOCA_JUNIORS}),
    )

    with pytest.raises(ValueError):
        instance.execute_governed_source_query(invalid_query)


def test_prepared_query_is_not_terminal_evidence():
    instance = gateway()
    prepared = instance.prepare_governed_source_query(query())

    assert prepared.response is None
    assert terminal_evidence_from_result(prepared) is None


def test_real_conversational_source_result_projects():
    instance = gateway(SuccessfulAdapter())
    request = GovernedConversationalQuery(
        text="Buscá Artemis",
        query=query(),
    )

    result = instance.execute_governed_conversational_query(request)

    assert result.status is GovernedConversationalQueryStatus.SUCCEEDED
    evidence = terminal_evidence_from_result(result.source_result)

    assert evidence is not None
    assert evidence.status is GovernedTerminalStatus.SUCCEEDED
    assert evidence.item_count == 1
    assert evidence.producer_verified is False


def test_discarded_conversational_items_do_not_change_source_status():
    instance = gateway(InvalidItemAdapter())
    request = GovernedConversationalQuery(
        text="Buscá Artemis",
        query=query(),
    )

    result = instance.execute_governed_conversational_query(request)

    assert result.status is GovernedConversationalQueryStatus.EMPTY
    assert result.source_result.status is GovernedSourceQueryStatus.SUCCEEDED
    assert result.discarded_items == 1

    evidence = terminal_evidence_from_result(result.source_result)
    assert evidence is not None
    assert evidence.status is GovernedTerminalStatus.SUCCEEDED
    assert evidence.item_count == 1
    assert evidence.producer_verified is False


def test_structurally_forged_result_is_not_authenticated():
    instance = gateway(SuccessfulAdapter())
    genuine = instance.execute_governed_source_query(query())

    forged = replace(genuine)
    assert forged is not genuine

    evidence = terminal_evidence_from_result(forged)

    assert evidence is not None
    assert evidence.producer_verified is False


@pytest.mark.parametrize(
    "invalid",
    (None, object(), {}, "forged"),
)
def test_invalid_result_types_do_not_project(invalid):
    assert terminal_evidence_from_result(invalid) is None


def test_inconsistent_result_status_does_not_project():
    instance = gateway(SuccessfulAdapter())
    genuine = instance.execute_governed_source_query(query())

    inconsistent = replace(
        genuine,
        status=GovernedSourceQueryStatus.EMPTY,
    )
    assert terminal_evidence_from_result(inconsistent) is None


def test_projection_has_no_admission_or_identity_fields():
    instance = gateway(SuccessfulAdapter())
    result = instance.execute_governed_source_query(query())
    evidence = terminal_evidence_from_result(result)

    assert evidence is not None
    assert not hasattr(evidence, "owner")
    assert not hasattr(evidence, "session_id")
    assert not hasattr(evidence, "turn_id")
    assert not hasattr(evidence, "authorized")
    assert not hasattr(evidence, "admitted")
