# M400.8 — Governed External Evidence Corroboration

## Propósito

M400.8 contrasta múltiples evidencias externas que ya atravesaron admisión,
provenance, verification y assessment. No consulta nuevas fuentes y no infiere
semánticamente por sí solo si dos textos dicen lo mismo.

Cada evidencia se asocia a una `proposition_id` explícita y una postura
`support` o `contradict`.

**corroboración ≠ verdad certificada**

**mayoría ≠ verdad**

**independencia de actor ≠ independencia epistemológica**

## Estados

`corroborated` requiere al menos dos evidencias utilizables de actores externos
distintos y todas con postura `support`.

`contradicted` aplica el mismo criterio cuando todas las evidencias utilizables
tienen postura `contradict`.

`mixed` conserva conflicto explícito cuando existen posturas utilizables en
ambos sentidos.

`insufficient` indica que falta cantidad o diversidad de actores para hablar de
corroboración.

`rejected` se utiliza cuando toda la evidencia disponible ya fue rechazada en
etapas anteriores.

## Independencia

M400.8 sólo puede verificar diversidad de `actor_id`. Dos actores distintos
pueden depender de la misma fuente original, copiarse entre sí o compartir
sesgos. Por eso actor distinto no equivale a independencia epistemológica.

M400.8 no intenta resolver ese problema con inferencia oculta.

## Confianza

`aggregate_confidence` es la media de las confidencias M400.7 de la evidencia
relevante. No es una probabilidad de verdad y no puede superar los límites de
las evaluaciones de entrada.

Una mayoría cuantitativa tampoco certifica verdad.

## Autoridad y límites

`GovernedExternalEvidenceCorroborator` expone `corroborator_id`, no
`authority_id`.

M400.8:

- no consulta nuevas fuentes;
- no ejecuta providers;
- no ejecuta adapters;
- no selecciona rutas;
- no crea proposiciones automáticamente;
- no infiere postura desde texto libre;
- no escribe memoria ni modifica código;
- mantiene `truth_certified=False`;
- mantiene `cognitive_authority_granted=False`.
