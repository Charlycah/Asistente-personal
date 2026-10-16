from __future__ import annotations

from app.desktop_ui import DesktopUIConfig
from app.household_conversation_style import HouseholdConversationStyle
from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import InterlocutorResolutionStatus


class Turn:
    response_text = "respuesta normal"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False
    response_path = "interceptor"
    degradation_reason = "not_applicable"


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def __init__(self) -> None:
        self.calls = 0
        self.private_context_allowed: list[bool] = []

    def converse(self, text: str) -> Turn:
        from core.cognitive_maturity import IdentityContextAccessGate

        self.calls += 1
        self.private_context_allowed.append(
            IdentityContextAccessGate.current().private_context_allowed
        )
        return Turn()


def test_pi1_resolved_carlos_continues_without_identity_prompt() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    brain = UnifiedBrain(gateway)
    brain.process("Confirmo que soy Carlos", session_id="main")

    turn = brain.process("¿Que hacemos hoy?", session_id="main")
    state = gateway.interlocutor_sessions.states[0]

    assert state.status is InterlocutorResolutionStatus.RESOLVED
    assert state.interlocutor.value == "Carlos"
    assert turn.response_text == "respuesta normal"
    assert runtime.calls == 1
    assert runtime.private_context_allowed == [True]


def test_pi2_cristina_identity_remains_isolated_from_carlos() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    brain = UnifiedBrain(gateway)
    brain.process("Confirmo que soy Carlos", session_id="carlos-session")
    brain.process("Confirmo que soy Cristina", session_id="cristina-session")

    states = {item.session_id: item for item in gateway.interlocutor_sessions.states}
    assert states["carlos-session"].interlocutor.value == "Carlos"
    assert states["cristina-session"].interlocutor.value == "Cristina"


def test_pi3_unknown_identity_is_invited_but_does_not_block_runtime() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    turn = UnifiedBrain(gateway).process("Buen dia", session_id="new-session")

    assert DesktopUIConfig().greeting == "¿Con quien estoy conversando?"
    assert turn.response_text == "respuesta normal"
    assert runtime.calls == 1
    assert runtime.private_context_allowed == [False]


def test_pi4_explicit_identification_establishes_later_continuity() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    brain = UnifiedBrain(gateway)

    pending = brain.process("Soy Carlos", session_id="main")
    resolved = brain.process("Confirmo que soy Carlos", session_id="main")
    later = brain.process("Seguimos", session_id="main")

    assert "Confirmo que soy Carlos" in pending.response_text
    assert "Identidad confirmada" in resolved.response_text
    assert later.response_text == "respuesta normal"
    assert gateway.interlocutor_sessions.states[0].interlocutor.value == "Carlos"
    assert runtime.private_context_allowed == [True]


def test_pi5_ambiguous_identity_is_not_guessed_and_runtime_remains_available() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    turn = UnifiedBrain(gateway).process("Soy yo", session_id="unknown-session")

    assert turn.response_text == "respuesta normal"
    assert runtime.calls == 1
    assert runtime.private_context_allowed == [False]
    assert all(
        item.status is not InterlocutorResolutionStatus.RESOLVED
        for item in gateway.interlocutor_sessions.states
    )


def test_pi6_household_prompt_suppresses_irrelevant_self_reference() -> None:
    prompt = HouseholdConversationStyle().system_prompt.casefold()

    assert "no menciones tu identidad salvo" in prompt
    assert "no empieces respuestas ordinarias con soy roby" in prompt


def test_pi7_household_prompt_preserves_legitimate_identity_answers() -> None:
    prompt = HouseholdConversationStyle().system_prompt.casefold()

    assert "sos roby" in prompt
    assert "tu nombre" in prompt
    assert "usuario pregunte por tu nombre, identidad o rol" in prompt


def test_pi8_calling_roby_by_roby_does_not_trigger_name_correction() -> None:
    prompt = HouseholdConversationStyle().system_prompt.casefold()

    assert "si el usuario te llama roby u otro nombre, corregilo" not in prompt
    assert "otro nombre distinto de roby" in prompt
