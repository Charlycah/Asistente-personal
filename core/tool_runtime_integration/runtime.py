from __future__ import annotations

import json
from collections.abc import Mapping

from core.llm_provider import LLMRequest
from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest

from .models import (
    ToolRuntimeConfig,
    ToolRuntimeContext,
    ToolRuntimeInvocation,
    ToolRuntimeStatus,
)


class ToolRuntimeIntegration:
    """Governed, explicit bridge from operational turns to M61 tools."""

    def __init__(
        self,
        gateway: ToolGatewayManager,
        *,
        config: ToolRuntimeConfig | None = None,
    ) -> None:
        self.gateway = gateway
        self.config = config or ToolRuntimeConfig()
        self._history: list[ToolRuntimeContext] = []

    @property
    def history(self) -> tuple[ToolRuntimeContext, ...]:
        return tuple(self._history)

    @property
    def last_context(self) -> ToolRuntimeContext | None:
        return self._history[-1] if self._history else None

    def enrich(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
    ) -> ToolRuntimeContext:
        normalized_owner = owner.strip()
        normalized_session = session_id.strip()
        if not normalized_owner or not normalized_session:
            raise ValueError("tool runtime owner and session must not be blank")
        if not self.config.enabled:
            return self._record(
                ToolRuntimeContext(
                    normalized_owner,
                    normalized_session,
                    ToolRuntimeStatus.NOT_REQUESTED,
                    request,
                    rationale=("tool_runtime_disabled",),
                )
            )
        parsed = self._parse(text)
        if parsed is None:
            self.gateway.observe_turn(text)
            return self._record(
                ToolRuntimeContext(
                    normalized_owner,
                    normalized_session,
                    ToolRuntimeStatus.NOT_REQUESTED,
                    request,
                )
            )
        capability_name, payload = parsed
        capability = self.gateway.capabilities.get(capability_name)
        if capability is not None and self._is_mutating(capability.metadata):
            if not self.config.allow_platform_mutation:
                invocation = ToolRuntimeInvocation(
                    normalized_owner,
                    normalized_session,
                    capability_name,
                    payload,
                    text,
                )
                return self._record(
                    ToolRuntimeContext(
                        normalized_owner,
                        normalized_session,
                        ToolRuntimeStatus.BLOCKED,
                        request,
                        invocation=invocation,
                        rationale=("platform_mutation_not_allowed",),
                    )
                )
        invocation = ToolRuntimeInvocation(
            normalized_owner,
            normalized_session,
            capability_name,
            payload,
            text,
        )
        result = self.gateway.execute(
            ToolRequest(
                capability_name=capability_name,
                payload=payload,
                reason="explicit_local_runtime_command",
                source="operational_runtime_m184",
                request_id=invocation.invocation_id,
            )
        )
        if result.normalized_status is ToolGatewayStatus.ROUTED:
            status = ToolRuntimeStatus.EXECUTED
            rationale = ("tool_executed_through_gateway",)
            enriched = self._enrich_request(request, capability_name, result.output)
        elif result.normalized_status is ToolGatewayStatus.BLOCKED:
            status = ToolRuntimeStatus.BLOCKED
            rationale = (result.error or "tool_execution_blocked",)
            enriched = request
        else:
            status = ToolRuntimeStatus.FAILED
            rationale = (result.error or "tool_execution_failed",)
            enriched = request
        return self._record(
            ToolRuntimeContext(
                normalized_owner,
                normalized_session,
                status,
                enriched,
                invocation=invocation,
                gateway_result=result,
                rationale=rationale,
            )
        )

    def _parse(self, text: str) -> tuple[str, Mapping[str, object]] | None:
        normalized = text.strip()
        prefix = self.config.command_prefix
        if not normalized.startswith(prefix):
            return None
        remainder = normalized[len(prefix) :].strip()
        if not remainder:
            raise ValueError("tool runtime command requires a capability")
        capability, separator, raw_payload = remainder.partition(" ")
        raw_payload = raw_payload.strip() if separator else "{}"
        if len(raw_payload) > self.config.maximum_payload_characters:
            raise ValueError("tool runtime payload exceeds configured limit")
        try:
            payload = json.loads(raw_payload or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("tool runtime payload must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("tool runtime payload must be a JSON object")
        return capability, payload

    def _enrich_request(
        self,
        request: LLMRequest,
        capability_name: str,
        output: Mapping[str, object],
    ) -> LLMRequest:
        if not self.config.include_output_in_prompt:
            return request
        rendered = json.dumps(output, ensure_ascii=False, sort_keys=True)
        prompt = (
            f"{request.prompt}\n\n"
            "Resultado gobernado de herramienta local:\n"
            f"- Capacidad: {capability_name}\n"
            f"- Salida: {rendered}\n"
            "Usa esta salida como evidencia del turno; no inventes campos ausentes."
        )
        return LLMRequest(
            prompt=prompt,
            system_prompt=request.system_prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            metadata={
                **request.metadata,
                "tool_context": "included",
                "tool_capability": capability_name,
            },
        )

    def _record(self, context: ToolRuntimeContext) -> ToolRuntimeContext:
        self._history.append(context)
        return context

    @staticmethod
    def _is_mutating(metadata: Mapping[str, str]) -> bool:
        return metadata.get("side_effect", "read").casefold() not in {
            "none",
            "read",
            "read_only",
        }
