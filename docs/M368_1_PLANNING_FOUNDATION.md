# M368.1 — Planning Foundation

## Propósito

M368.1 establece `planning_foundation` como la frontera canónica y gobernada para
la futura capacidad de planificación de ROBY XI.2.

La fundación no reemplaza las autoridades creadas o reconciliadas en M367. En
cambio, compone de forma explícita objetivos, tareas, prioridades, contexto,
restricciones y progreso ya existentes.

## Autoridad

- Autoridad canónica: `planning_foundation`.
- Autoridad descriptiva superior: `internal_world_model`.
- Objetivos: `goals_objectives_model`.
- Prioridad: `priority_reasoning`.
- Contexto: `context_state_model`.
- Tareas y progreso: `project_knowledge_model` y sus implementaciones gobernadas.

## Alcance

M368.1 declara siete dominios fundacionales:

1. objetivos;
2. objetivos ejecutivos admitidos;
3. tareas existentes;
4. prioridades;
5. contexto;
6. restricciones;
7. progreso.

## Límites

M368.1:

- es de solo lectura;
- no ejecuta planes;
- no crea objetivos automáticamente;
- no descompone objetivos;
- no replantea planes;
- no agrega persistencia;
- no modifica el comportamiento del runtime.

La descomposición de objetivos pertenece a M368.2. El grafo de tareas, las
dependencias, la evaluación de progreso y la replanificación pertenecen a hitos
posteriores de la serie.

## Resultado arquitectónico

ROBY dispone de un contrato único para consultar los insumos de planificación
sin introducir una autoridad paralela de metas, tareas, prioridades o contexto.
Esta frontera permitirá que los próximos incrementos agreguen razonamiento de
forma pequeña, verificable y gobernada.
