from dataclasses import FrozenInstanceError, replace
from datetime import timezone

import pytest

from core.roby_console_application import (
    ConsoleApplicationStatus,
    ConsoleTurnAction,
    ConsoleTurnStatus,
    InMemoryROBYConsoleRepository,
    ROBYConsoleApplication,
    ROBYConsoleConfig,
    ROBYConsoleSessionRequest,
)
from core.runtime_readiness_gate import RuntimeReadinessStatus
from tests.test_m162_runtime_readiness_gate import NOW, evaluate

READY = evaluate(now=NOW)


class FakeConsoleIO:
    def __init__(self, inputs=()):
        self.inputs = list(inputs)
        self.prompts = []
        self.outputs = []

    def read(self, prompt):
        self.prompts.append(prompt)
        if not self.inputs:
            return None
        return self.inputs.pop(0)

    def write(self, text):
        self.outputs.append(text)


def request(*, readiness=READY, **changes):
    values = {
        "owner": "Carlos",
        "readiness_result": readiness,
        "session_id": "console-main",
    }
    values.update(changes)
    return ROBYConsoleSessionRequest(**values)


def app(inputs=(), **changes):
    io = FakeConsoleIO(inputs)
    return ROBYConsoleApplication(io=io, **changes), io


def test_runs_greeting_through_m163_m164_and_m165():
    application, io = app(("Hola ROBY", "salir"))
    session = application.run(request(), now=NOW)
    first = session.turns[0]
    assert first.status is ConsoleTurnStatus.DELIVERED
    assert first.entry_result is not None
    assert first.greeting_result is not None
    assert first.voice_result is not None
    assert first.response_text == first.voice_result.response_text
    assert io.outputs == ["ROBY: " + first.response_text]


def test_preserves_exact_readiness_lineage():
    application, _ = app(("salir",))
    session = application.run(request(), now=NOW)
    assert session.request.readiness_result is READY


def test_exit_command_stops_session_without_output():
    application, io = app(("salir", "Hola"))
    session = application.run(request(), now=NOW)
    assert len(session.turns) == 1
    assert session.turns[0].action is ConsoleTurnAction.STOP_SESSION
    assert io.outputs == []


@pytest.mark.parametrize("command", ["salir", "EXIT", " Quit "])
def test_configured_exit_commands_are_case_insensitive(command):
    application, _ = app((command,))
    result = application.run(request(), now=NOW)
    assert result.turns[0].action is ConsoleTurnAction.STOP_SESSION


def test_end_of_input_closes_empty_session():
    application, io = app()
    result = application.run(request(), now=NOW)
    assert result.status is ConsoleApplicationStatus.STOPPED
    assert result.turns == ()
    assert io.prompts == ["Tu: "]


def test_question_is_routed_without_fabricated_answer():
    application, io = app(("Como estas?", "salir"))
    result = application.run(request(), now=NOW)
    turn = result.turns[0]
    assert turn.status is ConsoleTurnStatus.ROUTED
    assert turn.action is ConsoleTurnAction.AWAIT_PIPELINE
    assert turn.greeting_result is None
    assert turn.voice_result is None
    assert turn.response_text == application.config.pending_response
    assert io.outputs == ["ROBY: " + application.config.pending_response]


def test_blank_input_requests_completion():
    application, _ = app(("   ", "salir"))
    turn = application.run(request(), now=NOW).turns[0]
    assert turn.status is ConsoleTurnStatus.INCOMPLETE
    assert turn.action is ConsoleTurnAction.REQUEST_COMPLETION
    assert turn.response_text == application.config.incomplete_response


def test_attention_is_routed_to_pending_pipeline():
    application, _ = app(("ROBY", "salir"))
    turn = application.run(request(), now=NOW).turns[0]
    assert turn.action is ConsoleTurnAction.AWAIT_PIPELINE


def test_blocked_readiness_prevents_console_reads():
    blocked = replace(
        READY,
        status=RuntimeReadinessStatus.BLOCKED,
        action="withhold",
        ready=False,
        blocked=True,
        readiness_id="",
    )
    application, io = app(("Hola",))
    session = application.run(request(readiness=blocked), now=NOW)
    assert session.status is ConsoleApplicationStatus.BLOCKED
    assert session.turns == ()
    assert io.prompts == []
    assert io.outputs == ["ROBY: " + application.config.blocked_response]


def test_degraded_readiness_allows_console():
    degraded = replace(
        READY,
        status=RuntimeReadinessStatus.DEGRADED,
        action="declare_degraded",
        ready=False,
        degraded=True,
        readiness_id="",
    )
    application, _ = app(("salir",))
    session = application.run(request(readiness=degraded), now=NOW)
    assert session.status is ConsoleApplicationStatus.STOPPED


def test_max_turns_bounds_session():
    config = ROBYConsoleConfig(max_turns=2)
    application, io = app(("Hola", "Hola", "Hola"), config=config)
    session = application.run(request(), now=NOW)
    assert len(session.turns) == 2
    assert len(io.prompts) == 2


def test_turn_sequence_is_contiguous():
    application, _ = app(("Hola", "Como estas?", "salir"))
    turns = application.run(request(), now=NOW).turns
    assert tuple(item.sequence for item in turns) == (1, 2, 3)


def test_recent_greeting_responses_are_forwarded():
    application, _ = app(("Hola", "Hola", "salir"))
    turns = application.run(request(), now=NOW).turns
    assert turns[1].greeting_result.request.recent_responses == (
        turns[0].response_text,
    )


def test_no_external_side_effects_are_reported():
    application, _ = app(("Hola", "salir"))
    turn = application.run(request(), now=NOW).turns[0]
    assert not turn.provider_call_performed
    assert not turn.network_access_performed
    assert not turn.platform_mutation_performed


def test_repository_is_append_only():
    repository = InMemoryROBYConsoleRepository()
    first, _ = app(("salir",), repository=repository)
    second, _ = app(("salir",), repository=repository)
    first.run(request(session_id="one"), now=NOW)
    second.run(request(session_id="two"), now=NOW)
    assert len(repository.list_all()) == 2


def test_duplicate_session_record_is_rejected():
    repository = InMemoryROBYConsoleRepository()
    application, _ = app(("salir",), repository=repository)
    session = application.run(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(session)


def test_custom_console_text_is_used():
    config = ROBYConsoleConfig(
        prompt="> ",
        assistant_prefix="H> ",
        pending_response="Pendiente.",
    )
    application, io = app(("Pregunta?", "salir"), config=config)
    application.run(request(), now=NOW)
    assert io.prompts == ["> ", "> "]
    assert io.outputs == ["H> Pendiente."]


def test_process_turn_can_be_used_without_interactive_loop():
    application, io = app()
    turn = application.process_turn(request(), "Hola", sequence=1, now=NOW)
    assert turn.status is ConsoleTurnStatus.DELIVERED
    assert io.outputs == []


def test_session_and_turns_are_immutable():
    application, _ = app(("Hola", "salir"))
    session = application.run(request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        session.status = ConsoleApplicationStatus.STARTED
    with pytest.raises(FrozenInstanceError):
        session.turns[0].response_text = "other"


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_readiness():
    with pytest.raises(ValueError, match="match readiness owner"):
        request(owner="Other")


def test_session_id_is_required():
    with pytest.raises(ValueError, match="session id"):
        request(session_id=" ")


def test_console_config_rejects_duplicate_exit_commands():
    with pytest.raises(ValueError, match="unique"):
        ROBYConsoleConfig(exit_commands=("exit", "EXIT"))


def test_console_config_rejects_non_positive_max_turns():
    with pytest.raises(ValueError, match="positive"):
        ROBYConsoleConfig(max_turns=0)


def test_console_requires_timezone_aware_timestamp():
    application, _ = app(("salir",))
    with pytest.raises(ValueError, match="timezone-aware"):
        application.run(request(), now=NOW.replace(tzinfo=None))


def test_turn_identity_changes_with_timestamp():
    application, _ = app()
    first = application.process_turn(request(), "Hola", sequence=1, now=NOW)
    second = application.process_turn(
        request(),
        "Hola",
        sequence=1,
        now=NOW.astimezone(timezone.utc).replace(microsecond=1),
    )
    assert first.turn_id != second.turn_id


def test_standard_console_adapter_is_importable_without_side_effects():
    from interfaces.cli.roby_console import StandardConsoleIO

    assert callable(StandardConsoleIO().read)
    assert callable(StandardConsoleIO().write)
