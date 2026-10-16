# M393.7 — Auditoría Relacional Gobernada

## Objetivo

Cerrar la serie de memoria relacional enriquecida con una vista diagnóstica final y de sólo lectura bajo la autoridad canónica `relationship_memory`.

## Autoridad

La única autoridad continúa siendo `RelationshipMemoryManager`. M393.7 no crea gestores, almacenes, planificadores ni autoridades paralelas.

## Entrada

La auditoría consume exclusivamente `RelationshipTraceabilityView` M393.6. No recupera memoria adicional, no inspecciona texto libre y no fabrica evidencia.

## Estados

- `clear`: el linaje explícito no contiene hallazgos de auditoría.
- `review_required`: existe revisión explícita pendiente o un cambio evolutivo observable.
- `conflicted`: existe conflicto de consolidación o incidencia de consistencia explícita.
- `insufficient_evidence`: falta evidencia explícita o el registro está marcado como no respaldado.

Los conflictos tienen prioridad diagnóstica. La auditoría no decide qué registro prevalece ni modifica los estados fuente.

## Invariantes

- sólo lectura;
- determinista;
- una única autoridad por capacidad;
- sin inferencia semántica nueva;
- sin persistencia nueva;
- sin aprendizaje, automatización, permisos ni ejecución;
- sin cambios contractuales en `CanonicalCognitiveCore(`.
