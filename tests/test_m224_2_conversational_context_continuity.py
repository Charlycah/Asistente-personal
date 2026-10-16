from __future__ import annotations

from datetime import datetime, timezone

from app.runtime_root_factory import EnvironmentInferenceRequestPort
from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.end_to_end_local_conversation import (
    EndToEndLocalConversation,
    EndToEndLocalConversationConfig,
)
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)
from core.local_runtime_bootstrap import (
    LocalRuntimeBootstrap,
    LocalRuntimeBootstrapConfig,
)
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m178_runtime_composition_root import RecordingProvider, dependencies

NOW = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def runtime(
    tmp_path,
    *,
    provider: RecordingProvider,
    owner: str = "Carlos",
    session_id: str = "desktop-main",
    maximum_turns: int = 8,
    maximum_characters: int = 12_000,
) -> EndToEndLocalConversation:
    bootstrap = LocalRuntimeBootstrap(
        root=RuntimeCompositionRoot(dependencies(provider=provider)),
        config=LocalRuntimeBootstrapConfig(
            owner=owner,
            session_id=session_id,
            state_path=tmp_path / f"runtime-{owner}-{session_id}.json",
        ),
    )
    return EndToEndLocalConversation(
        bootstrap=bootstrap,
        config=EndToEndLocalConversationConfig(
            journal_path=tmp_path / "turns.jsonl",
            maximum_recent_context_turns=maximum_turns,
            maximum_recent_context_characters=maximum_characters,
        ),
    )


def test_inference_request_includes_recent_context_before_current_message():
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="desktop-main",
        text="¿Cómo me llamo?",
        recent_context=(
            ConversationalContextTurn(
                user_text="Mi nombre es Carlos.",
                assistant_text="Mucho gusto, Carlos.",
            ),
        ),
    )

    built = enrich_with_recent_conversation_context(
        conversation=request,
        inference_request=EnvironmentInferenceRequestPort().build(request),
    )

    assert built.prompt == (
        "Contexto conversacional reciente de esta misma sesión:\n"
        "Usuario: Mi nombre es Carlos.\n"
        "ROBY: Mucho gusto, Carlos.\n\n"
        "Usuario: ¿Cómo me llamo?\n"
        "ROBY:"
    )
    assert built.metadata["conversation_context_turns"] == "1"


def test_second_turn_reconstructs_context_from_journal(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)

    item.converse("Mi nombre es Carlos.", now=NOW)
    item.converse("¿Cómo me llamo?", now=NOW)

    second_request = provider.calls[1]
    assert "Usuario: Mi nombre es Carlos." in second_request.prompt
    assert "ROBY: Hola desde el proveedor local." in second_request.prompt
    assert second_request.prompt.endswith("Usuario: ¿Cómo me llamo?\nROBY:")


def test_context_survives_runtime_recreation(tmp_path):
    first_provider = RecordingProvider()
    first = runtime(tmp_path, provider=first_provider)
    first.bootstrap.start(now=NOW)
    first.converse("Mi nombre es Carlos.", now=NOW)
    first.bootstrap.stop(now=NOW)

    second_provider = RecordingProvider()
    second = runtime(tmp_path, provider=second_provider)
    second.bootstrap.start(now=NOW)
    second.converse("¿Cómo me llamo?", now=NOW)

    assert "Mi nombre es Carlos." in second_provider.calls[0].prompt


def test_context_is_isolated_by_session(tmp_path):
    first_provider = RecordingProvider()
    first = runtime(tmp_path, provider=first_provider, session_id="session-a")
    first.bootstrap.start(now=NOW)
    first.converse("Secreto de sesión A", now=NOW)

    second_provider = RecordingProvider()
    second = runtime(tmp_path, provider=second_provider, session_id="session-b")
    second.bootstrap.start(now=NOW)
    second.converse("¿Qué dije antes?", now=NOW)

    assert second_provider.calls[0].prompt == "¿Qué dije antes?"


def test_context_request_carries_no_foreign_owner_turns(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider, owner="Carlos")
    item.bootstrap.start(now=NOW)
    item.converse("Dato privado de Carlos", now=NOW)

    assert item.journal.list_for_session("Ana", "desktop-main") == ()


def test_context_turn_limit_keeps_only_most_recent_turns(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider, maximum_turns=2)
    item.bootstrap.start(now=NOW)
    item.converse("turno uno", now=NOW)
    item.converse("turno dos", now=NOW)
    item.converse("turno tres", now=NOW)
    item.converse("turno cuatro", now=NOW)

    prompt = provider.calls[3].prompt
    assert "turno uno" not in prompt
    assert "turno dos" in prompt
    assert "turno tres" in prompt
    assert prompt.endswith("Usuario: turno cuatro\nROBY:")


def test_context_can_be_disabled_without_changing_single_turn_prompt(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider, maximum_turns=0)
    item.bootstrap.start(now=NOW)
    item.converse("uno", now=NOW)
    item.converse("dos", now=NOW)

    assert provider.calls[1].prompt == "dos"
    assert "conversation_context_turns" not in provider.calls[1].metadata
