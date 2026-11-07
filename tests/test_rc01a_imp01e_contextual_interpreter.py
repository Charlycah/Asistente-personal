import pytest

from app.contextual_follow_up_interpreter import (
    FollowUpIntent,
    interpret_contextual_follow_up,
)


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("\u00bfTen\u00e9s otras?", FollowUpIntent.CONTINUE),
        ("\u00bfTienes m\u00e1s?", FollowUpIntent.CONTINUE),
        ("Mostrame algunas m\u00e1s", FollowUpIntent.CONTINUE),
        ("Las m\u00e1s recientes", FollowUpIntent.REORDER),
        ("\u00bfY las \u00faltimas?", FollowUpIntent.REORDER),
        ("Pero sin los rovers", FollowUpIntent.RESTRICT),
        ("Solo galaxias", FollowUpIntent.RESTRICT),
        ("Cambiemos de tema", FollowUpIntent.TOPIC_CHANGE),
        ("Ahora hablemos de m\u00fasica", FollowUpIntent.TOPIC_CHANGE),
        ("Hola, \u00bfc\u00f3mo est\u00e1s?", FollowUpIntent.UNDETERMINED),
    ],
)
def test_follow_up_intent(message, expected):
    result = interpret_contextual_follow_up(message)
    assert result.intent is expected


def test_freshness_flag():
    result = interpret_contextual_follow_up("Las m\u00e1s recientes")
    assert result.newest_first


def test_exclusion():
    result = interpret_contextual_follow_up("Pero sin los rovers")
    assert result.exclusion == "rovers"


def test_inclusion():
    result = interpret_contextual_follow_up("Solo galaxias")
    assert result.inclusion == "galaxias"
