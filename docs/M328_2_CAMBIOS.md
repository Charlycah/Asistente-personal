# M328.2 — Seguimiento de progreso

## Objetivo

Añadir seguimiento persistente y auditable del avance de los planes de objetivos,
sin ejecutar capacidades ni modificar automáticamente los objetivos asociados.

## Cambios

- Nuevo estado de paso `in_progress`.
- Evidencia persistente por paso.
- Razón obligatoria para pasos bloqueados.
- Transiciones validadas por dependencias.
- Cálculo de progreso por pasos completados sobre el total.
- Detección de próximos pasos disponibles.
- Persistencia atómica de actualizaciones del plan.
- Operaciones de runtime para actualizar pasos y consultar progreso.
- Contadores de planes completados y pasos bloqueados en el snapshot.

## Seguridad

Actualizar el progreso no ejecuta capacidades, no concede permisos, no modifica
la política y no altera el objetivo persistente asociado.

## Validación

- 5 pruebas nuevas de M328.2.
- 10 pruebas combinadas de M328.1 y M328.2 aprobadas.
- `compileall` aprobado.
