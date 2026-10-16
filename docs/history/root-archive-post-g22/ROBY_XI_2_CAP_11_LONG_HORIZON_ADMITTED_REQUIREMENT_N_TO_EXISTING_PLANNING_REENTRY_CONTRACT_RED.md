# ROBY XI.2 — CAP-11 — Long-horizon admitted R(N) → existing Planning re-entry P(N) — Contract RED

## Gobernanza

- Objetivo superior: **1 — completar CAP-11 Investigación autónoma profunda N-step**.
- Capacidad: forwarding del requisito discriminante admitido `R(N)` hacia Planning existente.
- Owner de Planning preservado: `GovernedMultiStepInvestigationPlanningReentryV1`.
- Bridge histórico bajo prueba: `GovernedLongHorizonInvestigationP2PlanningReentryV1`.
- No se crea planner, bridge, manager, loop ni autoridad paralela.
- Frontera del incremento: **STOP antes de Authorization**.

## Baseline de entrada

Baseline local certificada por el usuario: **13.711 PASS + Ruff limpio**.

## Contrato RED

El RED exige que el bridge long-horizon ya existente deje de estar limitado artificialmente a P2 y pueda reenviar una continuation N-step válida al owner canónico de Planning:

1. `RR2 → R3` admitido debe producir una única llamada al owner existente y devolver `P3`.
2. `RR3 → R4` admitido debe producir una única llamada al owner existente y devolver `P4`.
3. Deben preservarse identidad de continuation, requirement, episode/source/world lineage y budget N-step.
4. El plan producido debe ser nuevo respecto del historial del episodio.
5. La elegibilidad para Authorization puede quedar expuesta, pero **Authorization no se invoca**.
6. Execution y Reasoning tampoco se invocan.
7. El contrato histórico `R2 → P2` permanece protegido por sus tests existentes y no se modifica en RED.

## Resultado RED esperado

Los nuevos tests deben fallar exclusivamente porque `GovernedLongHorizonInvestigationP2PlanningReentryV1` aún contiene guards históricos `current_step == 2` / `remaining_acquisitions == 1`.

No se modifica código de producción en este bloque.
