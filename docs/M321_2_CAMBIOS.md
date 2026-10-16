# M321.2 — Detección de Ambigüedad

## Objetivo

Agregar al Brain una señal conservadora para detectar referencias explícitas que
no contienen información suficiente para resolverse con seguridad.

## Cambios

- Nuevo `DialogueAmbiguityAnalyzer` dentro de `application.brain`.
- Resultados acotados: `CLEAR` y `AMBIGUOUS_REFERENCE`.
- Integración observacional en `UnifiedExperienceLayer` mediante
  `last_dialogue_ambiguity`.
- Sin preguntas de clarificación automáticas, reescritura de solicitudes,
  cambios de memoria ni modificaciones al enrutamiento de motores.

## Ejemplos

- `¿Y el otro?` → referencia ambigua.
- `Eso` → referencia ambigua.
- `¿Y mañana?` después de una consulta meteorológica → continuación clara.

## Reversibilidad

La mejora puede retirarse eliminando el analizador y sus tres puntos de
integración, sin afectar motores, memoria, contexto persistente ni contratos de
capacidad.
