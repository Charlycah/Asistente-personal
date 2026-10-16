# M144 — Presence Context Dispatch

## Responsabilidad única
Resolver publicaciones M142 contra suscripciones M143 y construir un plan declarativo de destinos compatibles.

## Entradas
- publicaciones canónicas de M142;
- suscripciones declarativas de M143;
- propietario y política de frescura, confianza y límites.

## Salidas
- `PLANNED` para contexto completo;
- `PLANNED_PARTIAL` para contexto parcial permitido;
- `EMPTY` cuando no existen destinos compatibles;
- `REVIEW_REQUIRED`, `BLOCKED` o `NOT_APPLICABLE` cuando corresponde.

## Reglas
- selección determinista de la publicación válida más reciente;
- sólo suscripciones activas, elegibles, frescas y confiables;
- compatibilidad por tópico, versión de esquema y filtro parcial;
- deduplicación por suscripción y suscriptor;
- preservación exacta de publicaciones y suscripciones fuente.

## Fuera de alcance
Entrega, callbacks, ejecución de routing, procesamiento de consumidores, identidad, actividad, intención, decisión, adaptación, proveedores, automatización y mutación de plataforma.
