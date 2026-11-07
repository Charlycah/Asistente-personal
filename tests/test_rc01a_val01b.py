"""RC-01A-VAL-01B: dynamic contextual isolation tests."""

from types import SimpleNamespace
from unittest.mock import patch

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligence,
)
from app.governed_source_query import GovernedSourceQueryOrder
from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import IdentityContextAccessGate

FIRST = (
    "Mostrame imagenes del James Webb "
    "de galaxias y agujeros negros"
)
FOLLOW_UP = (
    "Ahora mostrame otras mas recientes "
    "y explicame que vemos"
)
SESSION = "desktop-main"
OWNER = "Carlos"


def make_gateway(previous=None, *, session=SESSION, owner=OWNER):
    turns = [previous] if previous is not None else []
    runtime = SimpleNamespace(
        authorized_recent_turns=lambda: tuple(turns),
        authorized_latest_turn_matches=lambda candidate: (
            bool(turns)
            and turns[-1].turn_id == candidate.turn_id
            and turns[-1].owner == candidate.owner
            and turns[-1].session_id == candidate.session_id
        ),
        bootstrap=SimpleNamespace(
            config=SimpleNamespace(
                owner=owner,
                session_id=session,
            )
        ),
        history=[previous] if previous is not None else [],
    )

    gateway = object.__new__(OfficialConversationGateway)
    gateway._runtime = runtime
    gateway._applied_conversational_intelligence = (
        AppliedConversationalIntelligence()
    )

    captured = []

    def execute(request):
        captured.append(request)
        return SimpleNamespace(), SimpleNamespace()

    gateway.execute_selected_governed_conversational_query = execute
    gateway._natural_governed_conversational_response = SimpleNamespace(
        compose=lambda **kwargs: "Respuesta gobernada de prueba"
    )

    return gateway, captured


def previous_turn(
    *,
    text=FIRST,
    session=SESSION,
    owner=OWNER,
    response_path="interceptor",
):
    return SimpleNamespace(
               turn_id="rc01a-val01b-turn-1",
        sequence=1,
        user_text=text,
        session_id=session,
        owner=owner,
        response_path=response_path,
        rationale=("applied_conversational_intelligence",),
    )


def resolve(gateway, *, allowed, session=SESSION, text=FOLLOW_UP):
    context = SimpleNamespace(
        shared_conversation_context_allowed=allowed
    )
    with patch.object(
        IdentityContextAccessGate,
        "current",
        return_value=context,
    ):
        return gateway._resolve_applied_contextual_follow_up(
            text,
            session,
        )


def test_val01b_authorized_continuation():
    gateway, captured = make_gateway(previous_turn())

    result = resolve(gateway, allowed=True)

    assert result is not None
    assert len(captured) == 1
    request = captured[0]

    assert "james webb" in request.query_text.casefold()
    assert "galaxias" in request.query_text.casefold()
    assert "agujeros negros" in request.query_text.casefold()
    assert request.order == GovernedSourceQueryOrder.NEWEST_FIRST
    assert request.text == FOLLOW_UP


def test_val01b_denied_context_does_not_execute():
    gateway, captured = make_gateway(previous_turn())

    result = resolve(gateway, allowed=False)

    assert result is None
    assert captured == []


def test_val01b_different_session_does_not_execute():
    gateway, captured = make_gateway(
        previous_turn(session="another-session")
    )

    result = resolve(gateway, allowed=True)

    assert result is None
    assert captured == []


def test_val01b_different_owner_does_not_execute():
    gateway, captured = make_gateway(
        previous_turn(owner="Another owner")
    )

    result = resolve(gateway, allowed=True)

    assert result is None
    assert captured == []


def test_val01b_intervening_general_turn_blocks_continuation():
    gateway, captured = make_gateway(
        previous_turn(
            text="Hablemos de otro tema",
            response_path="provider",
        )
    )

    result = resolve(gateway, allowed=True)

    assert result is None
    assert captured == []


def test_val01b_no_previous_turn_does_not_execute():
    gateway, captured = make_gateway()

    result = resolve(gateway, allowed=True)

    assert result is None
    assert captured == []


def test_val01b_ambiguous_message_does_not_execute():
    gateway, captured = make_gateway(previous_turn())

    result = resolve(
        gateway,
        allowed=True,
        text="?Y qu? opin?s de eso?",
    )

    assert result is None
    assert captured == []
def test_imp01e_b2_natural_continuation():
    gateway, captured = make_gateway(previous_turn())
    result = resolve(gateway, allowed=True, text="\u00bfTen\u00e9s otras?")

    assert result is not None
    assert captured
    request = captured[-1]
    assert "james webb" in request.query_text.casefold()
    assert "galaxias" in request.query_text.casefold()


def test_imp01e_b2_recent_results():
    gateway, captured = make_gateway(previous_turn())
    result = resolve(gateway, allowed=True, text="Las m\u00e1s recientes")

    assert result is not None
    assert captured
    request = captured[-1]
    assert request.order == GovernedSourceQueryOrder.NEWEST_FIRST
    assert "james webb" in request.query_text.casefold()


def test_imp01e_b2_paraphrased_continuation():
    gateway, captured = make_gateway(previous_turn())
    result = resolve(gateway, allowed=True, text="Mostrame algunas m\u00e1s")

    assert result is not None
    assert captured


def test_imp01e_b2_topic_change_blocks_continuation():
    gateway, captured = make_gateway(previous_turn())
    result = resolve(gateway, allowed=True, text="Cambiemos de tema")

    assert result is None
    assert not captured


def test_imp01e_b2_new_request_is_not_continuation():
    gateway, captured = make_gateway(previous_turn())
    result = resolve(
        gateway,
        allowed=True,
        text="Quiero conocer otras alternativas de programaci\u00f3n",
    )

    assert result is None
    assert not captured


def test_imp01e_b2_unverified_restriction_does_not_execute():
    gateway, captured = make_gateway(previous_turn())
    result = resolve(gateway, allowed=True, text="Solo galaxias")

    assert result is None
    assert not captured
