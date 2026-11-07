import pytest

from app.contextual_follow_up_interpreter import (
    FollowUpIntent,
    interpret_contextual_follow_up,
)


@pytest.mark.parametrize(
    ("message", "intent", "newest"),
    [
        (
            "Mostrame otras, pero m\u00e1s recientes",
            FollowUpIntent.REORDER,
            True,
        ),
        (
            "\u00bfTen\u00e9s algunas m\u00e1s recientes?",
            FollowUpIntent.REORDER,
            True,
        ),
        (
            "Solo galaxias",
            FollowUpIntent.RESTRICT,
            False,
        ),
        (
            "Pero sin los rovers",
            FollowUpIntent.RESTRICT,
            False,
        ),
        (
            "Cambiemos de tema, mostrame otras",
            FollowUpIntent.TOPIC_CHANGE,
            False,
        ),
    ],
)
def test_combined_follow_up(message, intent, newest):
    result = interpret_contextual_follow_up(message)
    assert result.intent is intent
    assert result.newest_first is newest


def test_combined_restriction_and_freshness():
    result = interpret_contextual_follow_up(
        "Pero sin los rovers, y las m\u00e1s recientes"
    )
    assert result.intent is FollowUpIntent.RESTRICT
    assert result.exclusion == "rovers"
    assert result.newest_first


def test_no_false_continuation():
    result = interpret_contextual_follow_up(
        "Quiero conocer otras alternativas de programaci\u00f3n"
    )
    assert result.intent is FollowUpIntent.UNDETERMINED
