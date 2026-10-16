# ROBY XI.2 — GATE 5.A.2.1
## Governed Level-Specific Read-Only Conversational Projection — SURGICAL GREEN

### Baseline de entrada
GATE 5.A.2 Contract Boundary Reconciliation certificado por el usuario sobre:
- M361 sincronizado;
- Ruff limpio;
- 13,987 PASS;
- 0 FAIL.

El CONTRACT RED posterior demostró exactamente los siete residuales semánticos esperados de G5A2-R1/G5A2-R2. El usuario corrigió exclusivamente el E501 del test RED; esa versión corregida se integra como contrato canónico en esta entrega. El desajuste M361 observado durante RED era consecuencia documental del cambio de bytes del test y se resuelve regenerando M361 después de integrar el archivo corregido.

## 1. Alcance productivo
Se modifica quirúrgicamente un único archivo productivo:
- `app/official_conversation_gateway.py`

No se crea módulo, manager, runtime, brain, registry ni autoridad paralela.

## 2. Implementación
`OfficialConversationGateway.analysis_mode_projection(...)` deja de retornar indiscriminadamente el snapshot bruto completo y ahora:
1. conserva el estado efímero por `session_id` de GATE 5.A.1;
2. obtiene una única fuente read-only mediante `UnifiedRuntimeObservability().snapshot(runtime)`;
3. selecciona campos exclusivamente según `status.level`;
4. devuelve un value object subordinado e inmutable `AnalysisModeProjection`;
5. representa ausencias mediante `unavailable` / `not provisioned` sin fabricar evidencia.

### PERSONAL
Selecciona solamente:
- `cognitive_core`;
- `conversation`;
- `self_model` si ya está publicado.

Si `self_model` no existe, se declara `self_model: unavailable`.

### TECHNICAL
Selecciona solamente campos ya presentes en observability:
- `operational`;
- `readiness`;
- `conversation`;
- `registered_capabilities`;
- `capability_registry`;
- `cognitive_core`;
- `self_diagnostics`;
- `capabilities` sólo si ya existe;
- `recovery` sólo si ya viene publicado.

No genera recovery ni ejecuta diagnostics. Ausencias se declaran explícitamente.

### ARCHITECTURAL
Selecciona solamente metadata/estado ya publicado:
- `reflection.architecture`;
- `reflection.published_state` cuando exista;
- `capability_registry`;
- metadata de `self_diagnostics`.

La evidencia arquitectónica productiva no se fabrica: se declara `architectural_evidence: not provisioned`.

## 3. Representación conversacional
Se añade `analysis_mode_conversational_projection(...)`, subordinado al mismo gateway, que transforma únicamente la selección ya gobernada a una forma estable:
- `mode`;
- `level`;
- `available`;
- `sections`;
- `unavailable`.

No expone el `UnifiedRuntimeObservabilitySnapshot` bruto como semántica del nivel.

## 4. Autoridades y STOP preservados
La proyección no llama:
- `.reason(`;
- `.plan(`;
- `.reflect(`;
- `.diagnose(`;
- `.learn(`;
- `.remember(`.

Tampoco ejecuta Ruff, pytest, scans, lectura automática de repositorio ni private/chain-of-thought reasoning.

Permanecen fuera de alcance:
- G5-R3 — inventario técnico completo (episodes, budgets, dependencies, versions, errors, certifications);
- G5-R4 — adquisición productiva de evidencia arquitectónica;
- Memory/Learning automáticos;
- Planning N+1;
- repair/background monitoring/autonomy expansion.

## 5. Compatibilidad arquitectónica
Los value objects nuevos permanecen anidados dentro de `OfficialConversationGateway`, preservando la invariante histórica M395.5 de clases top-level y la autoridad canónica de conversación.

`.roby/config.json` no se modifica. `credencial.json`, si existiera en la baseline, debe preservarse sin cambios.

## 6. Criterio de cierre
El GREEN queda listo para certificación integral local del usuario con:

```text
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

El cierre formal requiere Ruff limpio + 0 FAIL.
