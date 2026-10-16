# ROBY XI.2 — CAP-11 — Long-horizon admitted R(N) → existing Planning re-entry P(N) — GREEN

## Gobernanza

- Objetivo superior: **1 — completar CAP-11 Investigación autónoma profunda N-step**.
- Capacidad: forwarding del requisito discriminante admitido `R(N)` hacia Planning existente.
- Owner de Planning preservado: `GovernedMultiStepInvestigationPlanningReentryV1`.
- Bridge histórico generalizado: `GovernedLongHorizonInvestigationP2PlanningReentryV1`.
- No se crea planner, bridge, manager, loop ni autoridad paralela.
- Frontera preservada: **P(N) producido → STOP antes de Authorization**.

## Baseline de entrada

Baseline local certificada por el usuario: **13.711 PASS + Ruff limpio**.

## GREEN quirúrgico

Se eliminan únicamente los supuestos rígidos P2 del bridge histórico. La admisión long-horizon
pasa a aceptar continuations N-step válidas cuando:

1. `current_step >= 2`.
2. `continuation.current_step` coincide con el step del episode state resultante.
3. `continuation.remaining_acquisitions` coincide con el budget restante del episode state.
4. Requirement, episode, source y world lineage permanecen exactamente alineados.
5. El owner canónico de Planning se invoca una sola vez.
6. La salida de Planning conserva el mismo step y budget de la continuation recibida.
7. El plan producido es nuevo respecto del historial del episodio.
8. La elegibilidad para Authorization puede exponerse, pero Authorization no se invoca.
9. Execution y Reasoning tampoco se invocan.

Se preservan los nombres públicos históricos P2 para evitar una migración de API no requerida;
la semántica interna queda generalizada a N-step sin introducir otra autoridad.

## Evidencia local del bloque

- Contrato nuevo R3→P3 / R4→P4 + histórico R2→P2: **8 PASS**.
- Superficie CAP-11 ampliada de continuation/planning: **34 PASS**.

La promoción a baseline oficial requiere certificación local completa con:

`ruff check .`

`pytest -q`
