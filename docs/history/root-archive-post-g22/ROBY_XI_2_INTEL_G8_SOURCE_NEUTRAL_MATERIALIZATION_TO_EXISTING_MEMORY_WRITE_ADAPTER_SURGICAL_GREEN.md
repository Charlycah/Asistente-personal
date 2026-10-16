# ROBY XI.2 — INTEL-G8 — Source-neutral write-adapter SURGICAL GREEN

## Estado

SURGICAL GREEN pendiente de certificación local. Baseline de entrada: CONTRACT RED
validado con 14.108 PASS + 5 fallos RED intencionales, Ruff clean y 0 regresiones.

## Cambio productivo mínimo

Se generaliza exclusivamente `GovernedMemoryWriteAdapterFoundation`, autoridad ya
existente. No se crea adapter, writer, gateway, manager ni runtime paralelo.

La validación de provenance exige exactamente una genealogía gobernada:

- histórica: `preference_candidate_id`, sin `policy_candidate_id`;
- source-neutral: `policy_candidate_id`, sin `preference_candidate_id`.

Ambas ausentes o ambas presentes fallan cerrado.

## Metadata

El camino histórico conserva `preference_candidate_id` y `learning_kind`.

El camino source-neutral conserva `policy_candidate_id` y `learning_category`, y no
serializa `preference_candidate_id` ni `learning_kind` históricos como provenance falsa.

## Garantías preservadas

La idempotencia, validación estructural de `STABLE_KNOWLEDGE`, autoridad del writer y
contrato `GovernedMemoryWriteRequest` permanecen bajo las implementaciones existentes.

## STOP

El resultado máximo continúa siendo un `GovernedMemoryWriteRequest` inerte.

No se invoca `OfficialMemoryGateway`, no se escribe Memory, no se ejecuta runtime
productivo, no hay persistencia, background learning ni consolidación automática.

`MATERIALIZATION PROPOSAL != WRITE REQUEST != PERSISTED MEMORY`.
