# M321.3 — Clarificación Guiada

## Objetivo

Convertir la señal conservadora de ambigüedad de M321.2 en una pregunta breve y
determinista, sin modificar motores, memoria persistente ni contratos públicos.

## Cambios

- Nuevo `DialogueClarificationGuide` dentro del Brain.
- Preguntas específicas para alternativas ambiguas y demostrativos sin referente.
- Integración mínima en `UnifiedExperienceLayer`.
- Las continuaciones claras mantienen el flujo existente.
- La respuesta de un motor sólo se sustituye cuando la referencia es explícitamente
  ambigua.

## Validación

- Pruebas específicas de M321.3.
- Regresión acumulada de M320 y M321.
- Suite completa del proyecto.
