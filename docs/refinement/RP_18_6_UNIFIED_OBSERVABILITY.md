# RP.18.6 — Observabilidad unificada

ROBY expone una sola superficie de diagnóstico mediante
`OfficialROBYRuntime.observability()`.

La vista se construye en el momento de la consulta a partir de estados canónicos ya
existentes. No posee lifecycle, no inicia hilos y no mantiene contadores paralelos.

Integra:

- snapshot operativo y residentes;
- health y readiness;
- gateway conversacional;
- gateway y registro de capacidades;
- núcleo cognitivo residente, cuando está presente;
- plan de recuperación, cuando se proporciona un grafo.

El resultado es inmutable y serializable mediante `as_dict()`.
