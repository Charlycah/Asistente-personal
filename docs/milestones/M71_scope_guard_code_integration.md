# M71 - Scope Guard integrado en codigo real

## Objetivo
Integrar el Bloque 1 de Fase VII en el codigo existente de ROBY como una capa de alcance operativo segura, auditable y compatible con el pipeline cognitivo.

## Archivos incorporados

- `core/scope_guard.py`
- `tests/test_m71_scope_guard.py`
- `docs/adr/ADR_073_scope_guard_code_integration.md`
- `docs/milestones/M71_scope_guard_code_integration.md`

## Archivos modificados

- `core/cognitive_pipeline.py`

## Responsabilidad del modulo
`ScopeGuardManager` evalua cada turno y clasifica el alcance en tres estados:

- `in_scope`: permitido para ROBY Personal Operations.
- `review_required`: requiere revision humana antes de actuar.
- `out_of_scope`: excluido de ROBY.

## Dominios bloqueados

- bancos;
- cuentas;
- billeteras;
- pagos;
- inversiones;
- compras.

## Dominios permitidos

- memoria domestica;
- documentos;
- agenda;
- conocimiento personal;
- tareas;
- conversacion;
- organizacion personal.

## Dominios con revision humana

- decisiones medicas;
- decisiones legales;
- acciones externas.

## Integracion con CognitivePipeline
`CognitivePipeline` acepta `scope_guard: ScopeGuardManager | None`.
Cuando existe, ejecuta `scope_guard.observe_turn(text)` y agrega sus `system_prompt_lines()` al prompt del sistema.

## Verificacion ejecutada

```text
pytest -q tests/test_m71_scope_guard.py
11 passed

pytest -q
756 passed
```

## Verificacion pendiente
Ruff queda pendiente para ejecucion local porque el entorno actual no tiene instalado el paquete `ruff`.

## Cierre
M71 queda listo como primer guardrail operativo de Fase VII. El siguiente bloque recomendado es M72 - Household Memory, apoyado sobre las reglas de alcance definidas por Scope Guard.
