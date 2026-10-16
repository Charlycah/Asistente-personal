# M347.15 — Estabilización de la serie

## Objetivo

Cerrar la serie M347 con contratos verificables que protejan la arquitectura
cognitiva consolidada entre M347.3 y M347.14, sin incorporar comportamiento
productivo nuevo.

## Alcance

La suite `tests/test_m347_15_series_stabilization.py` verifica:

1. documentación completa y continua de los milestones M347.3–M347.15;
2. declaración consistente de M347.15 como base canónica en README y changelog;
3. una sola definición en `core/` para cada autoridad cognitiva de la serie;
4. compatibilidad de las firmas públicas ampliadas durante M347.10–M347.13;
5. estabilidad de valores públicos utilizados por pruebas, persistencia y trazas.

## Autoridades protegidas

- `ConversationContext`;
- `ConversationStrategyPlanner`;
- `CognitiveLearningPolicy`;
- `CognitiveMemoryRecall`;
- `CognitiveMemoryIntegration`;
- `MemoryPromptContextBuilder`.

Las comprobaciones no crean un registro paralelo de autoridades. Inspeccionan
las definiciones canónicas existentes para detectar duplicaciones accidentales.

## Compatibilidad protegida

Se preservan como extensiones opcionales:

- `ConversationStrategyPlanner.plan(..., context=None)`;
- `CognitiveMemoryIntegration.process_turn(...)` con aprendizaje, recall,
  contexto y perfil de sesión opcionales;
- `CognitiveMemoryRecallRequest` con estrategia, límite, umbral y perfil de
  sesión compatibles con llamadas históricas.

También quedan fijados los valores públicos esenciales de acciones, decisiones
de escritura, motivos de relevancia y continuidad entre sesiones.

## Límites

M347.15 no modifica:

- clasificación de intención;
- planificación o selección de acciones;
- política de escritura;
- esquema o contenido del store;
- ranking y umbral de recuperación;
- continuidad entre sesiones;
- construcción del contexto para prompts.

## Criterio de cierre

La serie queda estabilizada cuando pasan las pruebas específicas, las pruebas
integrales de M347.14, la regresión completa y `ruff check .`, sin cambios en
código productivo.
