# RP.19.5 — Ejecución deliberativa y seguimiento de compromisos

## Alcance

RP.19.5 convierte el primer asunto elegible de la cola deliberativa en un compromiso cognitivo trazable dentro del `CognitiveAgendaManager` canónico. No ejecuta acciones externas y no incorpora schedulers, residentes, runtimes, memorias ni lifecycles adicionales.

## Modelo de compromiso

Cada asunto conserva en la misma agenda persistente:

- estado del compromiso: `pending`, `in_progress`, `stalled` o `completed`;
- instante de inicio;
- progreso monotónico entre 0 y 1;
- instante del último progreso;
- nota de ejecución;
- cantidad de estancamientos detectados.

La activación inicia el compromiso. El progreso sólo cambia mediante evidencia explícita registrada por `record_progress`. Un progreso de `1.0` completa el compromiso, cierra el asunto y conserva el tombstone existente.

## Estancamiento y revisión

Si un compromiso permanece en curso sin progreso durante `commitment_stall_window`, pasa a `stalled`. Un compromiso estancado deja de ocupar el foco efectivo y permite revisar la cola con los demás asuntos elegibles. El asunto no se pierde, no se archiva y puede reanudarse al registrar nuevo progreso.

Los cambios de dependencias y hechos contextuales siguen reconstruyendo la cola deliberativa en cada ciclo oficial. Sólo existe un `active_commitment` publicado por snapshot.

## Persistencia y migración

La tabla `cognitive_agenda_items` incorpora columnas aditivas para el compromiso. La inicialización SQLite migra automáticamente bases de RP.19.1–RP.19.4.
