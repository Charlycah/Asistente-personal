# M389.6 — Reflexión Periódica

## Objetivo

Incorporar una autoridad única de solo lectura para evaluar revisiones analíticas
periódicas de forma visible, explícita y cancelable.

## Autoridad

`PeriodicReflectionAuthority` es la única autoridad de esta capacidad.

No inicia temporizadores, hilos, tareas asíncronas ni procesos en segundo plano.
Una revisión solo ocurre cuando un llamador gobernado invoca explícitamente
`review()` o `review_safely()`.

## Fuente permitida

M389.6 consume exclusivamente `PendingMattersReport`, producido por M389.5.
No vuelve a analizar conversación, memoria o historial.

## Contratos

- `PeriodicReflectionSchedule`
- `PeriodicReflectionReport`
- `PeriodicReflectionCadence`
- `PeriodicReflectionStatus`

Las periodicidades oficiales son manual, diaria, semanal y mensual.
La programación es una definición inmutable; no constituye una automatización.
La cancelación produce una nueva definición cancelada y no modifica el original.

## Garantías

- Solo lectura.
- Visible y cancelable.
- Sin contenido conversacional.
- Sin memoria ni aprendizaje.
- Sin planificación, tareas o recordatorios.
- Sin permisos ni ejecución de acciones.
- Sin procesos en segundo plano.
- Degradación segura y determinista.

## Integración futura

M389.7 podrá consumir `PeriodicReflectionReport` para informes ejecutivos.
M390 podrá utilizar el resultado como evidencia temporal sin reinterpretar
conversaciones ni crear autonomía implícita.
