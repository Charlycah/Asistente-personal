from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class HealthSession:
    person: str = "la persona"
    observations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class HealthOrientationResult:
    handled: bool
    response: str = ""
    prompt: str = ""
    urgent: bool = False


class HealthOrientationService:
    """Provides cautious, temporary health-orientation conversations."""

    _RED_FLAGS = (
        "no puede respirar",
        "no puedo respirar",
        "dificultad grave para respirar",
        "dolor fuerte en el pecho",
        "dolor intenso en el pecho",
        "perdió el conocimiento",
        "perdio el conocimiento",
        "está inconsciente",
        "esta inconsciente",
        "convulsiona",
        "convulsiones",
        "no puede hablar",
        "no mueve un brazo",
        "no mueve una pierna",
        "debilidad repentina",
        "confusión repentina",
        "confusion repentina",
        "sangrado abundante",
    )
    _HEALTH_MARKERS = (
        "me duele",
        "le duele",
        "tengo dolor",
        "tiene dolor",
        "tengo fiebre",
        "tiene fiebre",
        "me siento mal",
        "se siente mal",
        "síntoma",
        "sintoma",
        "dolencia",
        "orientación de salud",
        "orientacion de salud",
        "consulta de salud",
    )

    def __init__(self) -> None:
        self._sessions: dict[str, HealthSession] = {}

    def prepare(
        self,
        text: str,
        *,
        session_id: str | None = None,
    ) -> HealthOrientationResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"

        if self._contains_red_flag(folded):
            self._sessions.pop(key, None)
            return HealthOrientationResult(
                handled=True,
                urgent=True,
                response=(
                    "Esto puede ser una urgencia médica. Buscá atención inmediata "
                    "o llamá al servicio de emergencias de tu zona. No esperes una "
                    "respuesta de Roby ni conduzcas si la persona está inestable."
                ),
            )

        if folded in {"cancelar orientación", "cancelar orientacion"}:
            self._sessions.pop(key, None)
            return HealthOrientationResult(
                handled=True,
                response="Cancelé la orientación y descarté los datos temporales.",
            )

        if folded in {
            "resumen de salud",
            "mostrar resumen de salud",
            "resumí la consulta de salud",
            "resumi la consulta de salud",
        }:
            return self._summary(key)

        session = self._sessions.get(key)
        if session is None and not self._is_health_request(folded):
            return HealthOrientationResult(handled=False)

        if session is None:
            session = HealthSession(person=self._extract_person(normalized))
            self._sessions[key] = session
        if normalized not in session.observations:
            session.observations.append(normalized)

        return HealthOrientationResult(
            handled=True,
            prompt=self._build_prompt(session),
        )

    def _contains_red_flag(self, folded: str) -> bool:
        return any(flag in folded for flag in self._RED_FLAGS)

    def _is_health_request(self, folded: str) -> bool:
        return any(marker in folded for marker in self._HEALTH_MARKERS)

    def _extract_person(self, text: str) -> str:
        match = re.search(
            r"\b(?:sobre|para)?\s*(Carlos|Cristina)\b",
            text,
            flags=re.IGNORECASE,
        )
        return match.group(1) if match else "la persona"

    def _summary(self, key: str) -> HealthOrientationResult:
        session = self._sessions.get(key)
        if session is None or not session.observations:
            return HealthOrientationResult(
                handled=True,
                response="No hay una orientación de salud activa para resumir.",
            )
        observations = "\n".join(f"- {item}" for item in session.observations)
        return HealthOrientationResult(
            handled=True,
            response=(
                f"Resumen temporal para {session.person}:\n{observations}\n\n"
                "Este resumen no es un diagnóstico. Puede servir para explicarle "
                "la situación a un profesional de salud."
            ),
        )

    def _build_prompt(self, session: HealthSession) -> str:
        observations = "\n".join(f"- {item}" for item in session.observations)
        return (
            "Actuá como orientador general de bienestar, no como médico. "
            "Respondé en español claro y prudente. No diagnostiques, no prescribas, "
            "no indiques dosis y no sugieras suspender medicación. Separá hechos "
            "informados de posibilidades generales. Hacé como máximo tres preguntas "
            "breves y relevantes sobre duración, intensidad, fiebre, respiración u "
            "otros signos importantes. Indicá cuándo conviene consultar a un "
            "profesional. Si advertís una posible señal de alarma, recomendá atención "
            "urgente. No guardes estos datos en memoria permanente.\n\n"
            f"Persona: {session.person}\n"
            f"Observaciones temporales:\n{observations}"
        )
