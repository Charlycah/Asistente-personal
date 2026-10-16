# RP.20.24 — Propiedades booleanas triviales retiradas

## Objetivo

Reducir la superficie pública que sólo reflejaba presencia, longitud o igualdad de campos ya visibles, sin consumidores funcionales ni interpretación de dominio.

## Retirado

- `CognitiveAgendaSnapshot.open_items`
- `ROBYMentalState.has_active_goals`
- `ReasoningContext.has_workspace`
- `ConversationTimingDecision.ready_now`
- `ToolRuntimeContext.tool_call_performed`

## Acceso canónico

- `len(snapshot.items)`
- `bool(state.active_goals)`
- `context.working_memory is not None`
- `decision.recommendation is TimingRecommendation.INTERVENE_NOW`
- `context.gateway_result is not None`

## Conservado

Se conservaron propiedades como `passed`, `allowed`, `succeeded`, `called_llm` y `learned_something` porque expresan una decisión o interpretación de dominio estable.

## Validación

- `ruff check .` limpio
- 64 pruebas focales
- 6591 pruebas completas
