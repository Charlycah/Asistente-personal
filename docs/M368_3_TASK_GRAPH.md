# M368.3 — Task Graph

## Propósito

M368.3 incorpora `task_graph` como autoridad canónica subordinada a
`goal_decomposition`. Su función es convertir los componentes admitidos de un
objetivo en nodos y representar relaciones de precedencia mediante aristas
explícitas.

## Autoridad

- Autoridad canónica: `task_graph`.
- Autoridad superior: `goal_decomposition`.
- Fuente de nodos: componentes gobernados de M368.2.
- Relación admitida: `precedes`.

No se crea otra autoridad de objetivos, descomposición, dependencias, progreso
o ejecución.

## Contrato

El grafo conserva:

- identificador estable;
- objetivo y descomposición de origen;
- nodos inmutables y trazables;
- aristas explícitas y únicas;
- extremos conocidos;
- ausencia de autorreferencias;
- estructura acíclica;
- consultas puras de predecesores, sucesores, raíces y hojas.

El orden original de los componentes no genera aristas implícitas. Una
precedencia existe solamente cuando fue aportada explícitamente.

## Límites

M368.3:

- no inventa relaciones;
- no realiza seguimiento de dependencias;
- no determina bloqueos operativos;
- no evalúa progreso;
- no replantea planes;
- no ejecuta tareas;
- no agrega persistencia;
- no modifica el comportamiento del runtime.

El seguimiento de dependencias pertenece a M368.4.

## Resultado arquitectónico

ROBY puede representar una estructura dirigida y acíclica de tareas sin
confundir precedencia declarada con ejecución, disponibilidad o progreso.
