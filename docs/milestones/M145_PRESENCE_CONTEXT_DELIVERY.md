# M145 — Presence Context Delivery

## Responsabilidad única
Materializar cada destino de un plan M144 como un registro lógico, inmutable y auditable de entrega.

## Entradas
- planes de despacho gobernados de M144;
- propietario;
- política de frescura, confianza y límites.

## Salidas
- `DELIVERED` para planes de contexto completo;
- `DELIVERED_PARTIAL` para planes de contexto parcial;
- `REVIEW_REQUIRED`, `BLOCKED` o `NOT_APPLICABLE` cuando corresponde.

## Reglas
- selección determinista del dispatch válido más reciente;
- un registro de entrega por destino planificado;
- preservación exacta del dispatch y sus destinos;
- identificadores deterministas de resultado e ítems;
- control de propietario, frescura, confianza y límites;
- repositorio inmutable mediante protocolo.

## Fuera de alcance
Transporte externo, callbacks, ejecución de routing, procesamiento del consumidor, identidad, actividad, intención, decisiones, adaptación, proveedores, automatización y mutación de plataforma.
