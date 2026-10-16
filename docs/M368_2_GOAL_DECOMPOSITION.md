# M368.2 — Goal Decomposition

## Propósito

M368.2 incorpora `goal_decomposition` como autoridad canónica subordinada a
`planning_foundation` para representar la descomposición gobernada de un
objetivo admitido.

La capacidad convierte componentes explícitos y ordenados en una estructura
inmutable, determinista y trazable. No inventa pasos que el usuario o una
autoridad previa no hayan aportado.

## Autoridad

- Autoridad canónica: `goal_decomposition`.
- Autoridad superior: `planning_foundation`.
- Fuente de objetivos: `goals_objectives_model`.
- Modo de admisión: componentes explícitos.

No se crea una segunda autoridad de objetivos, tareas, prioridades o contexto.

## Contrato

Cada descomposición conserva:

- identificador estable de la descomposición;
- identificador y título del objetivo padre;
- componentes explícitos;
- orden contiguo;
- vínculo trazable de cada componente con el objetivo padre;
- estado `ready` o `clarification_required`.

Una descomposición lista requiere entre dos y veinte componentes únicos. Si no
hay suficiente estructura explícita, ROBY solicita aclaración en lugar de
completar el objetivo mediante inferencia silenciosa.

## Límites

M368.2:

- no crea objetivos automáticamente;
- no infiere componentes ocultos;
- no crea un grafo de tareas;
- no infiere dependencias;
- no evalúa progreso;
- no replantea planes;
- no ejecuta acciones;
- no agrega persistencia;
- no modifica el comportamiento del runtime.

El grafo de tareas pertenece a M368.3 y el seguimiento de dependencias a
M368.4.

## Resultado arquitectónico

ROBY puede representar cómo un objetivo explícito se divide en componentes
ordenados sin confundir estructura con ejecución. La salida es pura y puede ser
revisada, explicada y utilizada por hitos posteriores de la serie.
