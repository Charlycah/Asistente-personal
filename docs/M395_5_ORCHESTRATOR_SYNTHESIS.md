# M395.5 — Síntesis de Orquestadores y Certificación

## Alcance

M395.5 reduce concentración interna sin crear nuevas autoridades, managers, gateways ni composition roots.

### OfficialConversationGateway

- Conserva una única clase pública `OfficialConversationGateway`.
- Conserva `CanonicalCognitiveCore` en su linaje histórico certificado (línea 52).
- El constructor pasa de 164 líneas a 25 líneas.
- Evidencia cognitiva y servicios conversacionales gobernados se inicializan mediante fases privadas de la misma clase.
- No cambia la API pública ni el orden del turno.

### CognitivePipeline

- Conserva una única clase `CognitivePipeline`.
- `process_turn()` pasa de 325 líneas a 95 líneas.
- La observación previa a memoria queda explícita en `_run_pre_memory_observations()`.
- La construcción del system prompt del turno queda encapsulada en `_build_system_prompt_for_turn()`.
- Se preserva el orden: cognición/observación -> memoria -> prompt -> LLM -> resultado.

### Desktop

No se modifica. La auditoría no justificó introducir riesgo adicional durante la certificación final de M395.

## Invariantes

- Sin segunda autoridad.
- Sin segundo orchestrator.
- Sin nueva capacidad funcional.
- Sin modificación de APIs públicas.
- Linaje canónico del gateway preservado.
- Las fases extraídas son privadas y subordinadas al mismo orquestador.
