# ADR 194 — Executive Cognitive Runtime

## Estado

Aceptado.

## Contexto

ROBY ya disponía de coordinación ejecutiva gobernada en M91 y de un runtime
cognitivo ordenado en M189–M193. Faltaba proyectar esa coordinación en el turno
operacional sin convertirla en ejecución automática.

## Decisión

Agregar `ExecutiveCognitiveRuntimeContributor` como quinta etapa oficial del
orquestador cognitivo, después de reflexión y antes de contribuyentes
personalizados.

Solo se publican coordinaciones aprobadas o activas que no requieran revisión.
Las referencias de coordinación, plan, directivas e hitos permanecen fuera del
prompt y se conservan como linaje.

## Consecuencias

- El proveedor recibe prioridades, subsistemas, dependencias y restricciones.
- La coordinación ejecutiva permanece consultiva.
- Las directivas sensibles requieren revisión humana.
- La autoridad de herramientas, tareas y acciones no cambia.
