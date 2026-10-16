from __future__ import annotations

from .models import RuntimeObservation, TurnObservation


class DevelopmentConsoleRenderer:
    def render_runtime(self, item: RuntimeObservation) -> tuple[str, ...]:
        started = item.started_at.isoformat() if item.started_at else "-"
        modules = ", ".join(item.composed_modules) or "not-composed"
        return (
            (
                f"runtime status={item.status} owner={item.owner} "
                f"session={item.session_id}"
            ),
            f"started_at={started} turns={item.turn_count} traces={item.trace_count}",
            f"composition={modules}",
        )

    def render_turn(
        self, item: TurnObservation, *, reveal_prompt: bool = False
    ) -> tuple[str, ...]:
        modules = ", ".join(item.modules) or "untraced"
        flags = (
            f"provider={self._flag(item.provider_call_performed)} "
            f"retrieval={self._flag(item.retrieval_performed)} "
            f"network={self._flag(item.network_access_performed)} "
            f"mutation={self._flag(item.platform_mutation_performed)}"
        )
        summary = (
            f"turn={item.sequence} status={item.status} events={item.event_count} "
            f"terminal={item.terminal_event}",
            f"modules={modules}",
            flags,
            f"turn_id={item.turn_id}",
            f"trace_id={item.trace_id or '-'}",
            f"pipeline_result_id={item.pipeline_result_id}",
            f"operational_response_id={item.operational_response_id}",
            (
                f"context turns={item.context_turns} chars={item.context_characters} "
                f"current={item.current_message_characters}"
            ),
            (
                "context_sanitizer "
                f"input={item.context_input_turns} "
                f"sanitized={item.context_sanitized_turns} "
                f"reserved_removed={item.context_reserved_removed_turns} "
                f"curation_removed={item.context_curation_dropped_turns}"
            ),
            (
                f"context_sources journal={self._flag(item.context_from_journal)} "
                f"memory={self._flag(item.context_from_persistent_memory)} "
                f"retrieval={self._flag(item.context_from_retrieval)} "
                f"tools={self._flag(item.context_from_tools)}"
            ),
            (
                f"llm_request prompt_chars={item.prompt_characters} "
                f"system_chars={item.system_prompt_characters}"
            ),
            (
                f"llm_messages transport={item.message_transport} "
                f"total={len(item.inference_messages)} "
                f"system={item.system_message_count} "
                f"user={item.user_message_count} "
                f"assistant={item.assistant_message_count}"
            ),
            (
                f"provider_payload provider={item.provider_name or '-'} "
                f"model={item.model_name or '-'} "
                f"transport={item.message_transport} "
                f"endpoint={item.provider_endpoint_path or '-'} "
                f"prompt_chars={item.prompt_characters}"
            ),
            (
                "provider_message_roles="
                + (",".join(item.provider_message_roles) or "-")
            ),
            (
                "inference_request_roles="
                + (",".join(item.provider_message_roles) or "-")
            ),
            (
                "effective_provider_payload "
                f"endpoint={item.effective_provider_endpoint_path or '-'} "
                "roles="
                + (",".join(item.effective_provider_message_roles) or "-")
                + f" system={item.effective_provider_system_message_count} "
                f"system_chars={item.effective_system_prompt_characters} "
                "request_system_included="
                f"{self._flag(item.request_system_prompt_included)}"
            ),
        )
        if not reveal_prompt:
            return summary
        prompt_lines = tuple(
            f"llm_prompt| {line}" for line in item.inference_prompt.splitlines()
        )
        message_lines = tuple(
            f"llm_message| {role}: {content}"
            for role, content in item.inference_messages
        )
        return (
            *summary,
            "effective_provider_payload_verified",
            "llm_prompt_begin",
            *prompt_lines,
            "llm_prompt_end",
            "llm_messages_begin",
            "provider_messages_begin",
            *message_lines,
            "llm_messages_end",
            "provider_messages_end",
            "provider_transport_verified",
        )

    @staticmethod
    def _flag(value: bool) -> str:
        return "yes" if value else "no"
