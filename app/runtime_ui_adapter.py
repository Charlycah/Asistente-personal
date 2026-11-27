from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Protocol

from app.companion_expression_policy import CompanionExpressionPolicy
from app.conversational_quality_policy import ConversationalQualityPolicy
from app.official_conversation_gateway import (
    ConversationOrigin,
    OfficialConversationGateway,
)
from app.ui_adapter import UIResponse
from core.end_to_end_local_conversation import LocalConversationTurn
from app.unified_brain import UnifiedBrain, UnifiedBrainDiagnosticSnapshot
from app.weather_conversation_runtime import WeatherConversationInterceptionPort
from domain.response import ResponseStatus


@dataclass(frozen=True)
class TurnBoundUIResult:
    """UI response correlated with one conversation turn."""

    response: UIResponse
    turn: LocalConversationTurn | None
    applied_result: object | None = None

class InputRuntime(Protocol):
    def handle_input(self, user_input: str) -> object: ...


class RuntimeUIAdapter:
    """
    Adapta el runtime histórico de ROBY al contrato esperado por la interfaz.

    No construye dependencias.
    No interpreta intenciones.
    No contiene lógica conversacional.
    """

    def __init__(self, runtime: InputRuntime) -> None:
        self.runtime = runtime

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        normalized_text = text.strip()

        if not normalized_text:
            return UIResponse(
                text="Necesito que escribas un mensaje para continuar.",
                status=ResponseStatus.NEEDS_INFORMATION.value,
                session_id=session_id,
                needs_input=True,
            )

        try:
            result = self.runtime.handle_input(normalized_text)
        except Exception:
            # ROBY_DOCUMENT_ERROR_DIAGNOSTIC
            from app.roby_document_error_diagnostics import record_failure
            record_failure('app/runtime_ui_adapter.py:62')
            return UIResponse(
                text="Ocurrió un error al procesar tu mensaje.",
                status=ResponseStatus.FAILURE.value,
                session_id=session_id,
                needs_input=False,
            )

        return UIResponse(
            text=str(result),
            status=ResponseStatus.SUCCESS.value,
            session_id=session_id,
            needs_input=False,
        )


class LocalConversationUIAdapter:
    """Adapts the official local conversation runtime to the desktop UI."""

    def __init__(
        self,
        runtime,
        *,
        pending_memory_write_reader: Callable[[str], bool] | None = None,
        pending_memory_write_response_evaluator: Callable[..., object] | None = None,
        pending_memory_write_executor: Callable[..., object] | None = None,
    ) -> None:
        self.runtime = (
            runtime
            if isinstance(runtime, OfficialConversationGateway)
            else OfficialConversationGateway(runtime)
        )
        self._brain = UnifiedBrain(self.runtime)
        self._pending_memory_write_reader = pending_memory_write_reader
        self._pending_memory_write_response_evaluator = (
            pending_memory_write_response_evaluator
        )
        self._pending_memory_write_executor = pending_memory_write_executor
        self._last_memory_write_execution_authorization = None
        self._last_memory_write_execution_result = None

    def bind_pending_memory_write_authorization_transport(
        self,
        *,
        pending_memory_write_reader: Callable[[str], bool],
        pending_memory_write_response_evaluator: Callable[..., object],
        pending_memory_write_executor: Callable[..., object] | None = None,
    ) -> None:
        """Bind source-neutral Memory authorization transport after construction."""
        self._pending_memory_write_reader = pending_memory_write_reader
        self._pending_memory_write_response_evaluator = (
            pending_memory_write_response_evaluator
        )
        self._pending_memory_write_executor = pending_memory_write_executor

    @property
    def diagnostics(self) -> UnifiedBrainDiagnosticSnapshot:
        return self._brain.diagnostics

    @property
    def last_memory_write_execution_authorization(self):
        return self._last_memory_write_execution_authorization

    @property
    def last_memory_write_execution_result(self):
        return self._last_memory_write_execution_result

    @staticmethod
    def _memory_write_result_response(result, *, session_id: str) -> UIResponse:
        outcome = getattr(result.outcome, "value", str(result.outcome))
        responses = {
            "stored": "Bien, guardé ese aprendizaje en la memoria oficial.",
            "already_stored": (
                "Ese aprendizaje ya estaba guardado en la memoria oficial."
            ),
            "memory_unavailable": (
                "La autorización es válida, pero la memoria oficial "
                "no está disponible."
            ),
            "write_failed": (
                "La autorización es válida, pero no pude guardar ese aprendizaje."
            ),
            "review_required": (
                "No guardé ese aprendizaje porque la autorización exacta "
                "no pudo validarse."
            ),
            "rejected": "Entendido, no guardé ese aprendizaje.",
            "deferred": "De acuerdo, lo dejamos para más adelante.",
            "unclear": (
                "No guardé ese aprendizaje porque la autorización "
                "no fue suficientemente explícita."
            ),
            "abstain": (
                "No guardé ese aprendizaje porque no pude vincular "
                "la autorización."
            ),
        }
        text = responses.get(
            outcome,
            "No se completó la escritura gobernada en la memoria oficial.",
        )
        return UIResponse(
            text=text,
            status=ResponseStatus.SUCCESS.value,
            session_id=session_id,
            needs_input=False,
        )

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
        *,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> UIResponse:
        return self._submit_response(
            text,
            session_id=session_id,
            origin=ConversationOrigin.DESKTOP_TEXT,
            explicit_document_ids=explicit_document_ids,
            explicit_sources=explicit_sources,
            explicit_evidence_references=explicit_evidence_references,
            integrated_visual_context=integrated_visual_context,
        )

    def submit_voice(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        return self._submit_response(
            text,
            session_id=session_id,
            origin=ConversationOrigin.DESKTOP_VOICE,
        )

    def submit_text_with_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
        *,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> TurnBoundUIResult:
        return self._submit(
            text,
            session_id=session_id,
            origin=ConversationOrigin.DESKTOP_TEXT,
            explicit_document_ids=explicit_document_ids,
            explicit_sources=explicit_sources,
            explicit_evidence_references=explicit_evidence_references,
            integrated_visual_context=integrated_visual_context,
            _capture_causal=True,
        )

    def submit_voice_with_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
    ) -> TurnBoundUIResult:
        return self._submit(
            text,
            session_id=session_id,
            origin=ConversationOrigin.DESKTOP_VOICE,
            _capture_causal=True,
        )

    def _submit_response(self, *args, **kwargs) -> UIResponse:
        return self._submit(*args, **kwargs).response

    def _submit(
        self,
        text: str,
        *,
        session_id: str | None,
        origin: ConversationOrigin,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
        _capture_causal: bool = False,
    ) -> TurnBoundUIResult:
        normalized_text = text.strip()
        if not normalized_text:
            return TurnBoundUIResult(
                response=UIResponse(text='Necesito que escribas un mensaje para continuar.', status=ResponseStatus.NEEDS_INFORMATION.value, session_id=session_id, needs_input=True),
                turn=None,
            )
        self._last_memory_write_execution_authorization = None
        self._last_memory_write_execution_result = None
        if (
            session_id
            and self._pending_memory_write_reader is not None
            and self._pending_memory_write_response_evaluator is not None
            and self._pending_memory_write_reader(session_id)
        ):
            authorization = self._pending_memory_write_response_evaluator(
                session_id=session_id,
                response_text=normalized_text,
                human_response_reference=(
                    f"conversation:{origin.value}:{session_id}:"
                    "memory-write-execution-response"
                ),
            )
            self._last_memory_write_execution_authorization = authorization
            if (
                authorization is not None
                and self._pending_memory_write_executor is not None
            ):
                result = self._pending_memory_write_executor(
                    session_id=session_id,
                    authorization=authorization,
                )
                self._last_memory_write_execution_result = result
                if result is not None:
                    return TurnBoundUIResult(
                        response=self._memory_write_result_response(result, session_id=session_id),
                        turn=None,
                    )
        causal_observations = []

        def receive_causal_result(observed_turn, applied_result):
            causal_observations.append((observed_turn, applied_result))

        causal_kwargs = (
            {"_causal_result_receiver": receive_causal_result}
            if _capture_causal
            else {}
        )

        try:
            if (
                explicit_document_ids
                or explicit_sources
                or explicit_evidence_references
                or integrated_visual_context is not None
            ):
                turn = self._brain.process(
                    normalized_text,
                    origin=origin,
                    session_id=session_id,
                    explicit_document_ids=explicit_document_ids,
                    explicit_sources=explicit_sources,
                    explicit_evidence_references=explicit_evidence_references,
                    integrated_visual_context=integrated_visual_context,
                    **causal_kwargs,
                )
            else:
                turn = self._brain.process(
                    normalized_text,
                    origin=origin,
                    session_id=session_id,
                    **causal_kwargs,
                )
        except Exception:
            # ROBY_DOCUMENT_ERROR_DIAGNOSTIC
            from app.roby_document_error_diagnostics import record_failure
            record_failure('app/runtime_ui_adapter.py:321')
            return TurnBoundUIResult(
                response=UIResponse(text='Ocurrió un error al procesar tu mensaje.', status=ResponseStatus.FAILURE.value, session_id=session_id, needs_input=False),
                turn=None,
            )
        status = getattr(turn.status, "value", str(turn.status))
        needs_input = status in {"partial", "withheld"}
        response_text = turn.response_text or f"[{status}]"
        causal_applied_result = None
        if (
            _capture_causal
            and len(causal_observations) == 1
            and causal_observations[0][0] is turn
        ):
            causal_applied_result = causal_observations[0][1]

        result = TurnBoundUIResult(
            response=UIResponse(
                text=response_text,
                status=status,
                session_id=session_id or turn.session_id,
                needs_input=needs_input,
                silent=(
                    "local_music_playback_started_after_explicit_authorization"
                    in getattr(turn, "rationale", ())
                ),
            ),
            turn=turn,
            applied_result=causal_applied_result,
        )
        return result


class OptionalServiceGuardUIAdapter:
    """Prevents unverifiable answers for optional services that are not connected."""

    _WEATHER_TERMS = (
        "clima",
        "tiempo",
        "temperatura",
        "llueve",
        "lluvia",
        "pronóstico",
        "pronostico",
    )

    def __init__(self, adapter, *, weather_enabled: bool) -> None:
        self.adapter = adapter
        self.weather_enabled = weather_enabled

    @property
    def diagnostics(self) -> UnifiedBrainDiagnosticSnapshot | None:
        return getattr(self.adapter, "diagnostics", None)

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        normalized = text.strip().casefold()
        if (
            not self.weather_enabled
            and WeatherConversationInterceptionPort.is_weather_request(normalized)
        ):
            return UIResponse(
                text=(
                    "El servicio de clima todavía no está conectado. "
                    "Para darte condiciones actuales verificadas, activá OpenWeather "
                    "en .roby/config.json y vinculá su API key."
                ),
                status=ResponseStatus.NEEDS_INFORMATION.value,
                session_id=session_id,
                needs_input=True,
            )
        return self.adapter.submit_text(text, session_id=session_id)

    def submit_voice(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        return self.submit_text(text, session_id=session_id)

    def submit_text_with_turn_evidence(
        self, text: str, session_id: str | None = None
    ) -> TurnBoundUIResult:
        normalized = text.strip().casefold()
        if (
            not self.weather_enabled
            and WeatherConversationInterceptionPort.is_weather_request(normalized)
        ):
            return TurnBoundUIResult(
                response=UIResponse(
                    text=(
                        "El servicio de clima todavía no está conectado. "
                        "Para darte condiciones actuales verificadas, activá OpenWeather "
                        "en .roby/config.json y vinculá su API key."
                    ),
                    status=ResponseStatus.NEEDS_INFORMATION.value,
                    session_id=session_id,
                    needs_input=True,
                ),
                turn=None,
            )
        result = self.adapter.submit_text_with_turn_evidence(
            text, session_id=session_id
        )
        return TurnBoundUIResult(
            response=result.response,
            turn=result.turn,
            applied_result=getattr(result, "applied_result", None),
        )

    def submit_voice_with_turn_evidence(
        self, text: str, session_id: str | None = None
    ) -> TurnBoundUIResult:
        return self.submit_text_with_turn_evidence(
            text, session_id=session_id
        )


class ConversationalPersonalityUIAdapter:
    """Adds short-lived conversational context and a warmer household tone."""

    _THANKS_RE = re.compile(
        r"^\s*(?:no[, ]+)?(?:roby[, ]+)?gracias"
        r"(?:[, ]+roby)?[.!?]*\s*$",
        re.IGNORECASE,
    )
    _AFFIRMATIVE_RE = re.compile(
        r"^\s*(?:(?:si|sí|dale|bueno)(?:\s+(?:dale|contame|decime|mostrame))?"
        r"|(?:contame|decime|mostrame))(?:\s+roby)?[.!?]*\s*$",
        re.IGNORECASE,
    )
    _GREETING_RE = re.compile(
        r"^\s*(?:hola(?:\s+roby)?|buen(?:os|as)\s+"
        r"(?:d[ií]as|tardes|noches))(?:[, ]+como\s+(?:te\s+va|andas))?"
        r"[.!?¿¡ ]*$",
        re.IGNORECASE,
    )
    _WEATHER_FOLLOWUP_RE = re.compile(
        r"^\s*(?:¿?\s*)?(?:y\s+)?(?:(?:dame|decime|contame)\s+)?"
        r"(?:el\s+)?(?:pron[oó]stico|mañana|manana|"
        r"fin\s+de\s+semana|va\s+a\s+seguir\s+as[ií]|sigue\s+as[ií]|"
        r"va\s+a\s+llover|llueve\s+mañana)(?:\s+roby)?[?!.]*\s*$",
        re.IGNORECASE,
    )

    def __init__(self, adapter) -> None:
        self.adapter = adapter
        self._pending_by_session: dict[str, str] = {}
        self._expression_policy = CompanionExpressionPolicy()
        self._quality_policy = ConversationalQualityPolicy()

    @property
    def diagnostics(self) -> UnifiedBrainDiagnosticSnapshot | None:
        return getattr(self.adapter, "diagnostics", None)

    @staticmethod
    def _key(session_id: str | None) -> str:
        return session_id or "desktop-default"

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        key = self._key(session_id)
        normalized = text.strip()
        if self._THANKS_RE.match(normalized):
            self._pending_by_session.pop(key, None)
            return UIResponse(
                text="De nada.",
                status=ResponseStatus.SUCCESS.value,
                session_id=session_id,
                needs_input=False,
            )
        if self._GREETING_RE.match(normalized):
            self._pending_by_session.pop(key, None)
            return UIResponse(
                text="Hola. Todo tranquilo por acá. ¿Cómo andás vos?",
                status=ResponseStatus.SUCCESS.value,
                session_id=session_id,
                needs_input=False,
            )
        pending = self._pending_by_session.get(key)
        if self._AFFIRMATIVE_RE.match(normalized):
            pending = self._pending_by_session.pop(key, None)
            if pending == "weather_forecast":
                normalized = "decime el pronóstico extendido"
        elif (
            pending == "weather_forecast"
            and self._WEATHER_FOLLOWUP_RE.match(normalized)
        ):
            self._pending_by_session.pop(key, None)
            normalized = "decime el pronóstico extendido"

        response = self.adapter.submit_text(normalized, session_id=session_id)
        return self._decorate(response, request_text=normalized, key=key)

    def submit_voice(self, text: str, session_id: str | None = None) -> UIResponse:
        return self.submit_text(text, session_id=session_id)

    def _decorate(
        self, response: UIResponse, *, request_text: str, key: str
    ) -> UIResponse:
        if response.silent:
            return response
        text = self._expression_policy.apply(response.text.strip())
        text = self._quality_policy.apply(
            request_text=request_text,
            response_text=text,
        )
        lowered_request = request_text.casefold()
        is_forecast = any(
            term in lowered_request
            for term in ("pronóstico", "pronostico", "extendido")
        )
        is_current_weather = (
            not is_forecast
            and WeatherConversationInterceptionPort.is_weather_request(lowered_request)
            and "°c" in text.casefold()
        )
        if is_current_weather:
            self._pending_by_session[key] = "weather_forecast"
            offer = (
                "Si querés, también te cuento cómo viene el pronóstico "
                "para los próximos días."
            )
            if offer.casefold() not in text.casefold():
                text = f"{text}\n\n{offer}"
        elif is_forecast:
            self._pending_by_session.pop(key, None)

        return UIResponse(
            text=text,
            status=response.status,
            session_id=response.session_id,
            needs_input=response.needs_input,
        )

    def submit_text_with_turn_evidence(
        self, text: str, session_id: str | None = None
    ) -> TurnBoundUIResult:
        key = self._key(session_id)
        normalized = text.strip()

        if self._THANKS_RE.match(normalized):
            self._pending_by_session.pop(key, None)
            return TurnBoundUIResult(
                response=UIResponse(
                    text="De nada.",
                    status=ResponseStatus.SUCCESS.value,
                    session_id=session_id,
                    needs_input=False,
                ),
                turn=None,
            )

        if self._GREETING_RE.match(normalized):
            self._pending_by_session.pop(key, None)
            return TurnBoundUIResult(
                response=UIResponse(
                    text="Hola. Todo tranquilo por acá. ¿Cómo andás vos?",
                    status=ResponseStatus.SUCCESS.value,
                    session_id=session_id,
                    needs_input=False,
                ),
                turn=None,
            )

        pending = self._pending_by_session.get(key)
        if self._AFFIRMATIVE_RE.match(normalized):
            pending = self._pending_by_session.pop(key, None)
            if pending == "weather_forecast":
                normalized = "decime el pronóstico extendido"
        elif (
            pending == "weather_forecast"
            and self._WEATHER_FOLLOWUP_RE.match(normalized)
        ):
            self._pending_by_session.pop(key, None)
            normalized = "decime el pronóstico extendido"

        result = self.adapter.submit_text_with_turn_evidence(
            normalized, session_id=session_id
        )
        response = self._decorate(
            result.response, request_text=normalized, key=key
        )
        return TurnBoundUIResult(
            response=response,
            turn=result.turn,
            applied_result=getattr(result, "applied_result", None),
        )

    def submit_voice_with_turn_evidence(
        self, text: str, session_id: str | None = None
    ) -> TurnBoundUIResult:
        return self.submit_text_with_turn_evidence(
            text, session_id=session_id
        )
