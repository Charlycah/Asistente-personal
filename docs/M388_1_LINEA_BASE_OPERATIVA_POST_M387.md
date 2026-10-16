# M388.1 — Línea base operativa posterior a M387

## Propósito

M388.1 convierte el diagnóstico posterior a M387 en una proyección automatizada,
inmutable y de sólo lectura. No ejecuta conversaciones, no conecta nodos nuevos
y no cambia el comportamiento productivo.

## Partición estructural

El grafo conserva 18 nodos:

- 14 poseen adaptadores capaces de aportar evidencia canónica;
- 4 conservan una brecha estructural:
  `perception_and_evidence`, `epistemic_classification`, `cognitive_state` y
  `relational_affective_context`.

Esta clasificación informa capacidad de evidencia, no participación permanente.

## Proyección operacional

La línea base reutiliza `OperationalCycleDiagnostic` y proyecta los ciclos
retenidos por el gateway oficial. Distingue:

- nodos observados al menos una vez;
- nodos que participaron al menos una vez;
- nodos nunca observados;
- prefijo conectado e interrupción del último turno;
- completitud del último ciclo.

Un nodo omitido está observado, pero no participado.

## Escenarios de referencia

Se declaran seis escenarios acotados para las próximas etapas:

1. conversación identificada;
2. conversación con memoria;
3. conversación con conocimiento;
4. decisión gobernada;
5. acción externa gobernada;
6. degradación segura.

Los escenarios describen evidencia requerida. El diagnóstico no los ejecuta ni
declara éxito por la sola existencia de módulos.

## Privacidad y autoridad

La línea base no contiene mensajes, respuestas, recuerdos, identidades o
sesiones. No concede permisos, no ejecuta acciones y no modifica los ciclos.

## Resultado

M388.1 establece el punto cero automatizado para M388. La siguiente prioridad
permanece en `perception_and_evidence`, comenzando por el canal de texto real.
