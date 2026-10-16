# M393.6 — Trazabilidad Relacional Gobernada

M393.6 amplía M393.1–M393.5 con una vista de auditoría que reúne el linaje
observable de cada `record_id` relacional. La autoridad continúa siendo
`relationship_memory`, materializada por `RelationshipMemoryManager`; no se crea
gestor, repositorio, persistencia ni autoridad paralela.

## Alcance

`RelationshipMemoryManager.traceability_view()` recibe una vista M393.4 y,
opcionalmente, una evolución M393.5 compatible. Para cada registro expone:

- referencias explícitas de evidencia M393.1–M393.2;
- estado de consolidación M393.3;
- incidencias de consistencia M393.4;
- estado evolutivo M393.5 cuando fue suministrado explícitamente.

Los registros retirados pueden conservar su linaje anterior cuando la vista de
evolución los contiene como `removed`.

## Criterio conservador

La trazabilidad no interpreta causas ni crea evidencia. Sólo encadena referencias
y estados que ya existen en las vistas gobernadas. Cuando se suministra M393.5,
su snapshot actual debe corresponder al snapshot M393.4 para impedir mezclar
linajes incompatibles.

## Invariantes

- `relationship_memory` continúa siendo la única autoridad relacional;
- no modifica registros, confianza, evidencia, snapshots ni historial;
- no resuelve contradicciones ni decide qué versión prevalece;
- no infiere causalidad, identidad, intención ni verdad relacional;
- no persiste, aprende, planifica, autoriza, automatiza ni ejecuta;
- `CanonicalCognitiveCore(` permanece fuera del cambio contractual;
- `.roby/credentials.json` permanece fuera de alcance.
