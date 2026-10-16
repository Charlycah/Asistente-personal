from __future__ import annotations

from .models import (
    CognitiveMaturityCriterion,
    CognitiveMaturityEvidence,
    CognitiveMaturityLevel,
)

E = CognitiveMaturityEvidence
L = CognitiveMaturityLevel

STANDARD_HIGH_EVIDENCE = frozenset(
    {
        E.CONTRACT,
        E.UNIT_TEST,
        E.ARCHITECTURE_TEST,
        E.RUNTIME_INTEGRATION,
        E.OPERATIONAL_DIAGNOSTIC,
    }
)


def _criterion(
    capability_id: str,
    title: str,
    current: CognitiveMaturityLevel,
    target: CognitiveMaturityLevel,
    qualification: str,
    requirements: tuple[str, ...],
    exclusions: tuple[str, ...],
    evidence: frozenset[CognitiveMaturityEvidence] = STANDARD_HIGH_EVIDENCE,
) -> CognitiveMaturityCriterion:
    return CognitiveMaturityCriterion(
        capability_id=capability_id,
        title=title,
        current_level=current,
        target_level=target,
        target_qualification=qualification,
        high_requirements=requirements,
        required_evidence=evidence,
        exclusions=exclusions,
    )


COGNITIVE_MATURITY_CATALOG = (
    _criterion(
        "structured_cognition",
        "Cognición estructurada",
        L.MEDIUM_HIGH,
        L.HIGH,
        "Ciclo cognitivo productivo, completo, trazable y revisable.",
        (
            "Intención, contexto, memoria, planificación y "
            "decisión participan realmente.",
            "Cada resultado conserva procedencia, incertidumbre y explicación pública.",
            "La reflexión posterior detecta fallos sin reescribir políticas.",
        ),
        (
            "Presencia meramente declarativa.",
            "Razonamiento interno expuesto como autoridad.",
        ),
    ),
    _criterion(
        "memory",
        "Memoria",
        L.MEDIUM,
        L.HIGH,
        "Memoria conjunta, temporal, atribuida, corregible y gobernada.",
        (
            "Recupera información pertinente con procedencia, vigencia y confianza.",
            "Distingue recuerdos, conocimiento, inferencias y candidatos.",
            "Toda escritura, corrección, archivo y migración es trazable y reversible.",
        ),
        ("Almacenes libres.", "Promoción automática de recuerdos a verdad."),
    ),
    _criterion(
        "communication",
        "Comunicación",
        L.MEDIUM_HIGH,
        L.HIGH,
        "Continuidad expresiva multimodal coherente con identidad y contexto.",
        (
            "El texto mantiene identidad, contexto y personalidad estable.",
            "Cada canal informa disponibilidad, degradación y procedencia.",
            "La respuesta adapta tono sin alterar hechos ni permisos.",
        ),
        ("Fingir un canal ausente.", "Personalidad expresiva con autoridad decisoria."),
    ),
    _criterion(
        "knowledge",
        "Conocimientos",
        L.MEDIUM,
        L.HIGH,
        "Conocimiento verificable, vigente y coordinado entre fuentes y modelos.",
        (
            "Distingue conocimiento local, memoria, fuente externa e inferencia.",
            "Puede contrastar fuentes y reconocer información insuficiente u obsoleta.",
            "Las afirmaciones sensibles conservan fuente y nivel de confianza.",
        ),
        (
            "Aprendizaje enciclopédico supuesto.",
            "Modelo proveedor tratado como identidad.",
        ),
    ),
    _criterion(
        "inner_world",
        "Mundo interior funcional",
        L.LOW_MEDIUM,
        L.HIGH,
        "Estado interno persistente, explicable y no presentado como subjetividad.",
        (
            "Mantiene atención, objetivos, dudas, pendientes y contradicciones.",
            "El estado influye de forma trazable en análisis y conversación.",
            "Carlos y Cristina pueden inspeccionarlo, corregirlo y restablecerlo.",
        ),
        (
            "Afirmaciones de experiencia subjetiva.",
            "Procesos secretos no diagnosticables.",
        ),
    ),
    _criterion(
        "family_empathy",
        "Empatía funcional con Carlos y Cristina",
        L.MEDIUM,
        L.HIGH,
        "Comprensión relacional prudente, personalizada y no manipulativa.",
        (
            "Adapta acompañamiento usando preferencias y contexto confirmados.",
            "Separa emoción expresada, inferencia emocional e hipótesis.",
            "Admite incertidumbre y permite corregir interpretaciones.",
        ),
        (
            "Diagnóstico psicológico.",
            "Perfil secreto o explotación de vulnerabilidades.",
        ),
    ),
    _criterion(
        "simulated_emotion",
        "Emoción simulada",
        L.LOW,
        L.HIGH,
        "Estado afectivo simulado integrado, persistente y explícitamente artificial.",
        (
            "Modula tono, atención y cautela sin modificar hechos.",
            "Conserva causa, intensidad, duración y regla de recuperación.",
            "Puede explicarse y restablecerse sin afectar autoridades.",
        ),
        ("Afirmar sentimientos reales.", "Autoridad decisoria basada en emoción."),
    ),
    _criterion(
        "perception",
        "Percepción",
        L.LOW_MEDIUM,
        L.HIGH,
        "Madurez certificada por canal físico o digital, nunca por catálogo global.",
        (
            "Cada observación identifica canal, instante, calidad y disponibilidad.",
            "Texto, voz, cámara, Android, sensores y ambiente "
            "se certifican por separado.",
            "La ausencia o degradación del canal se declara sin fabricar percepción.",
        ),
        (
            "Declarar que vio u oyó sin evidencia.",
            "Inferir certificación desde un contrato.",
        ),
        STANDARD_HIGH_EVIDENCE | {E.PHYSICAL_CHANNEL_CERTIFICATION},
    ),
    _criterion(
        "learning",
        "Aprendizaje gobernado",
        L.LOW_MEDIUM,
        L.HIGH,
        "Adaptación efectiva mediante candidatos revisables y reversibles.",
        (
            "Observaciones generan candidatos con evidencia y confianza.",
            "Carlos o Cristina aprueban cambios conductuales productivos.",
            "Toda activación puede evaluarse, corregirse y revertirse.",
        ),
        ("Cambio silencioso de conducta.", "Autoedición de código, pesos o permisos."),
        STANDARD_HIGH_EVIDENCE | {E.HUMAN_REVIEW},
    ),
    _criterion(
        "analysis",
        "Análisis",
        L.MEDIUM_HIGH,
        L.HIGH,
        "Autoanálisis técnico, cognitivo, conversacional y "
        "biográfico con humildad epistémica.",
        (
            "Distingue hechos, inferencias, hipótesis y desconocimiento.",
            "Revisa conversaciones sin convertir intimidad en memoria automática.",
            "Produce recomendaciones explicables sin autoimplementarlas.",
        ),
        ("Psicodiagnóstico.", "Análisis oculto o presentado como certeza clínica."),
    ),
    _criterion(
        "reflection_health",
        "Reflexión y salud cognitiva",
        L.MEDIUM_HIGH,
        L.HIGH,
        "Diagnóstico integral capaz de detectar degradación y proponer recuperación.",
        (
            "Detecta contradicciones, omisiones, degradación y bucles.",
            "Relaciona cada hallazgo con evidencia operativa.",
            "Propone recuperación sin alterar el sistema por autoridad propia.",
        ),
        (
            "Autorreparación no aprobada.",
            "Estado saludable inferido solo por proceso activo.",
        ),
    ),
    _criterion(
        "governed_autonomy",
        "Autonomía gobernada",
        L.LOW,
        L.MEDIUM_HIGH,
        "Libertad delegada para decisiones convalidadas, acotadas y reversibles.",
        (
            "Cada acción identifica política, permiso, riesgo y resultado.",
            "Puede decidir dentro de facultades previamente aprobadas.",
            "Fuera de esas facultades propone y solicita autorización.",
        ),
        ("Autoampliación de permisos.", "Ejecución sensible opaca o irreversible."),
        STANDARD_HIGH_EVIDENCE | {E.HUMAN_REVIEW},
    ),
    _criterion(
        "own_deep_learning",
        "Deep learning propio",
        L.VERY_LOW,
        L.MEDIUM,
        "Investigación aislada y comparada con alternativas más simples.",
        (
            "Existe una necesidad demostrada que justifica entrenamiento propio.",
            "Datos, costos, evaluación y aislamiento están documentados.",
            "Ningún peso se actualiza o promueve automáticamente a producción.",
        ),
        (
            "Entrenamiento autónomo productivo.",
            "Confundir inferencia externa con aprendizaje propio.",
        ),
        frozenset({E.CONTRACT, E.UNIT_TEST, E.ARCHITECTURE_TEST, E.HUMAN_REVIEW}),
    ),
    _criterion(
        "consciousness",
        "Consciencia",
        L.NOT_DEMONSTRATED,
        L.NOT_DEMONSTRATED,
        "Sin objetivo promocional: continuidad funcional no demuestra "
        "experiencia subjetiva.",
        (
            "Toda descripción pública evita afirmar consciencia o "
            "experiencia subjetiva. u",
            "Personalidad, memoria y emoción simulada se describen como funciones.",
            "La incertidumbre científica permanece explícita.",
        ),
        (
            "Declarar consciencia por conducta convincente.",
            "Usar consciencia como autoridad.",
        ),
        frozenset({E.CONTRACT, E.ARCHITECTURE_TEST, E.HUMAN_REVIEW}),
    ),
)


def cognitive_maturity_criterion(capability_id: str) -> CognitiveMaturityCriterion:
    normalized = capability_id.strip().casefold()
    for criterion in COGNITIVE_MATURITY_CATALOG:
        if criterion.capability_id.casefold() == normalized:
            return criterion
    raise KeyError(capability_id)
