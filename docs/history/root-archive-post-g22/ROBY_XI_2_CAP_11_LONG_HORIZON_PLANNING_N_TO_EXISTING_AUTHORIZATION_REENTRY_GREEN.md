# ROBY XI.2 — CAP-11 — Long-horizon P(N) → existing Authorization re-entry A(N) — GREEN

## Gobernanza

- Objetivo superior: **1 — completar CAP-11 Investigación autónoma profunda N-step**.
- Capacidad: forwarding del Planning long-horizon `P(N)` hacia la Authorization re-entry existente.
- Owner canónico preservado: `GovernedMultiStepInvestigationAuthorizationReentryV1`.
- Autoridad de política preservada: `GovernedIndependenceAuthorizationBoundaryV1`.
- Bridge histórico generalizado: `GovernedLongHorizonInvestigationA2AuthorizationReentryV1`.
- No se crea authorization owner, boundary, bridge, manager, loop ni autoridad paralela.
- Frontera preservada: **A(N) producido → STOP antes de Execution**.

## Baseline de entrada

Baseline local certificada por el usuario antes del RED: **13.713 PASS + Ruff limpio**.

El RED long-horizon añadió dos contratos intencionalmente fallidos para P3→A3 y P4→A4. La
certificación local confirmó que ambos fallaban antes de alcanzar Authorization (`spy.calls == 0`)
y que el único ruido adicional era un I001 de orden de imports en el test. El archivo de imports
ordenados aportado por el usuario se integra en este GREEN.

## Corrección contractual descubierta durante GREEN

Una vez removido el guard P2 del bridge, el owner canónico fue alcanzado correctamente y reveló
que el fixture long-horizon actual produce la decisión de Authorization que corresponda a la
política registrada. En el fixture actual esa decisión puede ser `REVIEW_REQUIRED` por política de
iniciación no declarada; el bridge no tiene autoridad para convertirla en `MAY_INITIATE`.

Por tanto, el contrato se corrige para exigir exactamente la decisión devuelta por la autoridad
canónica y derivar `eligible_for_existing_execution` únicamente de `MAY_INITIATE`. Esto preserva
la gobernanza y evita convertir el bridge en una segunda autoridad de Authorization.

## GREEN quirúrgico

Se eliminan únicamente los supuestos rígidos P2/A2 del bridge histórico. La admisión long-horizon
pasa a aceptar un Planning N-step válido cuando:

1. `2 <= planning_reentry.current_step <= state.max_acquisitions`.
2. `planning_reentry.current_step == state.current_step`.
3. `state.consumed_acquisitions == planning_reentry.current_step - 1`.
4. `planning_reentry.remaining_acquisitions > 0`.
5. `planning_reentry.remaining_acquisitions == state.remaining_acquisitions`.
6. Requirement, plan, episode, source y world snapshot permanecen exactamente alineados.
7. El owner canónico de Authorization se invoca una sola vez.
8. La salida A(N) conserva el mismo step y remaining budget de P(N).
9. El authorization id no puede reutilizar uno previo del episodio.
10. La decisión se preserva exactamente desde la autoridad canónica.
11. `eligible_for_existing_execution=True` sólo puede derivar de `MAY_INITIATE`.
12. Execution y Reasoning no se invocan en este bloque.

Los nombres públicos históricos `A2`/`P2`, schema y rationale existentes se conservan para evitar
una migración de API innecesaria; la semántica interna queda generalizada a N-step.

## Compatibilidad histórica

El camino P2→A2 continúa protegido por sus tests históricos. No se modifica
`GovernedMultiStepInvestigationAuthorizationReentryV1`, ni
`GovernedIndependenceAuthorizationBoundaryV1`, ni ninguna superficie de Execution.

## Evidencia local del bloque

- Contrato P3→A3 / P4→A4 + P2→A2 histórico + owner canónico: **20 PASS**.
- Superficie ampliada Authorization/Execution N-step relacionada: **39 PASS**.
- `python -m compileall -q app tests/...`: limpio.
- Líneas > 88 en producción/test afectados: 0.
- Ruff no está disponible en el contenedor de construcción.

La promoción a baseline oficial requiere certificación local completa con:

`ruff check .`

`pytest -q`
