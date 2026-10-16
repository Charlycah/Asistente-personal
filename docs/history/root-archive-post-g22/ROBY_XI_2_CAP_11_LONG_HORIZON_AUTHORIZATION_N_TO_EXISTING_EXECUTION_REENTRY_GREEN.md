# ROBY XI.2 — CAP-11 Long-horizon A(N) → existing Execution re-entry E(N) — GREEN quirúrgico

## Estado de entrada

Baseline contractual local del usuario: RED limpio en Ruff con exactamente 2 fallos intencionales y 13.716 tests restantes verdes. La baseline GREEN anterior certificada era 13.715 PASS + Ruff limpio.

## Gobernanza

Se conserva una única autoridad de Execution: `GovernedMultiStepInvestigationExecutionReentryV1`.

No se crea executor, gateway, bridge, manager ni autoridad nueva. El único cambio productivo está en el bridge histórico `GovernedLongHorizonInvestigationE2ExecutionReentryV1`, cuyo nombre público E2 se conserva por compatibilidad.

## Cambio quirúrgico

Archivo productivo modificado:

`app/governed_long_horizon_investigation_e2_execution_reentry.py`

La elegibilidad deja de fijar `current_step == 2` y `remaining_acquisitions == 1`. Ahora exige alineación exacta entre Authorization re-entry y el estado vigente del episodio: paso dentro del budget, paso actual coincidente, adquisiciones consumidas coherentes y budget restante positivo e idéntico.

La validación posterior a Execution deja de exigir E2 terminal. El producto adquirido debe preservar el mismo paso que Authorization y consumir exactamente una adquisición, por lo que E3 puede cerrar con una adquisición restante y E4 con cero.

La elegibilidad para el existing Reasoning re-entry deja de depender de `remaining_acquisitions == 0`. Se deriva exclusivamente del resultado canónico ACQUIRED, del flag `eligible_for_reasoning_reentry`, del estado `AWAITING_REENTRY` y del registro canónico de la adquisición. Este bridge no invoca Reasoning.

## Contrato preservado

- A3 → existing Execution exactamente una vez → E3.
- A4 → existing Execution exactamente una vez → E4.
- A2 → E2 histórico permanece soportado.
- Se preservan episode, authorization, requirement, plan, source, world snapshot y la identidad del Authorization re-entry entregado al owner canónico.
- La adquisición se registra exactamente una vez.
- No se fabrica un execution ID previo.
- STOP antes de Reasoning: el bridge sólo expone elegibilidad para el re-entry existente.

## Validación del entorno de construcción

Targeted GREEN: 17 passed.

Validación relacionada ampliada: 52 passed.

`python -m compileall -q app core tests`: limpio.

La certificación oficial del paquete requiere ejecución local del usuario de:

`ruff check .`

`pytest -q`

No se declara certificación completa hasta recibir esos resultados.
