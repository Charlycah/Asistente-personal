# ROBY XI.2 — CAP-11 — Long-horizon A(N) → existing Execution re-entry E(N) — RED contractual

## Baseline oficial de entrada

**13.715 PASS + Ruff limpio**, certificada localmente por el usuario.

Este bloque es exclusivamente contractual. No modifica producción, no modifica el owner canónico de Execution y no abre Reasoning.

## Objetivo

Congelar el comportamiento pendiente del wiring long-horizon para que un `A(N)` autorizado y elegible pueda entrar exactamente una vez en `GovernedMultiStepInvestigationExecutionReentryV1`, producir `E(N)`, registrar exactamente una adquisición y terminar antes de Reasoning.

Corte contractual:

`long-horizon A(N)`
→ existing Execution re-entry exactamente una vez
→ `E(N)` preservado
→ `eligible_for_existing_reasoning_reentry`
→ **STOP antes de Reasoning**.

## Casos RED nuevos

### A3 → E3

Bajo budget 4, el contrato exige:

- A3 canónico y `MAY_INITIATE`;
- forwarding por identidad al owner existente;
- una sola invocación de Execution;
- una sola invocación de record de adquisición;
- E3 `ACQUIRED`;
- step 3 preservado;
- remaining budget posterior igual a 1;
- requirement / plan / authorization / episode / source / snapshot preservados;
- execution id nuevo respecto al estado previo;
- elegibilidad para Reasoning expuesta;
- Reasoning no invocado.

### A4 → E4

Bajo budget 4, el contrato exige lo mismo, con:

- step 4 preservado;
- remaining budget posterior igual a 0;
- STOP antes de Reasoning.

## Compatibilidad histórica

El contrato protege el caso certificado `A2 → E2` budget 2. Debe continuar produciendo una sola adquisición, remaining 0 y elegibilidad para Reasoning sin invocarlo.

## Autoridad preservada

El único owner productivo sigue siendo:

`GovernedMultiStepInvestigationExecutionReentryV1`

El bridge long-horizon no ejecuta directamente capacidades, no decide presupuesto, no registra por cuenta propia y no crea un executor alternativo.

## Fallo RED esperado

En la baseline de entrada, A3 y A4 deben ser rechazados por el bridge histórico antes de llegar al owner existente debido a los guards hard-coded A2/E2. La señal contractual esperada es:

`spy.calls == 0` cuando el contrato exige `1`.

El histórico A2→E2 y los contratos N-step del owner canónico deben permanecer verdes.

## Frontera

Este RED termina en:

`A(N) → E(N) → eligible_for_existing_reasoning_reentry`

con **STOP absoluto antes de Reasoning**.
