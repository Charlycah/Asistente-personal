# M390.7 — Reflexión sobre Estado Interior

M390.7 amplía la autoridad existente `ConversationReflectionAuthority` (M389.2) para observar, de forma opcional y explícita, evidencia ya certificada del mundo interior simulado.

No crea una nueva autoridad de reflexión. La autoridad M389.2 conserva la responsabilidad exclusiva sobre la reflexión conversacional posterior al turno.

## Entradas opcionales

- `SimulatedInnerStateSnapshot` de M390.1.
- `ExplicitInnerContinuityReport` de M390.3.
- `SimulatedFunctionalRegulationReport` de M390.6.

Los informes de continuidad y regulación sólo son considerados cuando también se entrega explícitamente el snapshot interior al que acompañan.

## Salida

`ConversationReflectionReport` conserva su contrato anterior y añade referencias opcionales a la evidencia M390 observada y códigos de observación estructurados. No copia contenido conversacional, no crea memoria, no aprende y no modifica el estado interior.

## Reglas

1. La reflexión observa; no reconstruye ni reinterpreta emociones.
2. Los riesgos interiores se representan como presencia de riesgo, sin convertir códigos internos en nuevos hechos.
3. Sin entrada M390, M389.2 mantiene el comportamiento anterior.
4. No existe persistencia, reloj, background, planificación, permisos ni ejecución.
5. `SimulatedInnerStateAuthority` conserva la autoridad exclusiva del estado interior.
