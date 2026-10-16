from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Protocol
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from core.llm_provider import LLMRequest, LLMResponse


class HttpResponse(Protocol):
    status_code: int
    text: str

    def json(self) -> dict[str, Any]: ...


HttpPost = Callable[..., HttpResponse]


@dataclass(frozen=True)
class SimpleHttpResponse:
    status_code: int
    text: str
    payload: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return dict(self.payload)


def _default_post(
    url: str,
    *,
    json_payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> SimpleHttpResponse:
    encoded_body = json.dumps(json_payload).encode("utf-8")
    req = urllib_request.Request(
        url,
        data=encoded_body,
        headers=headers or {},
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8")
            payload = json.loads(raw_body) if raw_body else {}
            return SimpleHttpResponse(
                status_code=response.status,
                text=raw_body,
                payload=payload,
            )
    except HTTPError as exc:
        raw_error = exc.read().decode("utf-8")
        return SimpleHttpResponse(
            status_code=exc.code,
            text=raw_error,
            payload={},
        )
    except (OSError, URLError) as exc:
        return SimpleHttpResponse(
            status_code=0,
            text=str(exc),
            payload={},
        )


def _build_prompt(request: LLMRequest) -> str:
    if request.messages:
        labels = {"system": "Sistema", "user": "Usuario", "assistant": "ROBY"}
        return "\n".join(
            f"{labels[item.role]}: {item.content}" for item in request.messages
        )
    if not request.system_prompt:
        return request.prompt

    return f"{request.system_prompt.strip()}\n\n{request.prompt}".strip()


def _chat_messages(request: LLMRequest) -> list[dict[str, str]]:
    if request.messages:
        return [
            {"role": item.role, "content": item.content} for item in request.messages
        ]
    messages = []
    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt.strip()})
    messages.append({"role": "user", "content": request.prompt})
    return messages


def _safe_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


class OllamaProvider:
    """Proveedor local compatible con el contrato LLM de ROBY."""

    name = "ollama"

    def __init__(
        self,
        *,
        endpoint: str = "http://localhost:11434/api/generate",
        default_model: str = "llama3",
        http_post: HttpPost | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.endpoint = endpoint
        self.default_model = default_model
        self._http_post = http_post or _default_post
        self._timeout = timeout

    def generate(self, request: LLMRequest) -> LLMResponse:
        model = request.model or self.default_model
        payload = {
            "model": model,
            "prompt": _build_prompt(request),
            "stream": False,
        }
        response = self._http_post(
            self.endpoint,
            json_payload=payload,
            headers={"Content-Type": "application/json"},
            timeout=self._timeout,
        )

        if response.status_code != 200:
            return LLMResponse(
                text="Ollama no aceptó la solicitud.",
                provider=self.name,
                model=model,
                accepted=False,
                error="ollama_http_error",
            )

        text = _safe_text(response.json().get("response"))
        if not text:
            return LLMResponse(
                text="Ollama no devolvió texto.",
                provider=self.name,
                model=model,
                accepted=False,
                error="empty_response",
            )

        return LLMResponse(text=text, provider=self.name, model=model)


class MistralProvider:
    """Proveedor remoto estilo OpenRouter/Mistral compatible con ROBY."""

    name = "mistral"

    def __init__(
        self,
        *,
        api_key: str,
        endpoint: str = "https://api.mistral.ai/v1/chat/completions",
        default_model: str = "mistral-7b-instruct",
        http_post: HttpPost | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.endpoint = endpoint
        self.default_model = default_model
        self._http_post = http_post or _default_post
        self._timeout = timeout

    def generate(self, request: LLMRequest) -> LLMResponse:
        model = request.model or self.default_model
        if not self.api_key:
            return LLMResponse(
                text="No hay API key configurada para Mistral.",
                provider=self.name,
                model=model,
                accepted=False,
                error="missing_api_key",
            )

        messages = _chat_messages(request)

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or 500,
            "temperature": (
                request.temperature if request.temperature is not None else 0.7
            ),
        }
        response = self._http_post(
            self.endpoint,
            json_payload=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self._timeout,
        )

        if response.status_code != 200:
            return LLMResponse(
                text="Mistral no aceptó la solicitud.",
                provider=self.name,
                model=model,
                accepted=False,
                error="mistral_http_error",
            )

        text = _extract_chat_completion_text(response.json())
        if not text:
            return LLMResponse(
                text="Mistral no devolvió texto.",
                provider=self.name,
                model=model,
                accepted=False,
                error="empty_response",
            )

        return LLMResponse(text=text, provider=self.name, model=model)


class GeminiProvider:
    """Proveedor remoto Gemini mediante la API REST oficial."""

    name = "gemini"

    def __init__(
        self,
        *,
        api_key: str = "",
        endpoint: str = "https://generativelanguage.googleapis.com/v1beta",
        default_model: str = "gemini-1.5-flash",
        http_post: HttpPost | None = None,
        timeout: float = 30.0,
        model_client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.default_model = default_model
        self._http_post = http_post or _default_post
        self._timeout = timeout
        self._model_client = model_client

    def generate(self, request: LLMRequest) -> LLMResponse:
        model = request.model or self.default_model
        if not self.api_key and self._model_client is None:
            return LLMResponse(
                text="No hay cliente Gemini configurado.",
                provider=self.name,
                model=model,
                accepted=False,
                error="missing_client",
            )
        if self._model_client is not None:
            response = self._model_client.generate_content(_build_prompt(request))
            text = _safe_text(getattr(response, "text", ""))
        else:
            payload = _gemini_payload(request)
            response = self._http_post(
                f"{self.endpoint}/models/{model}:generateContent?key={self.api_key}",
                json_payload=payload,
                headers={"Content-Type": "application/json"},
                timeout=self._timeout,
            )
            if response.status_code != 200:
                return LLMResponse(
                    text="Gemini no aceptó la solicitud.",
                    provider=self.name,
                    model=model,
                    accepted=False,
                    error="gemini_http_error",
                )
            text = _extract_gemini_text(response.json())

        if not text:
            return LLMResponse(
                text="Gemini no devolvió texto.",
                provider=self.name,
                model=model,
                accepted=False,
                error="empty_response",
            )
        return LLMResponse(text=text, provider=self.name, model=model)


def _gemini_payload(request: LLMRequest) -> dict[str, Any]:
    contents: list[dict[str, Any]] = []
    system_parts: list[str] = []
    if request.system_prompt:
        system_parts.append(request.system_prompt.strip())
    if request.messages:
        for message in request.messages:
            if message.role == "system":
                system_parts.append(message.content)
                continue
            role = "model" if message.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": message.content}]})
    else:
        contents.append({"role": "user", "parts": [{"text": request.prompt}]})
    payload: dict[str, Any] = {"contents": contents}
    if system_parts:
        payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}
    generation: dict[str, Any] = {}
    if request.max_tokens is not None:
        generation["maxOutputTokens"] = request.max_tokens
    if request.temperature is not None:
        generation["temperature"] = request.temperature
    if generation:
        payload["generationConfig"] = generation
    return payload


def _extract_gemini_text(payload: dict[str, Any]) -> str:
    try:
        candidates = payload.get("candidates", [])
        parts = candidates[0]["content"]["parts"]
        return "".join(
            _safe_text(part.get("text")) for part in parts if isinstance(part, dict)
        ).strip()
    except (AttributeError, IndexError, KeyError, TypeError):
        return ""


def _extract_chat_completion_text(payload: dict[str, Any]) -> str:
    try:
        choices = payload.get("choices", [])
        first_choice = choices[0]
        message = first_choice.get("message", {})
        return _safe_text(message.get("content"))
    except (AttributeError, IndexError, KeyError, TypeError):
        return ""
