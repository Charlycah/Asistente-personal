# M368.5 — Progress Evaluation

## Propósito

M368.5 incorpora `progress_evaluation` como autoridad canónica subordinada a
`dependency_tracking`. Su función es evaluar el avance estructural de un plan a
partir de la completitud explícita ya admitida por M368.4.

## Autoridad

- Autoridad canónica: `progress_evaluation`.
- Autoridad superior: `dependency_tracking`.
- Fuente de estructura: grafo gobernado de M368.3.
- Fuente de completitud: resultado explícito de M368.4.

No se crea otra autoridad de tareas, dependencias, replanificación o ejecución.

## Estados globales

El plan puede quedar evaluado como:

- `not_started`: ninguna tarea fue declarada completada;
- `in_progress`: existe completitud parcial explícita;
- `completed`: todas las tareas fueron declaradas completadas.

La fracción de avance se expresa como tareas completadas sobre tareas totales.
El porcentaje es una presentación derivada de esa fracción y no una predicción.

## Contrato

La evaluación conserva:

- objetivo y grafo de origen;
- conteos de tareas completadas, disponibles y bloqueadas;
- identificadores explícitos de tareas completadas;
- fracción y porcentaje estructurales reproducibles;
- estado global inmutable y trazable.

## Límites

M368.5:

- no pondera tareas por dificultad, duración o prioridad;
- no estima tiempo restante;
- no predice resultados;
- no infiere completitud;
- no ejecuta tareas;
- no replantea planes;
- no agrega persistencia;
- no modifica el comportamiento del runtime.

La replanificación pertenece a M368.6.

## Resultado arquitectónico

ROBY puede evaluar cuánto de un plan está estructuralmente completado y resumir
su estado global utilizando solo evidencia de completitud explícita.
