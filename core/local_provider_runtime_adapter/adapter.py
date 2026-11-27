from __future__ import annotations

from threading import Event
from time import monotonic
from typing import Any

from core.gui06_diagnostic_probe import capture_diagnostic_stage
from core.llm_provider import LLMRequest, LLMResponse, ProviderPayloadObservation

from .models import (
    LocalProviderRuntimeHealth,
    LocalProviderRuntimeSettings,
    LocalProviderRuntimeState,
)
from .transport import (
    LocalProviderTransport,
    LocalProviderTransportError,
    UrllibLocalProviderTransport,
)


class LocalProviderRuntimeAdapter:
    """OpenAI-compatible local provider boundary for ROBY's governed runtime."""

    def __init__(
        self,
        settings: LocalProviderRuntimeSettings,
        *,
        transport: LocalProviderTransport | None = None,
    ) -> None:
        self.settings = settings
        self.name = settings.provider_name
        self._transport = transport or UrllibLocalProviderTransport()
        self._cancel_event = Event()
        self._last_payload_observation: ProviderPayloadObservation | None = None

    def cancel(self) -> None:
        self._cancel_event.set()

    def reset_cancellation(self) -> None:
        self._cancel_event.clear()

    @property
    def last_payload_observation(self) -> ProviderPayloadObservation | None:
        return self._last_payload_observation

    def health(self) -> LocalProviderRuntimeHealth:
        started = monotonic()
        try:
            response = self._transport.request(
                method="GET",
                url=f"{self.settings.endpoint}/models",
                headers=self._headers(),
                payload=None,
                timeout=self.settings.health_timeout_seconds,
            )
            models = self._extract_models(response.payload)
            state = LocalProviderRuntimeState.AVAILABLE
            error = None
            if self.settings.model and self.settings.model not in models:
                state = LocalProviderRuntimeState.MISCONFIGURED
                error = "model_unavailable"
            return LocalProviderRuntimeHealth(
                state=state,
                provider_name=self.name,
                endpoint=self.settings.endpoint,
                configured_model=self.settings.model,
                available_models=models,
                latency_ms=int((monotonic() - started) * 1000),
                error_code=error,
            )
        except LocalProviderTransportError as exc:
            return LocalProviderRuntimeHealth(
                state=LocalProviderRuntimeState.UNAVAILABLE,
                provider_name=self.name,
                endpoint=self.settings.endpoint,
                configured_model=self.settings.model,
                latency_ms=int((monotonic() - started) * 1000),
                error_code=exc.code,
            )

    def generate(self, request: LLMRequest) -> LLMResponse:
        self._last_payload_observation = None
        if self._cancel_event.is_set():
            return self._failure(request, "cancelled")
        model = (request.model or self.settings.model).strip()
        if not model:
            return self._failure(request, "missing_model")
        messages = self._messages(request)
        capture_diagnostic_stage("P2", messages=messages)
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        effective_system = self._effective_system_prompt(request)
        self._last_payload_observation = ProviderPayloadObservation(
            endpoint_path="/chat/completions",
            message_roles=tuple(str(item.get("role", "")) for item in messages),
            effective_system_prompt_characters=len(effective_system),
            request_system_prompt_included=(
                bool((request.system_prompt or "").strip())
                and (request.system_prompt or "").strip() in effective_system
            ),
        )
        max_tokens = request.max_tokens or self.settings.max_tokens
        temperature = (
            request.temperature
            if request.temperature is not None
            else self.settings.temperature
        )
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        try:
            response = self._transport.request(
                method="POST",
                url=f"{self.settings.endpoint}/chat/completions",
                headers=self._headers(),
                payload=payload,
                timeout=self.settings.timeout_seconds,
            )
        except LocalProviderTransportError as exc:
            return self._failure(request, exc.code, model=model)
        if self._cancel_event.is_set():
            return self._failure(request, "cancelled", model=model)
        text = self._extract_text(response.payload)
        capture_diagnostic_stage("P3", text=text)
        if not text:
            return self._failure(request, "invalid_response", model=model)
        response_model = str(response.payload.get("model") or model).strip()
        return LLMResponse(
            text=text,
            provider=self.name,
            model=response_model,
            accepted=True,
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        return headers

    def _messages(self, request: LLMRequest) -> list[dict[str, str]]:
        effective_system = self._effective_system_prompt(request)

        if request.messages:
            messages = [
                {"role": item.role, "content": item.content}
                for item in request.messages
            ]

            existing_system_contents = {
                item["content"] for item in messages if item["role"] == "system"
            }

            requested_system = (request.system_prompt or "").strip()
            configured_system = self.settings.system_prompt.strip()

            composed_system = (
                f"{configured_system}\n\n{requested_system}"
            )

            if (
                configured_system
                and requested_system
                and configured_system != requested_system
                and effective_system == composed_system
                and (
                    configured_system in existing_system_contents
                    or requested_system in existing_system_contents
                )
            ):
                required_systems = (
                    configured_system,
                    requested_system,
                )
            elif effective_system:
                required_systems = (effective_system,)
            else:
                required_systems = ()

            missing_systems = [
                system
                for system in required_systems
                if system not in existing_system_contents
            ]

            insertion_index = 0

            if (
                configured_system in existing_system_contents
                and requested_system in missing_systems
            ):
                insertion_index = next(
                    index + 1
                    for index, item in enumerate(messages)
                    if item["role"] == "system"
                    and item["content"] == configured_system
                )

            messages[insertion_index:insertion_index] = [
                {"role": "system", "content": system}
                for system in missing_systems
            ]

            return messages

        messages: list[dict[str, str]] = []
        if effective_system:
            messages.append({"role": "system", "content": effective_system})
        messages.append({"role": "user", "content": request.prompt.strip()})
        return messages

    def _effective_system_prompt(self, request: LLMRequest) -> str:
        configured_prompt = self.settings.system_prompt
        requested_prompt = request.system_prompt or ""

        from app.household_conversation_style import (
            DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
        )

        style = DEFAULT_HOUSEHOLD_CONVERSATION_STYLE
        english_style = style.system_prompt_for_language("en")

        if configured_prompt.strip() == style.system_prompt.strip() and (
            requested_prompt.strip() == english_style
            or requested_prompt.startswith(english_style + "\n\n")
        ):
            configured_prompt = ""

        elif (
            configured_prompt.strip() == style.system_prompt.strip()
            and (
                requested_prompt.strip() == style.system_prompt.strip()
                or requested_prompt.startswith(
                    style.system_prompt.strip() + "\n\n"
                )
            )
        ):
            configured_prompt = ""

        parts: list[str] = []
        for candidate in (configured_prompt, requested_prompt):
            normalized = candidate.strip()
            if normalized and normalized not in parts:
                parts.append(normalized)
        return "\n\n".join(parts)

    @staticmethod
    def _extract_models(payload: dict[str, Any]) -> tuple[str, ...]:
        items = payload.get("data", ())
        if not isinstance(items, list):
            return ()
        models = []
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                model = item["id"].strip()
                if model:
                    models.append(model)
        return tuple(dict.fromkeys(models))

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""
        first = choices[0]
        if not isinstance(first, dict):
            return ""
        message = first.get("message")
        if not isinstance(message, dict):
            return ""
        content = message.get("content")
        return content.strip() if isinstance(content, str) else ""

    def _failure(
        self,
        request: LLMRequest,
        error: str,
        *,
        model: str | None = None,
    ) -> LLMResponse:
        return LLMResponse(
            text="",
            provider=self.name,
            model=model or request.model or self.settings.model or None,
            accepted=False,
            error=error,
        )
