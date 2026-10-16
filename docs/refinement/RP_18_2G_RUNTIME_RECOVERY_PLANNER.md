# RP.18.2G — Runtime Recovery Planner

## Propósito

Introducir una autoridad puramente declarativa que transforme el snapshot operativo,
el grafo de capacidades y el readiness en un plan de recuperación determinista.

## Responsabilidades

- Detectar qué capacidades solicitadas están degradadas o indisponibles.
- Incluir sus dependencias transitivas.
- Proponer restauración de lifecycle y supervisor antes que residentes.
- Ordenar residentes registrados por `startup_order`.
- Diferenciar residentes recuperables de residentes todavía no registrados.
- Explicar qué capacidades restauraría cada paso.

## Límites

El planner no ejecuta acciones, no muta el lifecycle, no reinicia residentes, no registra
componentes y no constituye todavía autorregulación autónoma.

## Posición en la consolidación

Cierra el soporte de diagnóstico y planificación derivado del snapshot operativo. La
continuación principal debe volver al roadmap rector con la integración del núcleo
RP.10–RP.18 en la raíz oficial de ejecución.
