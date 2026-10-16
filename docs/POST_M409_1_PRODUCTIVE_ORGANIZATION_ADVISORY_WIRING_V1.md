# Post-M409.1 — Productive Organization Advisory Wiring v1

## Estado

**IMPLEMENTED / CERTIFICATION PENDING USER GATES**

## Propósito

Extender el branch productivo ya existente de Explicit Deliberation para que una
referencia organizacional estructurada del turno pueda aportar evidencia real de
Goals, Projects y Reminders al advisory M391.6, sin crear una nueva autoridad ni
un segundo camino de decisión.

## Cadena productiva

1. `OfficialConversationGateway.submit()` conserva identificación como primera
   precedencia.
2. El Producer v1 detecta únicamente deliberación humana explícita.
3. El Adapter v1 produce las opciones M391.6 y sus bindings de provenance.
4. Las referencias organizacionales estructuradas del turno se adquieren por
   `alternative_ordinal`; no se extraen del texto.
5. `ProductiveOrganizationAdvisoryWiring` lee las fuentes productivas ya
   registradas en `OfficialRuntimeCapabilityRegistry`:
   - `household.goals`;
   - `household.projects`;
   - `resident.reminders`.
6. `PartialCanonicalOrganizationSnapshotBuilder` conserva `AVAILABLE`, `EMPTY`
   y `UNAVAILABLE`; Tasks permanece `UNAVAILABLE`.
7. `OrganizationDecisionExactIdentityLinker` acepta sólo `item_id` o
   `source_reference` exactos.
8. `PartialOrganizationM3915Consumer` consume el snapshot mediante M391.5.
9. `LinkedOrganizationM3916AdvisoryAssembler` delega en el
   `CanonicalDecisionFacade` existente.
10. El realizer productivo existente produce el `LocalConversationTurn`
    consultivo.

## Fallback gobernado

- Sin referencias organizacionales, se preserva exactamente el advisory explícito
  previo.
- Una referencia desconocida, ambigua, conflictiva o cuya fuente esté
  `UNAVAILABLE` no se adivina: se vuelve al advisory explícito previo.
- Los turnos con `external_evidence` mantienen la ruta runtime preexistente y no
  entran en este interceptor local.

## Invariantes

- Goals / Projects / Reminders son las únicas fuentes productivas admitidas en v1.
- Tasks = `UNAVAILABLE / DEFERRED`.
- Las referencias son per-turn y estructuradas; no hay matching por título,
  fuzzy, semantic ni LLM.
- `PersonalOrganizationAuthority` permanece autoridad de M391.5.
- `CanonicalDecisionFacade` permanece la única fachada de entrada a M391.6.
- `OfficialConversationGateway` sólo realiza el wiring mínimo.
- No hay nueva authority, coordinator binding, repository, memoria, persistencia,
  background processing ni ejecución de acciones.
- M410, networking y Residential permanecen fuera de alcance.

## Validación local disponible

Bloque focalizado: **28 tests passed**.

La certificación final continúa reservada a los gates del árbol oficial:
`python scripts/generate_quality_baseline.py`, `ruff check .` y `pytest -q`.
