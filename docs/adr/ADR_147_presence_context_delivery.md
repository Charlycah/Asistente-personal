# ADR-147 — Presence Context Delivery

## Estado
Aceptado.

## Contexto
M144 construye planes declarativos de despacho entre publicaciones y suscripciones compatibles. Faltaba una capa que materializara cada destino planificado como un registro de entrega lógico, auditable e inmutable, sin introducir transporte ni ejecución del consumidor.

## Decisión
M145 consume resultados gobernados de M144, selecciona el plan válido más reciente y crea un registro de entrega por destino. Cada registro preserva el destino, la publicación, el tópico, la versión de esquema, la condición completa o parcial y un identificador determinista.

## Límites
M145 no realiza transporte externo, no invoca callbacks, no ejecuta routing, no procesa contexto en nombre del consumidor y no autoriza identidad, actividad, intención, decisiones, adaptación, proveedores, automatización ni mutación de plataforma.

## Consecuencias
La materialización y auditoría de entregas queda separada del transporte y del consumo. Futuras capas podrán confirmar recepción o integrar consumidores reales sin modificar los contratos de publicación, suscripción, despacho o entrega lógica.
