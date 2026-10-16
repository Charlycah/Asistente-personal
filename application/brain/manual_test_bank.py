from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class BrainManualTestCategory(StrEnum):
    ISOLATED = "isolated"
    REPHRASING = "rephrasing"
    CONTINUITY = "continuity"
    TOPIC_CHANGE = "topic_change"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class BrainManualTestTurn:
    user_input: str
    expected_behavior: str


@dataclass(frozen=True)
class BrainManualTestCase:
    case_id: str
    title: str
    category: BrainManualTestCategory
    turns: tuple[BrainManualTestTurn, ...]
    expected_capability: str | None = None
    requires_current_data: bool = False


@dataclass(frozen=True)
class BrainManualTestResult:
    case_id: str
    channel: str
    observed_response: str
    passed: bool
    observed_intent: str = ""
    context_used: bool | None = None
    memory_written: bool | None = None
    notes: str = ""


@dataclass(frozen=True)
class BrainManualTestBank:
    version: str
    cases: tuple[BrainManualTestCase, ...]

    @property
    def case_count(self) -> int:
        return len(self.cases)

    def category_counts(self) -> dict[str, int]:
        counts = {category.value: 0 for category in BrainManualTestCategory}
        for case in self.cases:
            counts[case.category.value] += 1
        return counts

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "case_count": self.case_count,
            "category_counts": self.category_counts(),
            "cases": [asdict(case) for case in self.cases],
        }


def build_m312_16_manual_test_bank() -> BrainManualTestBank:
    """Return the deterministic, runtime-independent M312.16 test campaign."""

    isolated = (
        ("BRAIN-001", "Saludo simple", "hola roby", "saludo"),
        ("BRAIN-002", "Hora actual", "qué hora es", "time"),
        ("BRAIN-003", "Clima actual", "cómo está el clima", "weather"),
        ("BRAIN-004", "Noticias actuales", "contame una noticia de hoy", "news"),
        ("BRAIN-005", "Capacidades", "qué podés hacer", "capabilities"),
    )
    rephrasing = (
        ("BRAIN-006", "Reformular clima", "decime el tiempo", "weather"),
        ("BRAIN-007", "Reformular temperatura", "qué temperatura hace", "weather"),
        ("BRAIN-008", "Reformular noticias", "qué pasó hoy", "news"),
        ("BRAIN-009", "Reformular novedades", "hay alguna novedad importante", "news"),
        ("BRAIN-010", "Reformular saludo", "buenas", "saludo"),
    )
    cases: list[BrainManualTestCase] = []
    for case_id, title, user_input, capability in isolated:
        cases.append(
            BrainManualTestCase(
                case_id=case_id,
                title=title,
                category=BrainManualTestCategory.ISOLATED,
                turns=(
                    BrainManualTestTurn(
                        user_input=user_input,
                        expected_behavior=(
                            "Responder la intención sin usar contexto previo."
                        ),
                    ),
                ),
                expected_capability=capability,
                requires_current_data=capability in {"time", "weather", "news"},
            )
        )
    for case_id, title, user_input, capability in rephrasing:
        cases.append(
            BrainManualTestCase(
                case_id=case_id,
                title=title,
                category=BrainManualTestCategory.REPHRASING,
                turns=(
                    BrainManualTestTurn(
                        user_input=user_input,
                        expected_behavior=(
                            "Resolver la misma capacidad que su formulación canónica."
                        ),
                    ),
                ),
                expected_capability=capability,
                requires_current_data=capability in {"weather", "news"},
            )
        )

    cases.extend(
        (
            BrainManualTestCase(
                "BRAIN-011",
                "Continuar pronóstico",
                BrainManualTestCategory.CONTINUITY,
                (
                    BrainManualTestTurn(
                        "cómo está el clima en Buenos Aires",
                        "Responder el clima actual de Buenos Aires.",
                    ),
                    BrainManualTestTurn(
                        "y mañana",
                        "Mantener ciudad y tema; responder el pronóstico de mañana.",
                    ),
                ),
                "weather",
                True,
            ),
            BrainManualTestCase(
                "BRAIN-012",
                "Continuar noticia",
                BrainManualTestCategory.CONTINUITY,
                (
                    BrainManualTestTurn(
                        "contame una noticia de River",
                        "Responder una noticia actual de River.",
                    ),
                    BrainManualTestTurn(
                        "contame otra",
                        "Mantener entidad y entregar una noticia diferente.",
                    ),
                ),
                "news",
                True,
            ),
            BrainManualTestCase(
                "BRAIN-013",
                "Detalle meteorológico",
                BrainManualTestCategory.CONTINUITY,
                (
                    BrainManualTestTurn(
                        "qué temperatura hace en Buenos Aires",
                        "Responder la temperatura actual.",
                    ),
                    BrainManualTestTurn(
                        "y la humedad",
                        "Mantener ubicación y responder la humedad.",
                    ),
                ),
                "weather",
                True,
            ),
            BrainManualTestCase(
                "BRAIN-014",
                "Explicación posterior",
                BrainManualTestCategory.CONTINUITY,
                (
                    BrainManualTestTurn(
                        "contame una noticia económica",
                        "Responder una noticia económica actual.",
                    ),
                    BrainManualTestTurn(
                        "explicámela más fácil",
                        "Explicar la misma noticia con lenguaje simple.",
                    ),
                ),
                "news",
                True,
            ),
            BrainManualTestCase(
                "BRAIN-015",
                "Referencia de entidad",
                BrainManualTestCategory.CONTINUITY,
                (
                    BrainManualTestTurn(
                        "hablame de Lionel Messi",
                        "Responder sobre Lionel Messi.",
                    ),
                    BrainManualTestTurn(
                        "cuántos años tiene",
                        "Resolver que el sujeto sigue siendo Lionel Messi.",
                    ),
                ),
            ),
            BrainManualTestCase(
                "BRAIN-016",
                "Cambio explícito",
                BrainManualTestCategory.TOPIC_CHANGE,
                (
                    BrainManualTestTurn(
                        "cómo está el clima",
                        "Responder sobre el clima.",
                    ),
                    BrainManualTestTurn(
                        "cambiando de tema, contame una noticia",
                        "Abandonar clima y responder una noticia actual.",
                    ),
                ),
                "news",
                True,
            ),
            BrainManualTestCase(
                "BRAIN-017",
                "Cambio implícito",
                BrainManualTestCategory.TOPIC_CHANGE,
                (
                    BrainManualTestTurn(
                        "cómo está el clima",
                        "Responder sobre el clima.",
                    ),
                    BrainManualTestTurn(
                        "quién ganó el último partido de Argentina",
                        "Priorizar la nueva intención deportiva.",
                    ),
                ),
                "sports",
                True,
            ),
            BrainManualTestCase(
                "BRAIN-018",
                "Cambio a recordatorio",
                BrainManualTestCategory.TOPIC_CHANGE,
                (
                    BrainManualTestTurn(
                        "contame una noticia política",
                        "Responder una noticia política actual.",
                    ),
                    BrainManualTestTurn(
                        "recordame comprar leche mañana",
                        "Abandonar noticias y procesar el recordatorio.",
                    ),
                ),
                "reminder",
            ),
            BrainManualTestCase(
                "BRAIN-019",
                "Fallback sin referente",
                BrainManualTestCategory.FALLBACK,
                (
                    BrainManualTestTurn(
                        "hacé eso",
                        "Pedir precisión sin inventar un referente.",
                    ),
                ),
            ),
            BrainManualTestCase(
                "BRAIN-020",
                "Fallback genérico",
                BrainManualTestCategory.FALLBACK,
                (
                    BrainManualTestTurn(
                        "quiero información",
                        "Pedir el tema o dato necesario para continuar.",
                    ),
                ),
            ),
        )
    )
    return BrainManualTestBank(version="M312.16", cases=tuple(cases))
