from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.conversation_entry_point import ConversationEntryKind
from core.natural_greeting_response import (
    GreetingPeriod,
    InMemoryNaturalGreetingRepository,
    NaturalGreetingAction,
    NaturalGreetingConfig,
    NaturalGreetingRequest,
    NaturalGreetingResponder,
    NaturalGreetingStatus,
)
from tests.test_m163_conversation_entry_point import NOW, classify

GREETING = classify("Hola ROBY")


def request(*, entry=GREETING, **changes):
    values = {
        "owner": "Carlos",
        "entry_result": entry,
    }
    values.update(changes)
    return NaturalGreetingRequest(**values)


def respond(*, config=None, entry=GREETING, now=NOW, **changes):
    responder = NaturalGreetingResponder(config=config)
    return responder.respond(request(entry=entry, **changes), now=now)


def at(hour):
    return datetime(2026, 7, 12, hour, 0, tzinfo=timezone.utc)


def test_generates_natural_greeting_for_m163_greeting():
    result = respond()
    assert result.status is NaturalGreetingStatus.GENERATED
    assert result.action is NaturalGreetingAction.DELIVER
    assert result.natural
    assert result.response_text


def test_preserves_exact_m163_lineage():
    result = respond()
    assert result.request.entry_result is GREETING


def test_never_echoes_received_or_original_message():
    result = respond()
    lowered = result.response_text.casefold()
    assert "recibido" not in lowered
    assert result.response_text.casefold() != GREETING.normalized_text.casefold()


@pytest.mark.parametrize(
    "forbidden",
    ["solicitud procesada", "comando aceptado", "hola roby"],
)
def test_avoids_command_acknowledgement_language(forbidden):
    assert forbidden not in respond().response_text.casefold()


def test_visible_greeting_uses_no_accented_characters():
    response = respond().response_text
    assert all(character not in response for character in "áéíóúÁÉÍÓÚ")


@pytest.mark.parametrize(
    ("hour", "expected"),
    [
        (6, GreetingPeriod.MORNING),
        (13, GreetingPeriod.AFTERNOON),
        (20, GreetingPeriod.EVENING),
        (1, GreetingPeriod.NIGHT),
    ],
)
def test_detects_time_period(hour, expected):
    assert respond(now=at(hour)).period is expected


def test_can_disable_time_aware_greetings():
    config = NaturalGreetingConfig(allow_time_aware_greetings=False)
    assert respond(config=config, now=at(6)).period is GreetingPeriod.MORNING
    assert respond(config=config, now=at(6)).variant_key.startswith("neutral_")


def test_selection_is_deterministic_for_same_context():
    first = respond(now=at(10))
    second = respond(now=at(10))
    assert first.response_text == second.response_text
    assert first.variant_key == second.variant_key


def test_recent_response_is_avoided_when_alternative_exists():
    first = respond(now=at(10))
    second = respond(
        now=at(10),
        recent_responses=(first.response_text,),
    )
    assert second.response_text != first.response_text
    assert not second.repeated_recent_response


def test_repetition_is_reported_when_all_variants_are_recent():
    recent = (
        "Buen dia. Como estas?",
        "Buen dia. Que vas a hacer hoy?",
        "Buen dia. Como estas hoy?",
    )
    config = NaturalGreetingConfig(recent_response_window=3)
    result = respond(config=config, now=at(10), recent_responses=recent)
    assert result.repeated_recent_response


def test_non_greeting_entry_is_withheld():
    question = classify("Como estas?")
    assert question.kind is ConversationEntryKind.QUESTION
    result = respond(entry=question)
    assert result.status is NaturalGreetingStatus.WITHHELD
    assert result.action is NaturalGreetingAction.WITHHOLD
    assert result.response_text == ""


def test_not_requested_is_not_applicable():
    result = respond(greeting_requested=False)
    assert result.status is NaturalGreetingStatus.NOT_APPLICABLE
    assert result.action is NaturalGreetingAction.NONE


def test_m164_never_authorizes_external_side_effects():
    result = respond()
    assert not result.provider_call_allowed
    assert not result.network_access_allowed
    assert not result.platform_mutation_allowed


def test_repository_stores_result_and_exposes_last():
    repository = InMemoryNaturalGreetingRepository()
    responder = NaturalGreetingResponder(repository=repository)
    result = responder.respond(request(), now=NOW)
    assert repository.get(result.greeting_id) is result
    assert repository.list_all() == (result,)
    assert responder.last_greeting is result


def test_empty_repository_has_no_last_greeting():
    assert NaturalGreetingResponder().last_greeting is None


def test_duplicate_result_is_rejected():
    repository = InMemoryNaturalGreetingRepository()
    responder = NaturalGreetingResponder(repository=repository)
    result = responder.respond(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.owner = "Other"


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_entry_owner():
    with pytest.raises(ValueError, match="match conversation entry owner"):
        request(owner="Other")


def test_session_id_is_required():
    with pytest.raises(ValueError, match="session id"):
        request(session_id=" ")


def test_recent_responses_must_not_be_blank():
    with pytest.raises(ValueError, match="must not be blank"):
        request(recent_responses=(" ",))


def test_assistant_name_is_required():
    with pytest.raises(ValueError, match="assistant name"):
        NaturalGreetingConfig(assistant_name=" ")


def test_recent_window_must_not_be_negative():
    with pytest.raises(ValueError, match="must not be negative"):
        NaturalGreetingConfig(recent_response_window=-1)


def test_maximum_length_must_be_positive():
    with pytest.raises(ValueError, match="must be positive"):
        NaturalGreetingConfig(max_response_length=0)


def test_maximum_length_is_enforced():
    config = NaturalGreetingConfig(max_response_length=4)
    with pytest.raises(ValueError, match="maximum length"):
        respond(config=config)


def test_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        respond(now=NOW.replace(tzinfo=None))


def test_result_id_rejects_inconsistent_value():
    result = respond()
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(result, greeting_id="wrong")
