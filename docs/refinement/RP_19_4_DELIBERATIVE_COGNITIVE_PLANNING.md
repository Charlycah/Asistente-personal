# RP.19.4 — Planificación cognitiva deliberativa

## Objetivo

Convertir la agenda cognitiva operativa en una cola deliberativa explicable sin crear un planner, scheduler, residente, lifecycle o memoria paralelos.

## Implementación

`CognitiveAgendaManager` sigue siendo la única autoridad ejecutiva de agenda. Cada señal puede declarar:

- `expected_benefit`: beneficio esperado normalizado;
- `cognitive_cost`: costo cognitivo normalizado;
- `dependencies`: claves de asuntos que deben estar resueltos;
- `context_tags`: etiquetas para reducir cambios de contexto.

El snapshot publica `deliberative_queue`, compuesta por entradas explicables con utilidad, disponibilidad de dependencias, afinidad contextual y rationale determinista.

La utilidad combina el score y las reglas de activación de RP.19.2 con beneficio, costo y afinidad. Las dependencias se satisfacen mediante hechos explícitos `agenda:resolved:<key>` aportados al contexto canónico. No se realizan inferencias libres ni acciones externas.

`primary_focus` mantiene su semántica informativa. `activated_focus` es la primera entrada de la cola deliberativa y continúa siendo el único foco consumido por razonamiento, reflexión, thought stream, world model, memoria episódica y self model.

## Persistencia y migración

La misma tabla SQLite incorpora columnas migrables para beneficio, costo, dependencias y etiquetas. Las bases de RP.19.1–RP.19.3 se actualizan automáticamente con valores compatibles.

## Compatibilidad

Se conservan los contratos de activación, desempate, lifecycle, fuentes y snapshots anteriores. No se agrega infraestructura residente.
