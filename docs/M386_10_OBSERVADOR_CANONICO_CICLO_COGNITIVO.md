# M386.10 — Observador canónico del ciclo cognitivo

## Propósito

M386.10 incorpora un observador aislado capaz de reunir registros técnicos
M386.9 y producir el contrato canónico de un turno. El observador no descubre
actividad por sí mismo: sólo acepta hechos que un adaptador autorizado le
entregue explícitamente en el futuro.

No se conecta todavía al runtime ni al `UnifiedBrain`.

## Funcionamiento

Cada instancia representa un único ciclo y comienza con los 18 nodos como
`not_recorded`. Al recibir un `CognitiveCycleNodeRecord` validado:

1. comprueba que el nodo pertenece al grafo M386.7;
2. rechaza `not_recorded` como evento, porque ausencia no es observación;
3. impide registrar dos veces el mismo nodo;
4. conserva evidencia y motivos ya validados por M386.9;
5. reconstruye la instantánea en el orden canónico del grafo.

Los eventos pueden llegar en distinto orden. La vista resultante siempre
respeta el orden de los 18 nodos.

## No reescritura

El primer hecho admitido para un nodo no puede sobrescribirse. Esta regla evita
que una etapa posterior transforme retroactivamente una omisión, degradación o
participación en otra historia.

Una instancia puede sellarse. Después del sellado no acepta más registros. El
contrato devuelto sigue siendo inmutable.

## Diagnóstico

`CognitiveCycleObserverDiagnostic` informa solamente:

- contrato canónico actual;
- cantidad de nodos observados;
- cantidad pendiente;
- estado de sellado.

No contiene interlocutor, mensaje, respuesta, recuerdos ni razonamiento
privado. Tampoco concede autoridad.

## Límites

El observador:

- no llama al pipeline;
- no conversa;
- no consulta memoria;
- no clasifica evidencia;
- no decide;
- no ejecuta herramientas;
- no persiste;
- no modifica el grafo;
- no eleva autonomía.

M386.10 tampoco modifica los ciclos históricos. Es la futura frontera de
observación del contrato M386.9, no un nuevo cerebro ni un nuevo coordinador.

## Estado inicial honesto

Sin adaptadores productivos conectados, el observador informa cero nodos
observados y dieciocho pendientes. La existencia del observador no se usa como
prueba de que el ciclo cognitivo completo ya ocurrió.
