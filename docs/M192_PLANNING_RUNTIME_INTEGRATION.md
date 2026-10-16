# M192 — Planning Runtime Integration

M192 conecta la planificación ejecutiva existente de M90 con el runtime cognitivo
operacional de M189.

## Alcance

- Añade `PlanningRuntimeContributor` como proyección de solo contexto.
- Consume planes ejecutivos mediante `ExecutivePlanningSource`.
- Publica únicamente planes `approved` o `active`.
- Preserva objetivos, criterios, hitos, restricciones y linaje.
- Mantiene la planificación después del razonamiento y antes de contribuyentes
  cognitivos adicionales.

## Frontera de gobernanza

La integración no activa planes, no cambia estados, no ejecuta hitos, no llama
herramientas y no realiza mutaciones. Los planes en borrador, revisión, pausa,
completados o cancelados quedan registrados como omitidos.

## Orden operacional

1. conversación viva;
2. razonamiento gobernado;
3. planificación ejecutiva;
4. contribuyentes cognitivos adicionales;
5. herramientas;
6. proveedor local.
