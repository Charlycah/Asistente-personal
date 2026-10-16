# ADR-146 — Presence Context Dispatch

## Estado
Aceptado.

## Contexto
M142 publica contexto de presencia canónico y M143 registra contratos declarativos de suscripción. Faltaba una capa que resolviera compatibilidad entre ambos sin realizar entrega ni ejecutar consumidores.

## Decisión
M144 construye planes inmutables de despacho a partir de publicaciones M142 y suscripciones M143 gobernadas. Selecciona la publicación válida más reciente, filtra suscripciones activas por tópico, versión de esquema y aceptación de contexto parcial, deduplica destinos y produce un plan determinista.

## Límites
M144 no publica contexto, no registra suscripciones, no entrega mensajes, no invoca callbacks, no ejecuta routing, no procesa contexto y no autoriza inferencia, decisión, adaptación, automatización ni mutación de plataforma.

## Consecuencias
La selección de destinos queda desacoplada del transporte y de los consumidores. Una futura capa podrá ejecutar planes explícitos sin modificar los contratos de publicación, suscripción o despacho.
