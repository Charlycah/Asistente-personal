from __future__ import annotations

import ast
from pathlib import Path

from app.cognitive_runtime_sources import (
    OperationalCognitiveSource,
)
from app.voice_input import VoiceRequestTranscriber


def test_cognitive_runtime_uses_one_shared_source_adapter() -> None:
    source = OperationalCognitiveSource()

    adapters = (
        source.reasoning,
        source.planning,
        source.reflection,
        source.coordination,
    )

    assert all(callable(source_callable) for source_callable in adapters)


def test_removed_ceremonial_cognitive_adapter_classes_do_not_return() -> None:
    module = ast.parse(Path("app/cognitive_runtime_sources.py").read_text())
    class_names = {node.name for node in module.body if isinstance(node, ast.ClassDef)}

    assert class_names.isdisjoint(
        {
            "ReasoningSourceAdapter",
            "PlanningSourceAdapter",
            "ReflectionSourceAdapter",
            "ExecutiveCoordinationSourceAdapter",
        }
    )


def test_voice_request_transcriber_does_not_add_a_safe_wrapper_level() -> None:
    class FixedVoiceInput:
        def transcribe(self) -> str:
            return "  hola  "

    voice_input = FixedVoiceInput()
    transcriber = VoiceRequestTranscriber(voice_input)

    assert transcriber.voice_input is voice_input
    assert transcriber.transcribe() == "hola"


def test_natural_language_pending_flow_calls_repository_directly() -> None:
    source = Path("application/reminders/natural_language.py").read_text()

    assert "repository.list_pending()" in source
    assert "ListPendingRemindersUseCase(repository).execute()" not in source
