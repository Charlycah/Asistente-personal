# RP.19 — Cognitive Agenda Manager operativo

## Estado

RP.19 queda cerrado como la única agenda cognitiva ejecutiva de ROBY XI.2. Opera dentro de `CognitiveCoreRuntime` y del `ContinuousInternalCognitiveLoop`; no posee thread, scheduler, residente, memoria ni lifecycle propios.

## Capacidades consolidadas

- RP.19.1: persistencia y restauración de asuntos abiertos.
- RP.19.2: activación inteligente y foco efectivo único.
- RP.19.3: reanudación contextual y resolución autónoma declarativa.
- RP.19.4: cola deliberativa explicable con costo, beneficio y dependencias.
- RP.19.5: compromisos cognitivos, progreso y estancamiento.
- RP.19.6: revisión metacognitiva determinista.
- RP.19.7: aprendizaje adaptativo acotado y reversible.
- RP.19.8: salud operativa, invariantes y degradación segura.

## Autoridad y límites

Las metas, proyectos, recordatorios y demás fuentes continúan siendo autoritativas sobre sus datos. La agenda sólo fusiona señales, conserva continuidad y decide el foco cognitivo. No ejecuta herramientas ni acciones externas.

SQLite es persistencia, no autoridad de lifecycle. Si el repositorio falla, el manager conserva la agenda en memoria y publica estado `degraded`; no crea una base alternativa ni detiene el ciclo cognitivo.

## Invariantes certificadas

Cada snapshot operativo verifica:

1. la cantidad de asuntos no supera la capacidad configurada;
2. no existen claves duplicadas;
3. no aparecen asuntos cerrados o archivados en la vista abierta;
4. existe como máximo un compromiso `in_progress`;
5. el foco activado pertenece al snapshot;
6. el compromiso activo pertenece al snapshot.

`CognitiveAgendaOperationalHealth` expone estado, violaciones, fallas de fuentes y fallas del repositorio. `operational_report()` permite obtener la misma evaluación bajo demanda.

## Degradación segura

Las operaciones `load_open`, `status_for`, `save` y `set_status` están aisladas. Una falla conocida de almacenamiento se registra de forma sanitizada por nombre de operación y ROBY continúa con el estado en memoria. Las fallas de fuentes se mantienen separadas de las de persistencia.

## Persistencia y migraciones

La misma tabla `cognitive_agenda_items` conserva el esquema acumulativo de RP.19.1–RP.19.7. Las migraciones continúan siendo aditivas e idempotentes. RP.19.8 no crea una segunda tabla ni cambia la autoridad del repositorio.

## Criterio de cierre

RP.19 queda operativo cuando Ruff está limpio, la suite completa pasa y las pruebas focalizadas confirman persistencia, planificación, ejecución única, metacognición, aprendizaje, observabilidad e indisponibilidad segura del repositorio.
