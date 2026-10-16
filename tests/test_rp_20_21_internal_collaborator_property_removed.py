from app.official_conversation_gateway import OfficialConversationGateway


def test_gateway_does_not_expose_internal_runtime_collaborator() -> None:
    assert "runtime" not in OfficialConversationGateway.__dict__


def test_gateway_keeps_explicit_operational_views() -> None:
    assert {"bootstrap", "history", "traces", "snapshot", "submit"} <= set(
        OfficialConversationGateway.__dict__
    )


def test_gateway_has_no_generic_attribute_forwarding() -> None:
    assert "__getattr__" not in OfficialConversationGateway.__dict__
