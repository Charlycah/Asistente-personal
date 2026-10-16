# ROBY XI.2 — GATE 5.A.2.1
## Governed Level-Specific Read-Only Conversational Projection — CONTRACT RED

### Baseline de entrada certificada
- GATE 5.A.2 Contract Boundary Reconciliation: certificado y cerrado.
- M361 sincronizado.
- Ruff limpio.
- pytest: 13,987 PASS.
- 0 FAIL.

## Propósito
Congelar contractualmente el residual real G5A2-R1 / G5A2-R2 antes de modificar producción.

No se añade inteligencia, autoridad, persistencia, memoria, aprendizaje, diagnóstico ni adquisición de evidencia. El RED exige únicamente que el Analysis Mode ya existente deje de devolver indiscriminadamente el mismo snapshot bruto y proyecte de forma read-only según el nivel activo de la sesión.

## Autoridades preservadas
- `OfficialConversationGateway`: única frontera interactiva oficial.
- `UnifiedRuntimeObservability`: única fuente read-only unificada.
- `OfficialRuntimeCapabilityRegistry`: autoridad existente de capacidades.
- `CognitiveSelfModel`: sólo estado ya publicado.
- `CanonicalReflectionFacade`: sólo metadata estructural y estado ya publicado.
- `GovernedSelfDiagnostics`: autoridad existente, nunca ejecutada para poblar Analysis Mode.

## Contrato RED
El contrato exige:
1. La proyección depende materialmente de `status.level`.
2. Existe una representación conversacional estable y subordinada; no un passthrough bruto del snapshot unificado.
3. Los únicos niveles son PERSONAL, TECHNICAL y ARCHITECTURAL.
4. PERSONAL selecciona únicamente cognitive/self-model/conversation ya publicados.
5. TECHNICAL selecciona únicamente operational/readiness/conversation/capabilities/registry/cognitive/self-diagnostics y recovery sólo si ya está publicado.
6. ARCHITECTURAL selecciona únicamente reflection architecture/published state, registry y metadata de self-diagnostics ya publicada.
7. Ausencia de información se representa explícitamente como `unavailable` / `not provisioned` o equivalente estable.
8. La proyección no llama Reasoning, Planning, Reflection productiva, Diagnostics, Learning ni Memory.
9. No ejecuta Ruff, pytest, scans ni lectura automática del repositorio.
10. No expone chain-of-thought/private reasoning.
11. No crea manager/runtime/brain/registry/authority paralelo.
12. `analizá X` continúa siendo una petición cognitiva ordinaria y no activa Analysis Mode.
13. El estado sigue aislado por `session_id`.
14. `.roby/config.json` permanece byte-identical.
15. `credencial.json`, si existe, debe preservarse.

## RED esperado
Sobre la baseline certificada, deben fallar exclusivamente las aserciones que representan las costuras todavía ausentes:
- uso efectivo de `status.level`;
- representación conversacional específica;
- selección PERSONAL;
- selección TECHNICAL;
- selección ARCHITECTURAL;
- representación explícita de indisponibilidad.

Los STOP y autoridades históricas deben permanecer verdes.

## STOP
Este gate termina en CONTRACT RED.

No modificar producción. No implementar GREEN. No abrir G5-R3 Technical Inventory ni G5-R4 Architectural Evidence Acquisition. La siguiente transición sólo se autoriza después de que el usuario certifique localmente que el RED falla exactamente por las costuras esperadas y que Ruff permanece limpio.
