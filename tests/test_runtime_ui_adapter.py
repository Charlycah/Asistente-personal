from app.runtime_ui_adapter import RuntimeUIAdapter
from m6.response.models import ResponseStatus


class FakeRuntime:
    def __init__(self, response: object = "respuesta") -> None:
        self.response = response
        self.received_input: str | None = None

    def handle_input(self, user_input: str) -> object:
        self.received_input = user_input
        return self.response


class FailingRuntime:
    def handle_input(self, user_input: str) -> object:
        raise RuntimeError("runtime unavailable")


def test_submit_text_forwards_normalized_input() -> None:
    runtime = FakeRuntime("ROBY: recibí tu mensaje: Hola")
    adapter = RuntimeUIAdapter(runtime)

    response = adapter.submit_text("  Hola  ", session_id="session-1")

    assert runtime.received_input == "Hola"
    assert response.text == "ROBY: recibí tu mensaje: Hola"
    assert response.status == ResponseStatus.SUCCESS.value
    assert response.session_id == "session-1"
    assert response.needs_input is False


def test_submit_text_rejects_empty_input() -> None:
    runtime = FakeRuntime()
    adapter = RuntimeUIAdapter(runtime)

    response = adapter.submit_text("   ")

    assert runtime.received_input is None
    assert response.status == ResponseStatus.NEEDS_INFORMATION.value
    assert response.needs_input is True


def test_submit_text_converts_runtime_result_to_text() -> None:
    runtime = FakeRuntime({"answer": "hola"})
    adapter = RuntimeUIAdapter(runtime)

    response = adapter.submit_text("Hola")

    assert response.text == "{'answer': 'hola'}"


def test_submit_text_handles_runtime_failure() -> None:
    adapter = RuntimeUIAdapter(FailingRuntime())

    response = adapter.submit_text("Hola")

    assert response.text == "Ocurrió un error al procesar tu mensaje."
    assert response.status == ResponseStatus.FAILURE.value
    assert response.needs_input is False
