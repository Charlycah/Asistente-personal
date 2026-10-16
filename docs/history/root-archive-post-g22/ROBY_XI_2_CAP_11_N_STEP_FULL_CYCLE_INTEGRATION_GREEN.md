# ROBY XI.2 — CAP-11 — GREEN de integración del ciclo N-step completo

Estado: **GREEN DE INTEGRACIÓN — sin modificación productiva**.

Baseline oficial de entrada: **13.721 PASS + Ruff limpio**.

## Decisión arquitectónica

La solicitud de GREEN productivo fue contrastada contra el circuito real antes de tocar producción.

Se ejecutó una composición end-to-end usando los productos reales de cada frontera como entrada exacta de la siguiente:

`RR2 → R3 → P3 → A3 → E3 → RR3 → R4 → P4 → A4 → E4 → RR4 → STOP`

El recorrido completó correctamente el budget 4 y el intento posterior `RR4 → R5` resultó `NOT_ELIGIBLE` con cero invocaciones de discriminación/continuación.

Por tanto, no existe un defecto productivo demostrado que justifique introducir un nuevo orquestador, loop, manager o autoridad. Hacer un GREEN productivo artificial violaría los STOP boundaries y la regla de una autoridad por capacidad.

## Cambio realizado

Se agregó únicamente el contrato de integración arquitectónica:

`tests/architecture/test_cap11_long_horizon_n_step_full_cycle_green.py`

No se modificó ningún archivo bajo `app/` ni `core/`.

`.roby/config.json` permanece intacto.

## Cobertura integral

El contrato usa:

- RR2 canónico con budget 4 como punto de entrada;
- `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1` para R3/R4;
- `GovernedLongHorizonInvestigationP2PlanningReentryV1` hacia Planning canónico;
- `GovernedLongHorizonInvestigationA2AuthorizationReentryV1` hacia Authorization canónica;
- `GovernedLongHorizonInvestigationE2ExecutionReentryV1` hacia Execution canónica;
- `GovernedLongHorizonInvestigationRR2TerminalClosureV1` hacia Reasoning canónico;
- productos reales de cada etapa, sin reconstruir artificialmente la frontera siguiente;
- una misma autoridad de registry/runtime durante R3/R4;
- una sola adquisición y una sola reentrada de reasoning por step.

Verifica:

- R3 con remaining 2;
- E3 con remaining 1;
- RR3 `RECORDED` / `AWAITING_REQUIREMENT`;
- R4 con remaining 1;
- E4 con remaining 0;
- RR4 `CLOSED` / `BUDGET_EXHAUSTED`;
- lineage acumulado de requirement/plan/authorization/execution/reentry IDs;
- exactamente dos lecturas y dos reentradas de reasoning;
- RR4 no produce R5.

## Validación local del entorno de construcción

- nuevo contrato end-to-end: `1 passed`;
- batería relacionada ampliada: `30 passed`;
- `python -m compileall -q app core tests`: limpio;
- scan manual del nuevo test: sin líneas >88;
- comparación contra la GREEN 13.721 de entrada: `app/` sin diferencias, `core/` sin diferencias y `.roby/config.json` idéntico.

Ruff no está disponible en el contenedor de construcción; la certificación oficial continúa requiriendo la ejecución local del usuario.

## Gate de cierre CAP-11

Si `ruff check .` y `pytest -q` pasan localmente con este contrato añadido, CAP-11 N-step puede cerrarse como circuito gobernado completo **sin ningún GREEN productivo adicional**.
