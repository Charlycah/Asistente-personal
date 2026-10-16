# M28 — Agent Loop

## Objetivo

Construir el loop mínimo de Phase 2 sobre `AgentRuntime`, manteniendo la
arquitectura cerrada en Architecture 1.0 y sin introducir ejecución continua,
hilos, scheduler, UI, voz ni planificación avanzada.

M28 transforma el turno unitario de M27 en un ciclo explícito y controlable.

## Arquitectura

```text
AgentTurn
    ↓
AgentLoop.run_once()
    ↓
AgentRuntime.run_turn()
    ↓
AgentRuntimeResult
```

## Componentes

- `AgentLoop`: coordinador mínimo de un ciclo de agente.
- `AgentLoopSnapshot`: estado observable del loop sin exponer mutabilidad interna.

## Contrato

- El loop ejecuta un único ciclo por llamada a `run_once`.
- No crea hilos ni procesos en segundo plano.
- No conoce UI, voz, micrófono, desktop ni infraestructura externa.
- Una ejecución deja el loop detenido al finalizar.
- Una falla inesperada del runtime se transforma en un resultado seguro.
- Un ciclo reentrante se rechaza sin tocar el runtime.

## Tests

- `test_agent_loop_starts_stopped_with_empty_snapshot`
- `test_agent_loop_runs_one_cycle_through_runtime_and_stops_cleanly`
- `test_agent_loop_can_be_started_and_stopped_without_background_work`
- `test_agent_loop_rejects_reentrant_cycle_without_touching_runtime`
- `test_agent_loop_turns_runtime_failures_into_safe_results_and_stops`

## Estado

Completo.
