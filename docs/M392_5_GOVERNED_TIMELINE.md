# M392.5 — Línea Temporal Gobernada

M392.5 amplía el modelo persistente del mundo con una representación temporal
inmutable bajo la autoridad canónica `internal_world_model`.

## Fuente temporal

La vista consume únicamente instancias ya creadas de `ExecutiveEvent`, cuyo
contrato aporta `event_id` y `occurred_at` timezone-aware. M392.5 no crea eventos,
no consulta el reloj de pared y no observa fuentes externas.

Los intervalos y relaciones temporales requieren evidencia estructurada y
explícita. Una referencia desconocida se rechaza. Una contradicción entre una
relación declarada y las marcas temporales se conserva como riesgo y exige
revisión; no se reescribe la evidencia.

## Límites

M392.5 no crea agenda, calendario, recordatorios, planificación, persistencia,
automatización, procesos de fondo ni cambios de runtime. No modifica los eventos
fuente ni concede autoridad. El resultado es una proyección de sólo lectura,
determinista e inmutable.

## Autoridad

- Autoridad canónica: `internal_world_model`.
- Fuente contractual: `executive_event_model`.
- Nueva autoridad: ninguna.
