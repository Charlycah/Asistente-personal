# M393.5 — Evolución Relacional Gobernada

M393.5 amplía M393.1–M393.4 mediante una comparación temporal explícita de dos
vistas relacionales ya gobernadas. La autoridad continúa siendo
`relationship_memory`, materializada por `RelationshipMemoryManager`; no se crea
gestor, repositorio, reloj, memoria ni autoridad paralela.

## Alcance

`RelationshipMemoryManager.evolution_view()` recibe una vista de consistencia
anterior y una actual. Para cada `record_id` observable clasifica el estado como:

- `added`: sólo existe en la vista actual;
- `removed`: sólo existe en la vista anterior;
- `unchanged`: el registro, consolidación e inconsistencias observables coinciden;
- `changed`: el mismo `record_id` presenta una diferencia explícita observable.

## Criterio conservador

M393.5 no interpreta por qué cambió una relación. No usa reloj propio, texto libre,
heurísticas semánticas ni causalidad. Un cambio de `snapshot_id` por sí solo no
constituye cambio relacional. La vista conserva ambos estados y sólo describe la
diferencia observable.

## Invariantes

- `relationship_memory` continúa siendo la única autoridad relacional;
- reutiliza las vistas M393.3–M393.4 y no duplica almacenamiento;
- no modifica registros, confianza, evidencia, snapshots ni historial;
- no decide qué estado es verdadero, preferible o más reciente por inferencia;
- no persiste, aprende, planifica, agenda, autoriza ni ejecuta;
- `CanonicalCognitiveCore(` permanece fuera del cambio contractual;
- `.roby/credentials.json` permanece fuera de alcance.

## Fuera de alcance

M393.5 no realiza seguimiento en background, vencimientos, timers, resolución de
cambios, actualización automática, fusión, borrado, sincronización remota,
aprendizaje, automatización ni ejecución.
