from __future__ import annotations

from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)


def test_exp02a_default_language_remains_argentine_spanish():
    style = DEFAULT_HOUSEHOLD_CONVERSATION_STYLE

    prompt = style.system_prompt_for_language(None)

    assert prompt == style.system_prompt
    assert "Responde en espanol argentino" in prompt


def test_exp02a_explicit_english_uses_compatible_guidance():
    style = DEFAULT_HOUSEHOLD_CONVERSATION_STYLE

    prompt = style.system_prompt_for_language("en")

    assert "Respond in English" in prompt
    assert "Responde en espanol argentino" not in prompt


def test_exp02a_english_preserves_identity_and_sobriety():
    style = DEFAULT_HOUSEHOLD_CONVERSATION_STYLE

    prompt = style.system_prompt_for_language("en")

    assert "Sos Roby" in prompt
    assert "soberly" in prompt.lower()


def test_exp02a_english_excludes_spanish_only_rules():
    style = DEFAULT_HOUSEHOLD_CONVERSATION_STYLE

    prompt = style.system_prompt_for_language("en")

    assert "Usa voseo rioplatense" not in prompt
    assert "Nunca uses tu, ti, contigo" not in prompt
    assert "No uses espanol latino neutro" not in prompt
