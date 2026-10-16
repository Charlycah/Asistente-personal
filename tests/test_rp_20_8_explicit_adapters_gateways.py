from app.official_conversation_gateway import OfficialConversationGateway


def test_official_conversation_gateway_is_not_an_open_proxy() -> None:
    assert "__getattr__" not in OfficialConversationGateway.__dict__


def test_official_conversation_gateway_keeps_explicit_runtime_surface() -> None:
    expected = {
        "bootstrap",
        "history",
        "traces",
        "snapshot",
        "submit",
        "converse",
    }
    assert expected <= set(OfficialConversationGateway.__dict__)
