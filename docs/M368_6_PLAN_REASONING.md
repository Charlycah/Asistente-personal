# M368.6 — Plan Reasoning

## Objetivo

Incorporar una autoridad canónica y pura que razone sobre el estado gobernado
del plan y señale el siguiente paso estructural disponible, sin ejecutar ni
modificar el plan.

## Autoridad

`plan_reasoning` queda subordinada a `progress_evaluation` y consume también el
grafo y la evaluación de dependencias que originaron ese progreso.

## Decisiones gobernadas

La autoridad:

- conserva el orden del grafo;
- recomienda la primera tarea disponible en ese orden;
- expone todas las tareas accionables;
- informa tareas bloqueadas y bloqueadores directos;
- devuelve un resultado completado cuando el plan terminó;
- valida la trazabilidad entre grafo, dependencias y progreso.

## Límites

M368.6 no infiere prioridad, no reordena tareas, no replantea el plan, no
ejecuta acciones, no persiste estado y no modifica el runtime.

## Continuidad

La replanificación queda reservada para M368.7 o para una etapa posterior que
la arquitectura gobernada autorice expresamente.
