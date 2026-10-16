# M389.8 — Evidencia Epistemológica Unificada

## Objetivo

Cerrar M389 con una autoridad única de normalización epistemológica que reúna
resultados ya clasificados por M389.1 y consolidados por M389.7.

M389.8 no sustituye `EpistemicClassifier`, no analiza conversación y no crea
nuevas inferencias. Convierte niveles ya certificados a un lenguaje público
uniforme y trazable.

## Autoridad

`UnifiedEpistemicEvidenceAuthority` es la única autoridad para normalización
epistemológica transversal.

## Lenguaje común

- `observed`: “Esto fue observado en la evidencia.”
- `inferred`: “Esto lo inferí de la evidencia.”
- `possible`: “Esta es solamente una posibilidad.”
- `insufficient_information`: “No tengo información suficiente.”

## Entradas

- `ExecutiveReport` de M389.7.
- `EpistemicAssessment` de M389.1 cuando se requiere trazabilidad por reclamo.

## Salida

`UnifiedEpistemicReport` contiene registros inmutables con procedencia,
referencia, nivel original, categoría unificada, evidencia, riesgos y necesidad
de revisión humana.

Los conflictos entre categorías se conservan como
`conflict_review_required`; la autoridad nunca los resuelve ni promueve una
posibilidad a hecho.

## Límites

La autoridad es de solo lectura. No expone contenido conversacional, no crea ni
modifica memoria, aprendizaje, planificación, permisos, tareas, recordatorios o
automatizaciones, y no ejecuta acciones.
