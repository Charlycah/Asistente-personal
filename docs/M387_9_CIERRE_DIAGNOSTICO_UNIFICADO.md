# M387.9 — Cierre diagnóstico unificado

## Propósito

M387.9 completa el último nodo del grafo cognitivo objetivo. El nodo
`unified_diagnostics` confirma si la reflexión posterior y la evaluación de
aprendizaje fueron observadas antes de sellar el expediente del turno.

## Una sola vista

No se crea un sistema de diagnóstico paralelo. La evidencia de cierre alimenta
el mismo ciclo canónico y `UnifiedBrain.diagnostics` conserva la vista acumulada
de conversación, reflexión y brecha de observación.

## Estados

- reflexión y aprendizaje evaluados: `PARTICIPATED`;
- sólo uno observado: `DEGRADED`;
- ninguno observado: `OMITTED`.

La ausencia de candidato de aprendizaje cuenta como evaluación realizada, no
como aprendizaje efectuado.

## Límites

El diagnóstico no contiene mensajes, respuestas, recuerdos, candidatos ni
identidades. No ejecuta acciones, no reintenta turnos, no cambia decisiones y no
concede autoridad. Tampoco oculta las brechas anteriores del grafo: un cierre
diagnosticado no convierte en conectados los nodos que carecen de evidencia.
