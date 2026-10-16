# M393.4 — Consistencia Relacional Gobernada

M393.4 amplía M393.1–M393.3 mediante un diagnóstico de consistencia de solo
lectura bajo la autoridad existente `relationship_memory`, materializada por
`RelationshipMemoryManager`. No crea gestor, repositorio, memoria ni autoridad
paralela.

## Alcance

`RelationshipMemoryManager.consistency_view()` consume la consolidación M393.3 y
expone inconsistencias observables sin reescribir registros. El diagnóstico puede
mostrar:

- `exact_duplicate`: dos registros con la misma clase relacional y el mismo
  contenido después de una normalización estrictamente sintáctica;
- `explicit_contradiction`: contradicción declarada explícitamente entre dos
  `record_id` existentes y respaldada por una referencia de evidencia;
- `explicit_incompatibility`: incompatibilidad declarada explícitamente entre dos
  `record_id` existentes y respaldada por una referencia de evidencia.

## Criterio conservador

M393.4 no infiere contradicciones ni incompatibilidades desde texto libre. Sólo
la duplicación exacta puede detectarse automáticamente porque depende de igualdad
de clase y contenido normalizado, no de interpretación semántica.

Las contradicciones e incompatibilidades deben llegar como relaciones explícitas,
trazables y válidas. El diagnóstico conserva simultáneamente todos los conflictos
observados y no selecciona cuál registro es correcto.

## Invariantes

- `relationship_memory` continúa siendo la única autoridad relacional;
- M393.4 reutiliza `consolidation_view()` y no duplica almacenamiento;
- no modifica `RelationshipMemoryRecord`, confianza, snapshots ni historial;
- no resuelve, fusiona, elimina, corrige ni prioriza registros;
- no infiere significado relacional desde texto libre;
- no persiste, aprende, planifica, agenda, autoriza ni ejecuta;
- `CanonicalCognitiveCore(` permanece fuera del cambio contractual;
- `.roby/credentials.json` permanece fuera de alcance.

## Fuera de alcance

M393.4 no realiza deduplicación física, resolución automática de contradicciones,
fusión de memorias, escritura, actualización de relaciones, aprendizaje,
background, timers, automatización ni ejecución.
