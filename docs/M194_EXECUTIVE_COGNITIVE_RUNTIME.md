# M194 — Executive Cognitive Runtime

M194 integra la coordinación ejecutiva gobernada de M91 en el runtime cognitivo
operacional iniciado en M189.

## Objetivo

Proyectar coordinaciones ejecutivas aprobadas o activas como contexto consultivo
para el turno actual, después de conversación viva, razonamiento, planificación y
reflexión.

## Flujo oficial

1. Living conversation runtime.
2. Governed reasoning runtime.
3. Executive planning runtime.
4. Adaptive reflection runtime.
5. Executive cognitive runtime.
6. Contribuyentes cognitivos adicionales.
7. Tool runtime.
8. Proveedor local.

## Política

Solo coordinaciones `approved` o `active` pueden aportar contexto. Las
coordinaciones `draft`, `review_required`, `paused`, `completed` y `cancelled`
se conservan como linaje pero no modifican el prompt.

Una coordinación que incluya autonomía, revisión humana o prioridad crítica se
considera sensible y no se publica aunque su estado sea aprobado.

## Frontera de autoridad

La integración:

- no ejecuta directivas;
- no invoca herramientas;
- no crea tareas;
- no cambia estados de planes o coordinaciones;
- no modifica memoria;
- no llama al proveedor;
- no concede permisos.

Las directivas solo orientan la estructura y coordinación de la respuesta.
