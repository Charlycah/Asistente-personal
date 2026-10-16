# M389.5 — Asuntos Pendientes

## Objetivo

Incorporar una autoridad única, gobernada y de solo lectura que identifique
asuntos no resueltos usando exclusivamente resultados codificados de M389.1,
M389.2, M389.3 y M389.4.

## Autoridad

`PendingMattersAuthority` es la única autoridad de esta capacidad. Produce un
`PendingMattersReport` inmutable y determinista. No lee texto conversacional ni
almacena transcripciones.

## Fuentes permitidas

- `EpistemicAssessment` — M389.1.
- `ConversationReflectionReport` — M389.2.
- `HistoricalAnalysisReport` — M389.3.
- `FunctionalPsychologyReport` — M389.4.

## Categorías

- pregunta abierta;
- decisión pendiente;
- tema para retomar;
- solicitud incompleta;
- contradicción posible;
- confirmación faltante;
- dependencia externa;
- información insuficiente.

La implementación inicial solo emite una categoría cuando existe evidencia
codificada suficiente en las fuentes. Las categorías reservadas permanecen en
el contrato para evolución posterior sin ampliar autoridad.

## Estados de resolución

`open`, `partially_resolved`, `resolved` y `unknown`.

M389.5 nunca modifica esos estados, resuelve asuntos, crea tareas, crea
recordatorios ni agenda acciones.

## Clasificación epistemológica

Cada asunto conserva un `EpistemicLevel` ya existente: `fact`, `inference`,
`hypothesis` o `unknown`. La autoridad no promueve hipótesis a hechos.

## Seguridad

- Solo lectura y sin autoridad ejecutiva.
- Sin memoria ni aprendizaje.
- Sin planificación ni permisos.
- Sin tareas, recordatorios o automatizaciones.
- Sin contenido conversacional privado.
- Sin acceso a `.roby/credentials.json`.
- Sin modificaciones del gateway oficial.

## Degradación

`analyze_safely` devuelve un informe `degraded`, vacío y trazable. Ante un fallo
no inventa asuntos ni altera el ciclo conversacional.

## Integración futura

M389.6 y M389.7 podrán consumir el informe. M390 podrá utilizar asuntos ya
clasificados sin reinterpretar la conversación ni reemplazar esta autoridad.
