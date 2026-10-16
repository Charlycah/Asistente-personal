from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RuntimeObservation:
    owner: str
    session_id: str
    status: str
    started_at: datetime | None
    turn_count: int
    trace_count: int
    composed_modules: tuple[str, ...]


@dataclass(frozen=True)
class TurnObservation:
    sequence: int
    status: str
    turn_id: str
    trace_id: str
    pipeline_result_id: str
    operational_response_id: str
    modules: tuple[str, ...]
    provider_call_performed: bool
    retrieval_performed: bool
    network_access_performed: bool
    platform_mutation_performed: bool
    event_count: int
    terminal_event: str
    context_turns: int = 0
    context_input_turns: int = 0
    context_sanitized_turns: int = 0
    context_reserved_removed_turns: int = 0
    context_curation_dropped_turns: int = 0
    context_characters: int = 0
    current_message_characters: int = 0
    prompt_characters: int = 0
    system_prompt_characters: int = 0
    provider_name: str = ""
    model_name: str = ""
    context_from_journal: bool = False
    context_from_persistent_memory: bool = False
    context_from_retrieval: bool = False
    context_from_tools: bool = False
    inference_prompt: str = ""
    inference_messages: tuple[tuple[str, str], ...] = ()
    message_transport: str = "prompt"
    system_message_count: int = 0
    user_message_count: int = 0
    assistant_message_count: int = 0
    provider_endpoint_path: str = ""
    provider_message_roles: tuple[str, ...] = ()
    effective_provider_endpoint_path: str = ""
    effective_provider_message_roles: tuple[str, ...] = ()
    effective_provider_system_message_count: int = 0
    effective_system_prompt_characters: int = 0
    request_system_prompt_included: bool = False
