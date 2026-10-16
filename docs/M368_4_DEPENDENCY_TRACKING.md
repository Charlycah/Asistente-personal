# M368.4 — Dependency Tracking

## Propósito

M368.4 incorpora `dependency_tracking` como autoridad canónica subordinada a
`task_graph`. Su función es evaluar el estado estructural de cada tarea a partir
de las aristas explícitas del grafo y de un conjunto explícito de tareas
completadas.

## Autoridad

- Autoridad canónica: `dependency_tracking`.
- Autoridad superior: `task_graph`.
- Fuente de relaciones: aristas gobernadas de M368.3.
- Fuente de completitud: entrada explícita del llamador.

No se crea otra autoridad de grafos, progreso, replanificación o ejecución.

## Estados

Cada tarea puede quedar evaluada como:

- `available`: no posee predecesores incompletos;
- `blocked`: posee uno o más predecesores incompletos;
- `completed`: fue declarada explícitamente como completada.

Los bloqueadores informados son únicamente predecesores directos. M368.4 no
infiere bloqueadores transitivos ni convierte completitud declarada en progreso
automático.

## Contrato

La evaluación conserva:

- objetivo y grafo de origen;
- orden estable de nodos;
- estados inmutables;
- bloqueadores directos y trazables;
- rechazo de tareas completadas desconocidas o duplicadas;
- consultas puras de tareas disponibles y bloqueadas.

## Límites

M368.4:

- no modifica el grafo;
- no infiere dependencias nuevas;
- no ejecuta tareas;
- no calcula porcentaje de progreso;
- no replantea planes;
- no agrega persistencia;
- no modifica el comportamiento del runtime.

La evaluación de progreso pertenece a M368.5.

## Resultado arquitectónico

ROBY puede distinguir tareas disponibles, bloqueadas y completadas utilizando
únicamente dependencias explícitas y evidencia de completitud aportada.
