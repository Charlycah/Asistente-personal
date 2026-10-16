from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class DictationAction(str, Enum):
    NOT_HANDLED = "not_handled"
    STARTED = "started"
    UPDATED = "updated"
    PAUSED = "paused"
    RESUMED = "resumed"
    UNDONE = "undone"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    EMPTY = "empty"


@dataclass(frozen=True)
class DictationResult:
    handled: bool
    action: DictationAction = DictationAction.NOT_HANDLED
    message: str = ""
    document: str = ""
    active: bool = False


class IntelligentDictationSession:
    """Stateful, local dictation session independent from conversational routing."""

    _START_COMMANDS = {
        "iniciar dictado",
        "inicia dictado",
        "empezar dictado",
        "empeza dictado",
        "comenzar dictado",
        "comenza dictado",
        "modo dictado",
        "activar dictado",
        "activa dictado",
    }
    _FINISH_COMMANDS = {
        "terminar dictado",
        "termina dictado",
        "finalizar dictado",
        "finaliza dictado",
        "guardar dictado",
        "guarda dictado",
    }
    _CANCEL_COMMANDS = {
        "cancelar dictado",
        "cancela dictado",
        "descartar dictado",
        "descarta dictado",
    }
    _PAUSE_COMMANDS = {"pausar dictado", "pausa dictado"}
    _RESUME_COMMANDS = {
        "continuar dictado",
        "continua dictado",
        "reanudar dictado",
        "reanuda dictado",
    }
    _UNDO_COMMANDS = {
        "deshacer ultima frase",
        "borra ultima frase",
        "borrar ultima frase",
        "elimina ultima frase",
    }

    def __init__(self) -> None:
        self._segments: list[str] = []
        self._active = False
        self._paused = False

    @property
    def active(self) -> bool:
        return self._active

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def document(self) -> str:
        return self._join_segments(self._segments)

    def handle(self, text: str) -> DictationResult:
        raw = text.strip()
        normalized = self._normalize_command(raw)

        if not self._active:
            if normalized not in self._START_COMMANDS:
                return DictationResult(False)
            self._segments.clear()
            self._active = True
            self._paused = False
            return self._result(
                DictationAction.STARTED,
                "Modo dictado iniciado. Decime el texto y usaré órdenes como "
                "punto, coma, nueva línea y nuevo párrafo.",
            )

        if normalized in self._CANCEL_COMMANDS:
            self._reset()
            return DictationResult(
                True,
                DictationAction.CANCELLED,
                "Dictado cancelado. No conservé el texto.",
            )

        if normalized in self._FINISH_COMMANDS:
            document = self.document
            self._reset()
            if not document:
                return DictationResult(
                    True,
                    DictationAction.EMPTY,
                    "El dictado terminó sin texto.",
                )
            return DictationResult(
                True,
                DictationAction.FINISHED,
                "Dictado finalizado. El texto quedó disponible en la conversación.",
                document,
            )

        if normalized in self._PAUSE_COMMANDS:
            self._paused = True
            return self._result(DictationAction.PAUSED, "Dictado en pausa.")

        if normalized in self._RESUME_COMMANDS:
            self._paused = False
            return self._result(DictationAction.RESUMED, "Continúo con el dictado.")

        if normalized in self._UNDO_COMMANDS:
            if self._segments:
                self._segments.pop()
                return self._result(
                    DictationAction.UNDONE,
                    "Eliminé la última frase del dictado.",
                )
            return self._result(
                DictationAction.EMPTY,
                "Todavía no hay una frase para eliminar.",
            )

        if self._paused:
            return self._result(
                DictationAction.PAUSED,
                "El dictado está en pausa. Decí ‘continuar dictado’ para seguir.",
            )

        segment = self._format_spoken_text(raw)
        if not segment:
            return self._result(DictationAction.EMPTY, "No detecté texto para agregar.")
        self._segments.append(segment)
        return self._result(DictationAction.UPDATED, "Texto agregado al dictado.")

    def _result(self, action: DictationAction, message: str) -> DictationResult:
        return DictationResult(
            True,
            action,
            message,
            self.document,
            self._active,
        )

    def _reset(self) -> None:
        self._segments.clear()
        self._active = False
        self._paused = False

    @staticmethod
    def _normalize_command(text: str) -> str:
        decomposed = unicodedata.normalize("NFKD", text.casefold())
        without_accents = "".join(
            char for char in decomposed if not unicodedata.combining(char)
        )
        without_wake = re.sub(
            r"^(?:roby|robi|robby|robbie|ruby|rubi)[,:;.!?\s-]+",
            "",
            without_accents,
        )
        cleaned = re.sub(r"[^a-z0-9ñ\s]", " ", without_wake)
        return re.sub(r"\s+", " ", cleaned).strip()

    @classmethod
    def _format_spoken_text(cls, text: str) -> str:
        formatted = text.strip()
        replacements = (
            (r"\bnuevo párrafo\b", "\n\n"),
            (r"\bnuevo parrafo\b", "\n\n"),
            (r"\bnueva línea\b", "\n"),
            (r"\bnueva linea\b", "\n"),
            (r"\bpunto y coma\b", ";"),
            (r"\bdos puntos\b", ":"),
            (r"\bsigno de interrogación\b", "?"),
            (r"\bsigno de interrogacion\b", "?"),
            (r"\bsigno de exclamación\b", "!"),
            (r"\bsigno de exclamacion\b", "!"),
            (r"\bpunto\b", "."),
            (r"\bcoma\b", ","),
        )
        for pattern, replacement in replacements:
            formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)
        formatted = re.sub(r"\s+([,.;:!?])", r"\1", formatted)
        formatted = re.sub(r"([,.;:!?])(?=[^\s\n])", r"\1 ", formatted)
        formatted = re.sub(r"[ \t]+", " ", formatted)
        formatted = re.sub(r" *\n *", "\n", formatted)
        formatted = re.sub(r"\n{3,}", "\n\n", formatted)
        return formatted.strip()

    @staticmethod
    def _join_segments(segments: list[str]) -> str:
        document = ""
        for segment in segments:
            if not document:
                document = segment
                continue
            if document.endswith(("\n", " ")) or segment.startswith(
                ("\n", ",", ".", ";", ":", "!", "?")
            ):
                document += segment
            else:
                document += " " + segment
        return document.strip()
