# M33 — Cognitive Intent Analyzer

## Estado

CLOSED

## Objetivo

Iniciar la capa cognitiva de ROBY con un analizador determinístico que clasifique el tipo de conversación antes de invocar estrategias, memoria, herramientas o LLM.

M33 no incorpora memoria viva, proactividad ni llamadas a modelos. Solo responde una pregunta:

> ¿Qué tipo de conversación está teniendo ROBY?

## Alcance

Incluido:

- `CognitiveIntent`
- `CognitiveIntentResult`
- `CognitiveIntentAnalyzer`
- Clasificación básica de conversación:
  - casual
  - doméstica
  - técnica
  - cultural
  - razonamiento profundo
  - código
  - apoyo emocional
  - trabajo del proyecto ROBY
  - desconocida
- Señales usadas para la decisión.
- Indicadores mínimos para profundidad y uso de LLM.

Excluido:

- memoria persistente
- aprendizaje automático
- proactividad
- selección de modelo
- herramientas externas
- llamadas de red
- modificación del `AgentLoop`

## Cambio mínimo

Se agregó:

- `core/cognitive_intent.py`

Se agregó cobertura específica:

- `tests/test_m33_cognitive_intent_analyzer.py`

## Decisiones de arquitectura

El analizador es determinístico para mantener M33 verificable, rápido y estable. No depende de proveedores LLM ni de infraestructura externa.

La prioridad de clasificación favorece señales que requieren tratamiento especial:

1. Apoyo emocional
2. Código
3. Razonamiento profundo
4. Cultura
5. Doméstica
6. Casual
7. Trabajo del proyecto ROBY
8. Técnica

La salida queda lista para que milestones posteriores construyan estrategia conversacional, ingesta de memoria, recuperación de contexto y comportamiento proactivo.

## Validación

- Ruff limpio.
- Suite completa verde.
- Tests específicos de M33 verdes.
