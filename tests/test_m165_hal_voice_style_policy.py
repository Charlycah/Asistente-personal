from dataclasses import FrozenInstanceError, replace

import pytest

from core.roby_voice_style_policy import (
    InMemoryROBYVoiceStyleRepository,
    ROBYVoiceStyleConfig,
    ROBYVoiceStylePolicy,
    ROBYVoiceStyleRequest,
    VoicePolicyAction,
    VoicePolicyStatus,
)
from tests.test_m164_natural_greeting_response import NOW, respond

GREETING = respond()


def request(*, greeting=GREETING, **changes):
    values = {"owner": "Carlos", "greeting_result": greeting}
    values.update(changes)
    return ROBYVoiceStyleRequest(**values)


def apply(*, config=None, greeting=GREETING, now=NOW, **changes):
    policy = ROBYVoiceStylePolicy(config=config)
    return policy.apply(request(greeting=greeting, **changes), now=now)


def greeting_with(text):
    return replace(GREETING, response_text=text, greeting_id="")


def test_applies_voice_policy_to_m164_greeting():
    result = apply()
    assert result.status is VoicePolicyStatus.APPLIED
    assert result.action is VoicePolicyAction.DELIVER
    assert result.natural
    assert result.response_text


def test_preserves_exact_m164_lineage():
    result = apply()
    assert result.request.greeting_result is GREETING


def test_preserves_already_compliant_text():
    result = apply()
    assert result.response_text == GREETING.response_text
    assert not result.normalized


def test_strips_accents_from_visible_response():
    result = apply(greeting=greeting_with("Hola. Como estás?"))
    assert result.response_text == "Hola. Como estas?"
    assert result.normalized


def test_normalizes_extra_whitespace():
    result = apply(greeting=greeting_with("Hola.   Todo bien?  "))
    assert result.response_text == "Hola. Todo bien?"


@pytest.mark.parametrize(
    "phrase",
    [
        "Recibido. Hola ROBY.",
        "Comando aceptado.",
        "Solicitud procesada.",
        "En que puedo asistirle?",
    ],
)
def test_rejects_bureaucratic_language(phrase):
    result = apply(greeting=greeting_with(phrase))
    assert result.status is VoicePolicyStatus.WITHHELD
    assert result.action is VoicePolicyAction.WITHHOLD
    assert result.response_text == ""
    assert result.bureaucratic_phrase_detected


def test_policy_can_report_bureaucratic_phrase_without_rejecting():
    config = ROBYVoiceStyleConfig(forbid_bureaucratic_phrases=False)
    result = apply(config=config, greeting=greeting_with("Recibido."))
    assert result.status is VoicePolicyStatus.APPLIED
    assert result.bureaucratic_phrase_detected


def test_not_requested_is_not_applicable():
    result = apply(style_requested=False)
    assert result.status is VoicePolicyStatus.NOT_APPLICABLE
    assert result.action is VoicePolicyAction.NONE


def test_withholds_non_deliverable_greeting():
    inactive = replace(
        GREETING,
        status="withheld",
        action="withhold",
        response_text="",
        variant_key="",
        natural=False,
        greeting_id="",
    )
    result = apply(greeting=inactive)
    assert result.status is VoicePolicyStatus.WITHHELD


def test_m165_never_authorizes_external_side_effects():
    result = apply()
    assert not result.provider_call_allowed
    assert not result.network_access_allowed
    assert not result.platform_mutation_allowed


def test_repository_stores_result_and_exposes_last():
    repository = InMemoryROBYVoiceStyleRepository()
    policy = ROBYVoiceStylePolicy(repository=repository)
    result = policy.apply(request(), now=NOW)
    assert repository.get(result.policy_id) is result
    assert repository.list_all() == (result,)
    assert policy.last_result is result


def test_empty_repository_has_no_last_result():
    assert ROBYVoiceStylePolicy().last_result is None


def test_duplicate_result_is_rejected():
    repository = InMemoryROBYVoiceStyleRepository()
    policy = ROBYVoiceStylePolicy(repository=repository)
    result = policy.apply(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.owner = "Other"


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_greeting_owner():
    with pytest.raises(ValueError, match="match greeting owner"):
        request(owner="Other")


def test_assistant_name_is_required():
    with pytest.raises(ValueError, match="assistant name"):
        ROBYVoiceStyleConfig(assistant_name=" ")


def test_maximum_response_length_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        ROBYVoiceStyleConfig(max_response_length=0)


def test_response_length_limit_is_enforced():
    config = ROBYVoiceStyleConfig(max_response_length=5)
    with pytest.raises(ValueError, match="maximum length"):
        apply(config=config)


def test_timestamp_must_be_timezone_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        apply(now=NOW.replace(tzinfo=None))
