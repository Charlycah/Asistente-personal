# M366.3 — Semantic Memory

## Propósito

Consolidar la base semántica existente de ROBY bajo la autoridad canónica
`memory_gateway`, sin crear un cuarto almacén ni modificar el comportamiento
estable.

## Inventario reconciliado

- `GovernedPermanentKnowledge`: hechos explícitamente aceptados, revisables y sin
  autoridad de inferencia.
- `PersonalKnowledgeBase`: elementos de conocimiento personal estructurados,
  trazables y versionables.
- `HouseholdKnowledgeService`: acceso operativo al conocimiento doméstico con
  aprendizaje supervisado y confirmación explícita.

Estas piezas estaban presentes pero incompletamente relacionadas. M366.3 las
clasifica como capas complementarias de una misma memoria semántica gobernada.

## Límite esencial

La recuperación externa coordinada por `core.knowledge_gateway` amplía o verifica
información, pero **la recuperación externa no es memoria semántica**. Un resultado
externo solo podrá convertirse en conocimiento persistente mediante una futura
admisión explícita y gobernada.

## No alcance

M366.3:

- no crea persistencia nueva;
- no migra datos;
- no promueve episodios a hechos;
- no aprende automáticamente;
- no modifica el runtime ni el flujo conversacional;
- no sustituye las implementaciones existentes.
