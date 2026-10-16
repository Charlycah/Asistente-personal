# M27 — Agent Runtime

## Objetivo

Iniciar Phase 2 con un runtime mínimo de agente que estabiliza el contrato de un
turno autónomo sin alterar la arquitectura cerrada en Architecture 1.0.

M27 no introduce planificación avanzada, tareas periódicas ni ejecución en segundo
plano. Solo define el punto de entrada estable para que próximos milestones puedan
construir encima de él.

## Arquitectura

```text
AgentTurn
    ↓
AgentRuntime.run_turn()
    ↓
ROBY.process()
    ↓
AgentRuntimeResult
```

## Componentes

- `AgentProcessor`: contrato mínimo para procesadores compatibles con ROBY.
- `AgentTurn`: entrada normalizada de Phase 2.
- `AgentRuntime`: coordinador de un único turno de agente.
- `AgentRuntimeResult`: salida estable para futuros ciclos autónomos.

## Contrato

- ROBY sigue siendo el núcleo de procesamiento.
- El runtime no conoce UI, voz, micrófono, desktop ni infraestructura externa.
- Un turno vacío no debe llamar a ROBY.
- Una falla del procesador no debe romper el ciclo del agente.
- El contrato queda preparado para scheduler, loop o planner en milestones futuros.

## Tests

- `test_agent_turn_defines_phase_2_input_contract`
- `test_agent_runtime_normalizes_and_delegates_turn_to_processor`
- `test_agent_runtime_rejects_blank_turn_without_calling_processor`
- `test_agent_runtime_keeps_processor_failures_non_critical`

## Estado

Completo.
