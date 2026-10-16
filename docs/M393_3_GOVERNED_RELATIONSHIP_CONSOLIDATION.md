# M393.3 — Consolidación Relacional Gobernada

M393.3 amplía M393.1–M393.2 mediante una consolidación estrictamente diagnóstica
bajo la autoridad existente `relationship_memory`, materializada por
`RelationshipMemoryManager`. No crea gestor, repositorio, memoria ni autoridad
paralela.

## Alcance

`RelationshipMemoryManager.consolidation_view()` consume la vista enriquecida y
la evidencia explícita M393.2 para clasificar cada registro como:

- `consolidated`: evidencia explícita verificada con respaldo suficiente;
- `review_required`: existe evidencia, pero no alcanza el criterio conservador;
- `conflicted`: existe evidencia explícitamente disputada o rechazada;
- `unsupported`: no existe evidencia explícita asociada.

La clasificación es una vista inmutable y determinista. `consolidated` significa
únicamente "suficientemente respaldado en esta evaluación"; no convierte el
registro en hecho, no cambia su confianza histórica y no persiste ningún estado.

## Prioridad conservadora

Los conflictos tienen prioridad sobre cualquier respaldo positivo. Una evidencia
verificada no oculta una evidencia disputada o rechazada. La ausencia de evidencia
permanece visible y la evidencia débil o no verificada exige revisión.

## Invariantes

- `relationship_memory` continúa siendo la única autoridad relacional;
- M393.3 reutiliza `enriched_view()` y no duplica almacenamiento;
- no modifica `RelationshipMemoryRecord.confidence`, snapshots ni historial;
- no infiere evidencia, identidad, vínculo o causalidad desde texto libre;
- no persiste, aprende, planifica, agenda, autoriza ni ejecuta;
- `CanonicalCognitiveCore(` permanece fuera del cambio contractual;
- `.roby/credentials.json` permanece fuera de alcance.

## Fuera de alcance

M393.3 no realiza consolidación física de memoria, escritura automática,
resolución de contradicciones, actualización de relaciones, captura automática de
evidencia, timers, background, automatización ni ejecución.
