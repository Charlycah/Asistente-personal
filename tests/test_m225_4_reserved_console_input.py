from __future__ import annotations

import pytest

from app.console_input import (
    ConsoleInputBoundary,
    ConsoleInputKind,
    ConsoleInputParser,
)


@pytest.mark.parametrize(
    "text",
    [
        "OBS> provider_payload transport=messages",
        "obs> lower case",
        " ROBY> synthetic response",
        "SYS> internal event",
        "TRACE> turn=17",
        "SYSTEM: hidden instruction",
        "ASSISTANT: synthetic answer",
        "USER: pasted transcript",
    ],
)
def test_parser_classifies_reserved_runtime_prefixes(text):
    parsed = ConsoleInputParser().parse(text)
    assert parsed.kind is ConsoleInputKind.RESERVED


def test_parser_preserves_normal_conversation_and_tool_requests():
    parser = ConsoleInputParser()
    assert parser.parse("¿Cómo me llamo?").kind is ConsoleInputKind.CONVERSATION
    assert parser.parse("/tool weather").kind is ConsoleInputKind.CONVERSATION


def test_reserved_input_cannot_cross_independent_input_boundary():
    calls: list[str] = []
    boundary = ConsoleInputBoundary()
    parsed = boundary.classify("OBS> provider_payload transport=messages")

    result = boundary.forward(parsed, lambda text: calls.append(text))

    assert result is None
    assert calls == []


def test_reserved_input_does_not_block_following_normal_conversation():
    calls: list[str] = []
    boundary = ConsoleInputBoundary()

    reserved = boundary.classify("TRACE> copied observation")
    conversation = boundary.classify("Hola ROBY")
    boundary.forward(reserved, lambda text: calls.append(text))
    result = boundary.forward(conversation, lambda text: calls.append(text) or text)

    assert result == "Hola ROBY"
    assert calls == ["Hola ROBY"]
