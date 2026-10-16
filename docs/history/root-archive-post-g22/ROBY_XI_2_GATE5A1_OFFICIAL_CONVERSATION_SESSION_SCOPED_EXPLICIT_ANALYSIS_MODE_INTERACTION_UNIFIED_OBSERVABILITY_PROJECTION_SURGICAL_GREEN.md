# ROBY XI.2 — GATE 5.A.1
## Official Conversation Session-Scoped Explicit Analysis Mode Interaction + Existing UnifiedRuntimeObservability Projection — SURGICAL GREEN

**Tipo:** SURGICAL GREEN.  
**Baseline RED certificada por usuario:** 13,979 PASS + Ruff limpio + exactamente 8 RED FAIL esperados + 0 fallos externos.  
**Autoridad preservada:** `OfficialConversationGateway`.

## Objetivo

Cerrar exclusivamente los residuales contractuales G5A-R1..R4 sin crear una autoridad cognitiva paralela.

## Cambio productivo mínimo

Se modifica únicamente `app/official_conversation_gateway.py`.

1. `OfficialConversationGatewaySnapshot` incorpora `analysis_mode`.
2. Se incorpora estado efímero `_analysis_mode_by_session`, aislado por `session_id`.
3. Se incorporan value objects subordinados `AnalysisModeLevel`, `AnalysisModeStatus` y `AnalysisModeCommand`.
4. `analysis_mode_command(...)` reconoce únicamente órdenes explícitas de entrada, nivel, estado y salida.
5. `analizá X` / `compará X/Y` no son comandos de modo.
6. `analysis_mode_status(...)` consulta estado sin ejecutar reasoning/planning/reflection/diagnostics.
7. `apply_analysis_mode_command(...)` muta sólo el estado efímero de interacción de la sesión.
8. `analysis_mode_projection(...)` reutiliza `UnifiedRuntimeObservability` existente y sólo proyecta cuando la sesión está activa.
9. `submit(...)` aplica exclusivamente comandos explícitos de modo después de resolver el `session_id`; el flujo cognitivo ordinario permanece bajo las autoridades existentes.

## Preservación arquitectónica

No se crea `AnalysisModeManager`, `AnalysisBrain`, `IntrospectionManager`, `AnalysisRuntime`, segundo registry, segundo cognitive core ni nueva autoridad de reasoning/planning/reflection.

El Modo Análisis no persiste en Memory/Learning, no llama `diagnose()`, no expone chain-of-thought/private reasoning, no ejecuta Ruff/pytest/scanners, no repara código y no abre Planning N+1.

`UnifiedRuntimeObservability` permanece la autoridad read-only de proyección introspectiva.

## Integración del RED corregido por usuario

Se integra como versión canónica el test corregido por el usuario:

`tests/architecture/test_gate5a1_official_conversation_session_scoped_analysis_mode_contract_red.py`

La corrección elimina el import no utilizado y resuelve los `E501` sin cambiar las invariantes del contrato.

## Validación focal del GREEN

El contrato GATE 5.A.1 pasa completo y las pruebas históricas focales de observability/unificación permanecen verdes.

La certificación integral final corresponde al entorno local del usuario mediante:

```text
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

## STOP

Permanece STOP sobre persistencia durable del modo, preferencias aprendidas, activación heurística/automática, auto-escalado de nivel, diagnósticos o scans automáticos, Memory/Learning, Planning N+1, reparación, background monitoring, ampliación de autonomía y exposición de razonamiento privado.
