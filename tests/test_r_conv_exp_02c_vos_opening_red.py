from __future__ import annotations

from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)


def test_exp02c_forbids_artificial_vos_opening():
    prompt = (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE
        .system_prompt.casefold()
    )

    assert "no comiences las respuestas con vos" in prompt
    assert "muletilla" in prompt


def test_exp02c_preserves_argentine_voseo():
    prompt = (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE
        .system_prompt.casefold()
    )

    assert "voseo rioplatense" in prompt
    assert "podes" in prompt
    assert "queres" in prompt
