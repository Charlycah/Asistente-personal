from app.ui_adapter import ROBYUIAdapter, UIResponse
from m6.response.models import ResponseStatus, UserResponse


class FakeROBY:
    def __init__(self, response: UserResponse | None = None) -> None:
        self.response = response or UserResponse(
            text="Listo.",
            status=ResponseStatus.SUCCESS,
        )
        self.calls = []

    def process(self, text: str, session_id: str | None = None) -> UserResponse:
        self.calls.append({"text": text, "session_id": session_id})
        return self.response


class FailingROBY:
    def process(self, text: str, session_id: str | None = None) -> UserResponse:
        raise RuntimeError("boom")


def test_ui_adapter_sends_text_to_roby_and_returns_presentable_response():
    roby = FakeROBY(
        UserResponse(text="Recordatorio creado.", status=ResponseStatus.SUCCESS)
    )
    adapter = ROBYUIAdapter(roby)

    response = adapter.submit_text("recordame tomar agua", session_id="s1")

    assert roby.calls == [{"text": "recordame tomar agua", "session_id": "s1"}]
    assert response == UIResponse(
        text="Recordatorio creado.",
        status="success",
        session_id="s1",
        needs_input=False,
    )


def test_ui_adapter_marks_needs_input_when_roby_needs_information():
    roby = FakeROBY(
        UserResponse(
            text="¿Cuándo querés que te lo recuerde?",
            status=ResponseStatus.NEEDS_INFORMATION,
        )
    )
    adapter = ROBYUIAdapter(roby)

    response = adapter.submit_text("recordame tomar agua", session_id="s1")

    assert response.text == "¿Cuándo querés que te lo recuerde?"
    assert response.status == "needs_information"
    assert response.needs_input is True


def test_ui_adapter_rejects_empty_text_without_calling_roby():
    roby = FakeROBY()
    adapter = ROBYUIAdapter(roby)

    response = adapter.submit_text("   ", session_id="s1")

    assert roby.calls == []
    assert response.status == "needs_information"
    assert response.needs_input is True
    assert response.session_id == "s1"
    assert response.text


def test_ui_adapter_converts_unexpected_roby_errors_to_failure_response():
    adapter = ROBYUIAdapter(FailingROBY())

    response = adapter.submit_text("hola", session_id="s1")

    assert response.status == "failure"
    assert response.needs_input is False
    assert response.session_id == "s1"
    assert response.text
