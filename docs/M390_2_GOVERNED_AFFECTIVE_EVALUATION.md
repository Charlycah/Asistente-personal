# M390.2 — Evaluación Afectiva Gobernada

## Objetivo

Transformar resultados ya certificados de M389 en señales tipadas que puedan ser consumidas por `SimulatedInnerStateAuthority`, sin duplicar análisis ni crear una autoridad emocional paralela.

## Autoridad

M390.2 no introduce una autoridad. `GovernedAffectiveEvaluator` es un adaptador puro y subordinado. La única autoridad del estado interior simulado sigue siendo `SimulatedInnerStateAuthority` (M390.1).

## Fuentes permitidas

- `FunctionalPsychologyReport` (M389.4).
- `PendingMattersReport` (M389.5).
- `UnifiedEpistemicReport` (M389.8).

No se admiten conversaciones brutas, memoria, sensores, personalidad, planner, archivos externos ni credenciales.

## Política de evaluación

La evaluación es determinista y conservadora. Los reportes completos producen señales funcionales codificadas. Los estados `INSUFFICIENT_EVIDENCE` y `DEGRADED` se convierten en `UNKNOWN`/`UNCERTAIN`. Los conflictos epistemológicos se preservan como señal `MIXED`/`CONFLICTED`; nunca se resuelven ocultamente.

Las categorías afectivas describen sólo comportamiento funcional simulado. No afirman consciencia, experiencia subjetiva o emoción real.

## Límites

M390.2 no:

- construye snapshots por sí mismo;
- mantiene estado;
- persiste;
- aprende;
- crea objetivos o tareas;
- modifica memoria, planificación, personalidad o permisos;
- ejecuta acciones;
- modifica `UnifiedBrain`;
- modifica `official_conversation_gateway.py`;
- modifica `.roby/credentials.json`.

## Integración

El flujo permitido es:

`M389.4/M389.5/M389.8 -> GovernedAffectiveEvaluator -> SimulatedInnerStateSignal -> SimulatedInnerStateAuthority`

La conexión automática al ciclo productivo queda reservada para un incremento posterior.
