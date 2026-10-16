# RP.16 — Cognitive World Model

RP.16 incorpora un modelo interno gobernado y auditable que transforma el hilo
cognitivo y sus hipótesis en una representación explícita de entidades y
relaciones.

## Flujo

Agenda → Deliberation → Reflection → Thought Stream → Hypothesis Workspace →
World Model → Continuous Cognitive State

## Contratos

- Los focos activos se representan como hechos observados.
- Las hipótesis se representan como inferencias o estados inciertos.
- Toda entidad y relación conserva procedencia y confianza.
- Los focos anteriores se retiran sin convertirlos en hechos vigentes.
- El modelo no ejecuta acciones, no modifica la agenda y no solicita
  autorización.
- No almacena cadenas privadas de razonamiento.

## Exposición

El resultado queda disponible como `state.world_model`.

El contrato histórico `state.rationale == "agenda:<key>"` se mantiene intacto.
