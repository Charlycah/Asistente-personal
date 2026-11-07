"""RC-01A-TEST-02: specialized turns and shared conversation history."""

from app.official_conversation_gateway import OfficialConversationGateway
from tests.test_m180_end_to_end_local_conversation import NOW, runtime
from tests.test_m345_0_applied_conversational_intelligence import NasaAdapter


def test_specialized_turn_is_recorded_in_shared_history(tmp_path):
    local_runtime = runtime(tmp_path)
    local_runtime.bootstrap.start(now=NOW)

    gateway = OfficialConversationGateway(local_runtime)
    gateway.register_governed_source_query_adapter("nasa", NasaAdapter())

    request = (
        "Mostrame imagenes del James Webb "
        "de galaxias y agujeros negros"
    )

    turn = gateway.submit(request)

    assert turn is not None

    history = local_runtime.history

    assert len(history) == 1
    assert history[0].user_text == request
    assert history[0].response_text


def test_contextual_follow_up_uses_shared_history(tmp_path):
    local_runtime = runtime(tmp_path)
    local_runtime.bootstrap.start(now=NOW)

    gateway = OfficialConversationGateway(local_runtime)
    gateway.register_governed_source_query_adapter("nasa", NasaAdapter())

    first_request = (
        "Mostrame imagenes del James Webb "
        "de galaxias y agujeros negros"
    )
    second_request = (
        "Ahora mostrame otras mas recientes "
        "y explicame que vemos"
    )

    gateway.submit(first_request)
    gateway.submit(second_request)

    history = local_runtime.history

    assert len(history) == 2
    assert history[0].user_text == first_request
    assert history[1].user_text == second_request

    applied = gateway.last_applied_owner_turn_result

    assert applied is not None, (
        "The contextual follow-up must remain connected "
        "to the specialized visual request."
    )


def test_rc01a_characterize_two_turn_routes(tmp_path):
    local_runtime = runtime(tmp_path)
    local_runtime.bootstrap.start(now=NOW)

    gateway = OfficialConversationGateway(local_runtime)
    gateway.register_governed_source_query_adapter("nasa", NasaAdapter())

    first = gateway.submit(
        "Mostrame imagenes del James Webb de galaxias y agujeros negros"
    )
    second = gateway.submit(
        "Ahora mostrame otras mas recientes y explicame que vemos"
    )

    history = local_runtime.history

    print("\\n=== RC-01A / TWO TURN ROUTES ===")
    print("FIRST TYPE:", type(first).__name__)
    print("SECOND TYPE:", type(second).__name__)

    for index, turn in enumerate(history, 1):
        print(f"TURN {index} USER:", turn.user_text)
        print(
            f"TURN {index} RESPONSE PATH:",
            getattr(turn, "response_path", None),
        )
        print(
            f"TURN {index} STATUS:",
            getattr(turn, "status", None),
        )
        print(
            f"TURN {index} RESPONSE:",
            turn.response_text[:300],
        )

    assert len(history) == 2
