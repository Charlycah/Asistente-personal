from __future__ import annotations

from core.end_to_end_local_conversation import EndToEndLocalConversation

from .models import RuntimeObservation, TurnObservation


class DevelopmentConsoleObserver:
    """Read-only projection over runtime, turns, and operational traces."""

    def __init__(self, runtime: EndToEndLocalConversation) -> None:
        self.runtime = runtime

    def runtime_observation(self) -> RuntimeObservation:
        bootstrap = self.runtime.bootstrap
        composition = bootstrap.composition or bootstrap.root.composition
        modules = ()
        if composition is not None:
            modules = tuple(
                name
                for name in composition.__dataclass_fields__
                if getattr(composition, name) is not None
            )
        return RuntimeObservation(
            owner=bootstrap.config.owner,
            session_id=bootstrap.config.session_id,
            status=bootstrap.state.status.value,
            started_at=bootstrap.state.started_at,
            turn_count=len(self.runtime.history),
            trace_count=len(self.runtime.traces),
            composed_modules=modules,
        )

    def last_turn(self) -> TurnObservation | None:
        history = self.runtime.history
        if not history:
            return None
        return self.turn_observation(history[-1].sequence)

    def turn_observation(self, sequence: int) -> TurnObservation | None:
        turn = next(
            (item for item in self.runtime.history if item.sequence == sequence), None
        )
        if turn is None:
            return None
        trace = next(
            (
                item
                for item in self.runtime.traces
                if item.events[0].turn_sequence == sequence
            ),
            None,
        )
        events = trace.events if trace is not None else ()
        terminal = events[-1] if events else None
        pipeline_event = next(
            (
                event
                for event in events
                if event.pipeline_result_id == turn.pipeline_result_id
            ),
            None,
        )
        composition = self.runtime.bootstrap.composition
        repository = (
            composition.conversation_pipeline.repository
            if composition is not None
            else None
        )
        pipeline_result = (
            repository.get(turn.pipeline_result_id) if repository is not None else None
        )
        preparation = (
            pipeline_result.preparation if pipeline_result is not None else None
        )
        provider_execution = (
            pipeline_result.provider_execution if pipeline_result is not None else None
        )
        inference_request = (
            provider_execution.request.inference_request
            if provider_execution is not None
            else preparation.inference_request
            if preparation is not None
            else None
        )
        metadata = inference_request.metadata if inference_request is not None else {}
        messages = (
            tuple(inference_request.messages) if inference_request is not None else ()
        )
        roles = tuple(item.role for item in messages)
        payload_observation = (
            provider_execution.provider_payload_observation
            if provider_execution is not None
            else None
        )
        effective_roles = (
            payload_observation.message_roles if payload_observation is not None else ()
        )
        context_turns = int(metadata.get("conversation_context_turns", "0"))
        context_characters = int(metadata.get("conversation_context_characters", "0"))
        return TurnObservation(
            sequence=turn.sequence,
            status=turn.status.value,
            turn_id=turn.turn_id,
            trace_id=trace.trace_id if trace is not None else "",
            pipeline_result_id=turn.pipeline_result_id,
            operational_response_id=turn.operational_response_id,
            modules=tuple(dict.fromkeys(event.module for event in events)),
            provider_call_performed=(
                pipeline_event.provider_call_performed
                if pipeline_event is not None
                else turn.provider_call_performed
            ),
            retrieval_performed=(
                pipeline_event.retrieval_performed
                if pipeline_event is not None
                else turn.retrieval_performed
            ),
            network_access_performed=(
                pipeline_event.network_access_performed
                if pipeline_event is not None
                else turn.network_access_performed
            ),
            platform_mutation_performed=(
                pipeline_event.platform_mutation_performed
                if pipeline_event is not None
                else False
            ),
            event_count=len(events),
            terminal_event=terminal.event_type.value
            if terminal is not None
            else "untraced",
            context_turns=context_turns,
            context_input_turns=int(
                metadata.get("conversation_context_input_turns", "0")
            ),
            context_sanitized_turns=int(
                metadata.get("conversation_context_sanitized_turns", "0")
            ),
            context_reserved_removed_turns=int(
                metadata.get("conversation_context_reserved_removed_turns", "0")
            ),
            context_curation_dropped_turns=int(
                metadata.get("conversation_context_curation_dropped_turns", "0")
            ),
            context_characters=context_characters,
            current_message_characters=len(turn.user_text),
            prompt_characters=len(inference_request.prompt) if inference_request else 0,
            system_prompt_characters=(
                len(inference_request.system_prompt or "") if inference_request else 0
            ),
            provider_name=(
                provider_execution.selected_provider_name if provider_execution else ""
            ),
            model_name=(
                provider_execution.selected_model_name if provider_execution else ""
            ),
            context_from_journal=context_turns > 0,
            context_from_persistent_memory=(
                "memory_context" in metadata or "memory_runtime" in metadata
            ),
            context_from_retrieval=(
                pipeline_result.retrieval_execution is not None
                if pipeline_result is not None
                else False
            ),
            context_from_tools=any(key.startswith("tool_") for key in metadata),
            inference_prompt=inference_request.prompt if inference_request else "",
            inference_messages=tuple((item.role, item.content) for item in messages),
            message_transport="messages" if messages else "prompt",
            system_message_count=roles.count("system"),
            user_message_count=roles.count("user"),
            assistant_message_count=roles.count("assistant"),
            provider_endpoint_path=("/chat/completions" if messages else "/generate"),
            provider_message_roles=roles,
            effective_provider_endpoint_path=(
                payload_observation.endpoint_path
                if payload_observation is not None
                else ""
            ),
            effective_provider_message_roles=effective_roles,
            effective_provider_system_message_count=effective_roles.count("system"),
            effective_system_prompt_characters=(
                payload_observation.effective_system_prompt_characters
                if payload_observation is not None
                else 0
            ),
            request_system_prompt_included=(
                payload_observation.request_system_prompt_included
                if payload_observation is not None
                else False
            ),
        )
