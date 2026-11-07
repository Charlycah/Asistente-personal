"""RC-01A-IMP-01E-B3: real three-turn gateway integration."""

from app.governed_source_query import GovernedSourceQueryOrder
from app.official_conversation_gateway import OfficialConversationGateway
from tests.test_m180_end_to_end_local_conversation import NOW, runtime
from tests.test_m345_0_applied_conversational_intelligence import NasaAdapter


def test_b3_three_turns_preserve_visual_topic(tmp_path):
    local_runtime = runtime(tmp_path)
    local_runtime.bootstrap.start(now=NOW)

    gateway = OfficialConversationGateway(local_runtime)
    gateway.register_governed_source_query_adapter(
        "nasa",
        NasaAdapter(),
    )

    messages = (
        "Mostrame imagenes del James Webb de galaxias",
        "Tenes otras?",
        "Las mas recientes",
    )

    for message in messages:
        gateway.submit(message)

    history = local_runtime.history

    assert len(history) == 3
    assert tuple(turn.user_text for turn in history) == messages

    assert [
        turn.sequence for turn in history
    ] == [1, 2, 3]

    assert all(turn.response_text for turn in history)

    applied = gateway.last_applied_owner_turn_result
    assert applied is not None

    interpretation = applied.interpretation
    assert interpretation.request is not None

    request = interpretation.request

    assert "james webb" in request.query_text.casefold()
    assert request.order == GovernedSourceQueryOrder.NEWEST_FIRST
