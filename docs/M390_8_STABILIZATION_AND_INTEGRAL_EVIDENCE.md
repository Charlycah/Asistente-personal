# M390.8 — Estabilización y Evidencia Integral

M390.8 cierra la serie M390 sin añadir una nueva capacidad conductual ni una
nueva autoridad. Incorpora un diagnóstico de evidencia integral, inmutable y de
solo lectura, destinado a verificar la coherencia explícita de la cadena ya
certificada del mundo interior simulado.

## Cadena auditada

1. `SimulatedInnerStateSnapshot` (M390.1).
2. `ExplicitInnerContinuityReport` (M390.3).
3. `SimulatedFunctionalRegulationReport` (M390.6).
4. `ConversationReflectionReport` reutilizado por M390.7.
5. `AdaptivePersonalityRequest` modulado por M390.5.

`M390IntegralEvidenceDiagnostic` no posee `authority_id`, no construye estado
interior, no modifica personalidad, no persiste, no aprende, no planifica y no
ejecuta. Sólo informa evidencia presente, piezas ausentes y conflictos de
linaje explícito.

## Invariantes de cierre

- `SimulatedInnerStateAuthority` continúa como única autoridad del estado
  interior simulado.
- `ConversationReflectionAuthority` continúa como única autoridad reflexiva
  utilizada por M390.
- `AdaptivePersonalityAuthority` continúa como única autoridad expresiva.
- Los evaluadores M390.2–M390.6 y el diagnóstico M390.8 permanecen
  subordinados y sin `authority_id`.
- No se incorpora runtime, persistencia, reloj, memoria, aprendizaje,
  planificación, permisos, objetivos ni ejecución.
- `.roby/credentials.json` permanece fuera de alcance y fuera del ZIP.
