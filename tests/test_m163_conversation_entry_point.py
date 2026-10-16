from dataclasses import FrozenInstanceError, replace

import pytest

from core.conversation_entry_point import (
    ConversationEntryAction,
    ConversationEntryConfig,
    ConversationEntryKind,
    ConversationEntryPoint,
    ConversationEntryRequest,
    InMemoryConversationEntryRepository,
)
from core.runtime_readiness_gate import RuntimeReadinessStatus
from tests.test_m162_runtime_readiness_gate import NOW, evaluate

READY = evaluate(now=NOW)


def request(text="Hola ROBY", *, readiness=READY, **changes):
    values = {
        "owner": "Carlos",
        "text": text,
        "readiness_result": readiness,
    }
    values.update(changes)
    return ConversationEntryRequest(**values)


def classify(text="Hola ROBY", *, config=None, readiness=READY, **changes):
    point = ConversationEntryPoint(config=config)
    return point.classify(
        request(text, readiness=readiness, **changes),
        now=NOW,
    )


def test_greeting_routes_to_natural_greeting_stage():
    result = classify("Hola ROBY")
    assert result.kind is ConversationEntryKind.GREETING
    assert result.action is ConversationEntryAction.ROUTE_TO_GREETING
    assert result.addressed_to_roby


@pytest.mark.parametrize("text", ["Hola", "Buenas", "Hey ROBY", "Ey"])
def test_common_greetings_are_detected(text):
    assert classify(text).kind is ConversationEntryKind.GREETING


def test_assistant_name_alone_is_attention():
    result = classify("ROBY")
    assert result.kind is ConversationEntryKind.ATTENTION
    assert result.action is ConversationEntryAction.ROUTE_TO_ATTENTION


def test_blank_message_is_incomplete():
    result = classify("   ")
    assert result.kind is ConversationEntryKind.INCOMPLETE
    assert result.action is ConversationEntryAction.REQUEST_COMPLETION


def test_question_is_detected():
    result = classify("Como estas?")
    assert result.kind is ConversationEntryKind.QUESTION
    assert result.action is ConversationEntryAction.ROUTE_TO_REASONING


def test_request_is_detected_before_question():
    result = classify("ROBY, buscame que paso con la ISS")
    assert result.kind is ConversationEntryKind.REQUEST
    assert result.action is ConversationEntryAction.ROUTE_TO_ACTION


def test_continuation_is_detected():
    result = classify("Ademas sigamos con el modulo")
    assert result.kind is ConversationEntryKind.CONTINUATION
    assert result.action is ConversationEntryAction.ROUTE_TO_CONTEXT


def test_comment_is_default_conversational_entry():
    result = classify("Pink Floyd tiene una atmosfera unica")
    assert result.kind is ConversationEntryKind.COMMENT
    assert result.action is ConversationEntryAction.ROUTE_TO_DIALOGUE


@pytest.mark.parametrize("text", ["Chau", "Nos vemos", "Hasta luego"])
def test_farewell_is_detected(text):
    assert classify(text).kind is ConversationEntryKind.FAREWELL


def test_normalizes_whitespace_without_rewriting_content():
    result = classify("  Hola    ROBY  ")
    assert result.normalized_text == "Hola ROBY"


def test_preserves_exact_m162_lineage():
    result = classify()
    assert result.request.readiness_result is READY


def test_blocked_readiness_withholds_entry():
    blocked = replace(
        READY,
        status=RuntimeReadinessStatus.BLOCKED,
        ready=False,
        blocked=True,
        rationale=("blocked_for_test",),
        readiness_id="",
    )
    result = classify(readiness=blocked)
    assert result.kind is ConversationEntryKind.NOT_APPLICABLE
    assert result.action is ConversationEntryAction.WITHHOLD
    assert not result.conversational


def test_not_requested_is_not_applicable():
    result = classify(conversation_requested=False)
    assert result.kind is ConversationEntryKind.NOT_APPLICABLE
    assert result.action is ConversationEntryAction.NONE
    assert result.normalized_text == ""


def test_m163_never_generates_or_executes_response():
    result = classify()
    assert not result.response_generation_allowed
    assert not result.provider_call_allowed
    assert not result.network_access_allowed
    assert not result.platform_mutation_allowed


def test_custom_assistant_name_is_supported():
    config = ConversationEntryConfig(assistant_names=("roby", "samantha"))
    result = classify("Samantha", config=config)
    assert result.kind is ConversationEntryKind.ATTENTION
    assert result.addressed_to_roby


def test_repository_stores_result_and_exposes_last():
    repository = InMemoryConversationEntryRepository()
    point = ConversationEntryPoint(repository=repository)
    result = point.classify(request(), now=NOW)
    assert repository.get(result.entry_id) is result
    assert repository.list_all() == (result,)
    assert point.last_entry is result


def test_empty_repository_has_no_last_entry():
    assert ConversationEntryPoint().last_entry is None


def test_duplicate_result_is_rejected():
    repository = InMemoryConversationEntryRepository()
    point = ConversationEntryPoint(repository=repository)
    result = point.classify(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.text = "otro"


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_readiness_owner():
    with pytest.raises(ValueError, match="match readiness owner"):
        request(owner="Other")


def test_session_id_is_required():
    with pytest.raises(ValueError, match="session id"):
        request(session_id=" ")


def test_assistant_names_must_be_unique():
    with pytest.raises(ValueError, match="unique"):
        ConversationEntryConfig(assistant_names=("ROBY", "roby"))


def test_minimum_text_length_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        ConversationEntryConfig(minimum_text_length=0)


def test_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        ConversationEntryPoint().classify(
            request(),
            now=NOW.replace(tzinfo=None),
        )
