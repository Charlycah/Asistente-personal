# ROBY XI.2 — CAP-11 — Long-horizon P(N) → existing Authorization re-entry A(N) — CONTRACT RED

## Gobernanza

- Objetivo superior: **1 — completar CAP-11 Investigación autónoma profunda N-step**.
- Baseline oficial de entrada: **13.713 PASS + Ruff limpio**.
- Capacidad bajo contrato: forwarding de `P(N)` long-horizon ya planificado hacia la
  Authorization re-entry existente.
- Owner canónico preservado: `GovernedMultiStepInvestigationAuthorizationReentryV1`.
- Bridge histórico bajo prueba: `GovernedLongHorizonInvestigationA2AuthorizationReentryV1`.
- No se crea Authorization boundary, bridge, manager, loop, planner ni gateway paralelo.
- Frontera dura: **A(N) producido → STOP antes de Execution**.

## Reconciliación que origina este RED

El owner canónico de Authorization re-entry ya acepta N-step. Sus invariantes actuales
validan un step gobernado dentro del budget constitucional, adquisiciones previas
consumidas y budget restante positivo. El residual está únicamente en el bridge
long-horizon histórico, que todavía exige `current_step == 2` y
`remaining_acquisitions == 1` tanto antes como después de invocar el owner existente.

Por ello este RED no autoriza cambios en el owner canónico de Authorization.

## Contrato RED

El RED debe demostrar exclusivamente el wiring faltante del bridge histórico:

1. Un `P3` long-horizon canónico y elegible se forwardea exactamente una vez al owner
   `GovernedMultiStepInvestigationAuthorizationReentryV1` y produce `A3`.
2. Un `P4` long-horizon canónico y elegible se forwardea exactamente una vez al mismo
   owner y produce `A4`.
3. El objeto exacto `planning_reentry` es el único que puede entrar a Authorization.
4. Requirement, plan, episode, source, world snapshot, step y remaining budget deben
   conservarse sin reescritura.
5. El `authorization_id` producido debe ser nuevo respecto del historial del episodio.
6. Sólo `MAY_INITIATE` puede exponer `eligible_for_existing_execution=True`.
7. Esa elegibilidad es declarativa: `invokes_execution=False`, `invokes_reasoning=False`
   y el bridge no puede ejecutar ningún gateway.
8. El comportamiento histórico `P2 → A2` permanece protegido por sus tests existentes.

## RED esperado

Con producción intacta, los nuevos casos P3/A3 y P4/A4 deben fallar antes de invocar
Authorization, porque `_eligible(...)` del bridge histórico continúa limitado a P2:

- `planning_reentry.current_step == 2`
- `planning_reentry.remaining_acquisitions == 1`

Por tanto el síntoma RED correcto es `authorization spy calls == 0`, mientras los tests
históricos P2/A2 siguen verdes.

## Prohibiciones del bloque

No modificar producción durante RED. No tocar `GovernedMultiStepInvestigationAuthorizationReentryV1`,
`GovernedIndependenceAuthorizationBoundaryV1`, Execution, Reasoning, Planning, Episode,
Memory, World Model, networking, persistencia, scheduler, background processes ni
`.roby/config.json`.

## Corte posterior

Sólo después de un RED contractual acotado y certificado corresponde un GREEN quirúrgico
sobre `GovernedLongHorizonInvestigationA2AuthorizationReentryV1`, reemplazando únicamente
los supuestos P2/A2 por invariantes N-step ya canónicas y preservando P2→A2.
