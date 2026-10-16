from dataclasses import dataclass, field
from enum import StrEnum


class CognitiveIntent(StrEnum):
    """Tipos cognitivos mínimos para clasificar una conversación antes del LLM."""

    CASUAL_CHAT = "casual_chat"
    DOMESTIC_QUESTION = "domestic_question"
    TECHNICAL_QUESTION = "technical_question"
    CULTURAL_QUESTION = "cultural_question"
    DEEP_REASONING = "deep_reasoning"
    CODE_REQUEST = "code_request"
    EMOTIONAL_SUPPORT = "emotional_support"
    PROJECT_WORK = "project_work"
    UNKNOWN = "unknown"


class InteractionIntent(StrEnum):
    """Forma explícita del turno dentro de la conversación."""

    QUESTION = "question"
    COMMAND = "command"
    FOLLOW_UP = "follow_up"
    CORRECTION = "correction"
    SOCIAL = "social"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CognitiveIntentResult:
    intent: CognitiveIntent
    confidence: float
    normalized_text: str
    signals: tuple[str, ...] = field(default_factory=tuple)
    requires_depth: bool = False
    should_use_llm: bool = True
    interaction_intent: InteractionIntent = InteractionIntent.UNKNOWN
    interaction_confidence: float = 0.0
    interaction_signals: tuple[str, ...] = field(default_factory=tuple)


class CognitiveIntentAnalyzer:
    """
    Analizador cognitivo mínimo para Phase 2A.

    Clasifica un turno conversacional por señales determinísticas, sin llamadas a
    red, proveedores LLM, memoria ni proactividad. Su única responsabilidad es
    responder qué tipo de conversación está teniendo ROBY para que milestones
    posteriores decidan estrategia, memoria y construcción de prompt.
    """

    _CASUAL_PATTERNS = (
        "hola",
        "buenas",
        "buen día",
        "buen dia",
        "buenas tardes",
        "buenas noches",
        "qué tal",
        "que tal",
        "cómo estás",
        "como estas",
    )
    _DOMESTIC_PATTERNS = (
        "qué hora",
        "que hora",
        "temperatura",
        "clima",
        "agenda",
        "recordame",
        "recordatorio",
        "alarma",
        "timer",
        "temporizador",
        "comprar",
        "lista",
        "cocinar",
    )
    _TECHNICAL_PATTERNS = (
        "arquitectura",
        "dependency injection",
        "inyección de dependencias",
        "inyeccion de dependencias",
        "api",
        "base de datos",
        "db",
        "tests",
        "pytest",
        "ruff",
        "git",
        "provider",
        "runtime",
        "service",
    )
    _CULTURAL_PATTERNS = (
        "cultura",
        "historia",
        "literatura",
        "cine",
        "música",
        "musica",
        "arte",
        "bowman",
        "kubrick",
        "2001",
        "idiosincrasia",
    )
    _DEEP_PATTERNS = (
        "sentido de la vida",
        "qué significa",
        "que significa",
        "filosofía",
        "filosofia",
        "conciencia",
        "existencia",
        "moral",
        "ética",
        "etica",
        "profundo",
        "por qué vivimos",
        "por que vivimos",
    )
    _CODE_PATTERNS = (
        "código",
        "codigo",
        "python",
        "clase",
        "función",
        "funcion",
        "script",
        "implementa",
        "programa",
        "refactor",
        "debug",
        "bug",
    )
    _EMOTIONAL_PATTERNS = (
        "me siento",
        "estoy triste",
        "ansiedad",
        "preocupado",
        "preocupada",
        "frustrado",
        "frustrada",
        "solo",
        "sola",
        "miedo",
        "angustia",
    )
    _CORRECTION_PATTERNS = (
        "no,",
        "no me refería",
        "no me referia",
        "quise decir",
        "me corrijo",
        "corrijo",
        "en realidad",
    )
    _FOLLOW_UP_PATTERNS = (
        "seguimos",
        "sigamos",
        "continuemos",
        "además",
        "ademas",
        "también",
        "tambien",
        "y mañana",
        "y después",
        "y despues",
        "dame el pronóstico",
        "dame el pronostico",
    )
    _COMMAND_PATTERNS = (
        "abrí ",
        "abri ",
        "abre ",
        "mostrame",
        "muéstrame",
        "muestrame",
        "decime",
        "dime",
        "dame ",
        "recordame",
        "creá ",
        "crea ",
        "hacé ",
        "hace ",
        "ejecutá ",
        "ejecuta ",
        "implementa",
    )
    _QUESTION_PREFIXES = (
        "qué ",
        "que ",
        "cómo ",
        "como ",
        "cuándo ",
        "cuando ",
        "dónde ",
        "donde ",
        "cuál ",
        "cual ",
        "quién ",
        "quien ",
        "por qué ",
        "por que ",
        "podés ",
        "podes ",
        "puedes ",
    )
    _SOCIAL_PATTERNS = _CASUAL_PATTERNS + (
        "gracias",
        "hasta luego",
        "nos vemos",
        "buen trabajo",
    )

    _PROJECT_PATTERNS = (
        "roby",
        "milestone",
        "phase",
        "fase",
        "m27",
        "m28",
        "m29",
        "m30",
        "m31",
        "m32",
        "m33",
        "commit",
        "architecture 1.0",
    )

    def analyze(self, text: str) -> CognitiveIntentResult:
        normalized_text = " ".join(text.strip().lower().split())

        if not normalized_text:
            return CognitiveIntentResult(
                intent=CognitiveIntent.UNKNOWN,
                confidence=0.0,
                normalized_text="",
                signals=("empty_text",),
                should_use_llm=False,
            )

        scored_intents = self._score_intents(normalized_text)
        intent, signals = self._select_intent(scored_intents)
        confidence = self._confidence_for(signals)
        interaction_intent, interaction_signals = self._classify_interaction(
            normalized_text
        )

        return CognitiveIntentResult(
            intent=intent,
            confidence=confidence,
            normalized_text=normalized_text,
            signals=tuple(signals),
            requires_depth=intent
            in {
                CognitiveIntent.CULTURAL_QUESTION,
                CognitiveIntent.DEEP_REASONING,
            },
            should_use_llm=intent is not CognitiveIntent.DOMESTIC_QUESTION,
            interaction_intent=interaction_intent,
            interaction_confidence=self._confidence_for(interaction_signals),
            interaction_signals=tuple(interaction_signals),
        )

    def _classify_interaction(
        self, normalized_text: str
    ) -> tuple[InteractionIntent, list[str]]:
        correction = self._matches(normalized_text, self._CORRECTION_PATTERNS)
        if correction:
            return InteractionIntent.CORRECTION, correction

        follow_up = self._matches(normalized_text, self._FOLLOW_UP_PATTERNS)
        if follow_up:
            return InteractionIntent.FOLLOW_UP, follow_up

        command = self._matches(normalized_text, self._COMMAND_PATTERNS)
        if command:
            return InteractionIntent.COMMAND, command

        question = [
            prefix
            for prefix in self._QUESTION_PREFIXES
            if normalized_text.startswith(prefix)
        ]
        if "?" in normalized_text or "¿" in normalized_text:
            question.append("question_mark")
        if question:
            return InteractionIntent.QUESTION, question

        social = self._matches(normalized_text, self._SOCIAL_PATTERNS)
        if social:
            return InteractionIntent.SOCIAL, social

        return InteractionIntent.UNKNOWN, ["no_interaction_signal"]

    def _score_intents(self, normalized_text: str) -> dict[CognitiveIntent, list[str]]:
        return {
            CognitiveIntent.EMOTIONAL_SUPPORT: self._matches(
                normalized_text,
                self._EMOTIONAL_PATTERNS,
            ),
            CognitiveIntent.CODE_REQUEST: self._matches(
                normalized_text,
                self._CODE_PATTERNS,
            ),
            CognitiveIntent.DEEP_REASONING: self._matches(
                normalized_text,
                self._DEEP_PATTERNS,
            ),
            CognitiveIntent.CULTURAL_QUESTION: self._matches(
                normalized_text,
                self._CULTURAL_PATTERNS,
            ),
            CognitiveIntent.DOMESTIC_QUESTION: self._matches(
                normalized_text,
                self._DOMESTIC_PATTERNS,
            ),
            CognitiveIntent.CASUAL_CHAT: self._matches(
                normalized_text,
                self._CASUAL_PATTERNS,
            ),
            CognitiveIntent.PROJECT_WORK: self._matches(
                normalized_text,
                self._PROJECT_PATTERNS,
            ),
            CognitiveIntent.TECHNICAL_QUESTION: self._matches(
                normalized_text,
                self._TECHNICAL_PATTERNS,
            ),
        }

    @staticmethod
    def _matches(normalized_text: str, patterns: tuple[str, ...]) -> list[str]:
        return [pattern for pattern in patterns if pattern in normalized_text]

    @staticmethod
    def _select_intent(
        scored_intents: dict[CognitiveIntent, list[str]],
    ) -> tuple[CognitiveIntent, list[str]]:
        for intent, signals in scored_intents.items():
            if signals:
                return intent, signals

        return CognitiveIntent.UNKNOWN, ("no_known_signal",)

    @staticmethod
    def _confidence_for(signals: list[str] | tuple[str, ...]) -> float:
        if not signals or tuple(signals) in {
            ("no_known_signal",),
            ("no_interaction_signal",),
        }:
            return 0.2

        return min(0.95, 0.55 + (0.1 * len(signals)))
