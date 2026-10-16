# RP.19.1 — Agenda cognitiva persistente

## Resultado

El `CognitiveAgendaManager` continúa siendo la única frontera de agenda del núcleo
cognitivo oficial. RP.19.1 agrega persistencia como un puerto inyectable y un
repositorio SQLite; no agrega residentes, scheduler, memoria paralela ni lifecycle.

## Auditoría de integración

- `CognitiveCoreRuntime` sigue exponiendo la misma instancia de agenda que posee
  `ContinuousInternalCognitiveLoop`.
- El ciclo refresca agenda, delibera, reflexiona, actualiza pensamiento, hipótesis,
  world model y memoria episódica en el orden certificado por RP.18.
- Cognitive Episodic Memory conserva episodios derivados del world model; no se
  usa como almacenamiento sustituto de asuntos abiertos.
- Recordatorios conservan su store, polling y lifecycle propios. La agenda sólo
  consume señales autorizadas; no programa ni dispara recordatorios.
- Metas y proyectos conservan sus repositorios y servicios autoritativos. La
  agenda persiste su lectura ejecutiva, no duplica esas entidades.

## Contrato persistente

Cada asunto conserva:

- clave estable, clase y título;
- fuentes y puntaje ejecutivo;
- prioridad, urgencia y relevancia;
- estado `active`, `watching` o `blocked`;
- motivo (`rationale`);
- condiciones explícitas de reanudación;
- primera y última observación;
- expiración opcional.

Los estados terminales `closed` y `archived` se conservan como tombstones para
impedir que una señal idéntica recree automáticamente un asunto resuelto. Un
asunto puede reabrirse de forma explícita.

## Restauración y lifecycle

El repositorio se construye durante el wiring del mismo núcleo cognitivo. El
manager carga los asuntos abiertos en su constructor, antes de que el lifecycle
oficial inicie el loop residente. No existe un proceso de restauración separado.

Variables:

- `ROBY_COGNITIVE_AGENDA_PERSISTENCE_ENABLED` (por defecto `true`)
- `ROBY_COGNITIVE_AGENDA_DB_PATH` (por defecto `.roby/cognitive_agenda.db`)

## Semántica de refresco

Las señales actuales actualizan o crean asuntos. Los asuntos restaurados que no
reciben una señal durante un ciclo permanecen abiertos, porque ausencia de señal
no equivale a resolución. La expiración archiva; el cierre y archivo explícitos
retiran el asunto del working set. Los fallos de una fuente quedan aislados como
en RP.11.

## Compatibilidad

Los constructores y campos previos mantienen valores por defecto. Sin repositorio,
el manager conserva el comportamiento en memoria usado por las pruebas y por
integraciones explícitas existentes.
