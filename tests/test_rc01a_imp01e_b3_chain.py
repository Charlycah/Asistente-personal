
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.governed_source_query import GovernedSourceQueryOrder
from core.cognitive_maturity import IdentityContextAccessGate

_helper_path = Path(__file__).with_name("test_rc01a_val01b.py")
_spec = spec_from_file_location("_rc01a_b3_helper", _helper_path)

if _spec is None or _spec.loader is None:
    raise RuntimeError("No se pudo cargar el auxiliar B3.")

_helper = module_from_spec(_spec)
_spec.loader.exec_module(_helper)

OWNER = _helper.OWNER
SESSION = _helper.SESSION
make_gateway = _helper.make_gateway
previous_turn = _helper.previous_turn


def test_b3_three_turn_chain_preserves_original_topic():
    original = previous_turn()
    original.sequence = 1
    original.response_text = "Respuesta especializada original"

    continuation = SimpleNamespace(
        turn_id="rc01a-b3-turn-2",
        sequence=2,
        rationale=("applied_conversational_intelligence",),
        response_text="Respuesta especializada de continuacion",
        user_text="\u00bfTen\u00e9s otras?",
        session_id=SESSION,
        owner=OWNER,
        response_path="interceptor",
    )

    gateway, captured = make_gateway(continuation)

    gateway._runtime.authorized_recent_turns = (
        lambda: (original, continuation)
    )
    gateway._runtime.history = [original, continuation]

    context = SimpleNamespace(
        shared_conversation_context_allowed=True
    )

    with patch.object(
        IdentityContextAccessGate,
        "current",
        return_value=context,
    ):
        result = gateway._resolve_applied_contextual_follow_up(
            "Las m\u00e1s recientes",
            SESSION,
        )

    assert result is not None
    assert len(captured) == 1

    request = captured[0]
    assert "james webb" in request.query_text.casefold()
    assert request.order == GovernedSourceQueryOrder.NEWEST_FIRST



def _b3_check_chain(
    *,
    original_sequence=1,
    continuation_sequence=2,
    original_owner=OWNER,
    original_session=SESSION,
    original_path="interceptor",
    original_text=None,
    continuation_text="\u00bfTen\u00e9s otras?",
    continuation_path="interceptor",
    latest_matches=True,
    include_original=True,
):
    original = previous_turn(
        text=original_text or _helper.FIRST,
        owner=original_owner,
        session=original_session,
        response_path=original_path,
    )
    original.sequence = original_sequence
    original.response_text = "Respuesta original"

    continuation = SimpleNamespace(
        turn_id="rc01a-b3-sec-turn-2",
        sequence=continuation_sequence,
        response_text="Respuesta de continuacion",
        user_text=continuation_text,
        session_id=SESSION,
        owner=OWNER,
        response_path=continuation_path,
    )

    gateway, captured = make_gateway(continuation)
    history = (
        (original, continuation)
        if include_original
        else (continuation,)
    )

    gateway._runtime.authorized_recent_turns = lambda: history
    gateway._runtime.history = list(history)

    if not latest_matches:
        gateway._runtime.authorized_latest_turn_matches = (
            lambda candidate: False
        )

    context = SimpleNamespace(
        shared_conversation_context_allowed=True
    )

    with patch.object(
        IdentityContextAccessGate,
        "current",
        return_value=context,
    ):
        result = gateway._resolve_applied_contextual_follow_up(
            "Las m\u00e1s recientes",
            SESSION,
        )

    return result, captured


def test_b3_rejects_sequence_gap():
    result, captured = _b3_check_chain(
        continuation_sequence=3,
    )
    assert result is None
    assert not captured


def test_b3_rejects_other_owner():
    result, captured = _b3_check_chain(
        original_owner="otro-propietario",
    )
    assert result is None
    assert not captured


def test_b3_rejects_other_session():
    result, captured = _b3_check_chain(
        original_session="otra-sesion",
    )
    assert result is None
    assert not captured


def test_b3_rejects_general_interruption():
    result, captured = _b3_check_chain(
        continuation_path="general",
    )
    assert result is None
    assert not captured


def test_b3_rejects_missing_antecedent():
    result, captured = _b3_check_chain(
        include_original=False,
    )
    assert result is None
    assert not captured


def test_b3_rejects_stale_latest_turn():
    result, captured = _b3_check_chain(
        latest_matches=False,
    )
    assert result is None
    assert not captured


def test_b3_rejects_explicit_topic_change():
    result, captured = _b3_check_chain(
        continuation_text="Cambiemos de tema",
    )
    assert result is None
    assert not captured



def test_b3_rejects_unrelated_specialized_turn():
    result, captured = _b3_check_chain(
        continuation_text=(
            "Consulta mis documentos personales "
            "sobre un tramite"
        ),
        continuation_path="interceptor",
    )

    assert result is None
    assert not captured



def test_b3_rejects_foreign_interceptor_provenance():
    original = previous_turn(
        text=_helper.FIRST,
        owner=OWNER,
        session=SESSION,
        response_path="interceptor",
    )
    original.sequence = 1
    original.response_text = "Respuesta visual"
    original.rationale = (
        "applied_conversational_intelligence",
    )

    foreign = SimpleNamespace(
        turn_id="rc01a-b3-cap-foreign",
        sequence=2,
        response_text="Respuesta de otra capacidad",
        user_text="Tenes otras?",
        session_id=SESSION,
        owner=OWNER,
        response_path="interceptor",
        rationale=("controlled_interlocutor_identification_completed",),
    )

    gateway, captured = make_gateway(foreign)

    history = (original, foreign)
    gateway._runtime.authorized_recent_turns = lambda: history
    gateway._runtime.history = list(history)

    context = SimpleNamespace(
        shared_conversation_context_allowed=True,
    )

    with patch.object(
        IdentityContextAccessGate,
        "current",
        return_value=context,
    ):
        result = gateway._resolve_applied_contextual_follow_up(
            "Las mas recientes",
            SESSION,
        )

    assert result is None
    assert not captured
