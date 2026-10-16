# ROBY XI.2 — GATE 5.A.1
## Official Conversation Session-Scoped Explicit Analysis Mode Interaction + Existing UnifiedRuntimeObservability Projection — CONTRACT RED

**Tipo:** contrato RED.  
**Cambio productivo:** NO.  
**Baseline de entrada certificada:** 13,975 PASS + Ruff limpio + 0 FAIL.  
**Predecesor:** GATE 5.A — CONTRACT BOUNDARY RECONCILIATION — CERTIFIED / CLOSED.

## Objetivo

Congelar contractualmente la costura mínima ya demostrada por GATE 5.A, antes de tocar producción.

El contrato exige que `OfficialConversationGateway` continúe siendo la frontera interactiva oficial y que el futuro Modo Análisis sea solamente estado subordinado, efímero y aislado por `session_id`, alimentado por el `UnifiedRuntimeObservability` existente.

## Invariantes RED

1. El snapshot conversacional oficial debe poder exponer el estado del Modo Análisis.
2. Debe existir consulta read-only por sesión.
3. Debe existir reconocimiento explícito de comandos de modo.
4. `entrar/activar modo análisis`, selección de nivel, consulta y salida son comandos de modo.
5. `analizá X`, `compará X/Y`, `razoná X` no activan ni cambian el modo.
6. El estado debe estar aislado por `session_id`, nunca global.
7. Los únicos niveles contractuales son `PERSONAL`, `TECHNICAL`, `ARCHITECTURAL`.
8. La proyección debe reutilizar `UnifiedRuntimeObservability`; no crear otra introspección.
9. No se crean `AnalysisModeManager`, `AnalysisBrain`, `IntrospectionManager`, otro runtime o registry.
10. Consulta/proyección no ejecuta reasoning, planning, reflection ni diagnostics.
11. Architectural no ejecuta Ruff/pytest/scanners ni fabrica evidencia.
12. Datos ausentes deben permanecer ausentes/unavailable/not provisioned.
13. No Memory/Learning writes, Planning N+1, repair, background monitoring o autonomía adicional.
14. No chain-of-thought/private reasoning.
15. `.roby/config.json` permanece byte-identical.
16. `credencial.json`, si existe, se preserva.

## Semántica mínima congelada

```text
session_id A -> inactive | active(PERSONAL|TECHNICAL|ARCHITECTURAL)
session_id B -> estado independiente

"entrar en modo análisis"      -> comando de modo
"modo análisis técnico"        -> comando de modo + TECHNICAL
"salir del modo análisis"      -> comando de modo
"¿está activo el modo análisis?" -> consulta read-only
"analizá este problema"        -> NO es comando de modo
```

## RED esperado

El baseline de GATE 5.A todavía no posee la costura productiva. Por eso el test contractual debe fallar exclusivamente por los residuales G5A-R1..R4 ya inventariados, mientras los invariantes históricos permanecen verdes.

Archivo contractual:

`tests/architecture/test_gate5a1_official_conversation_session_scoped_analysis_mode_contract_red.py`

## STOP

Este gate NO implementa el Modo Análisis. No se modifica producción. No se abre GREEN hasta certificación local del RED esperado.

Siguiente paso permitido sólo tras certificar RED:

`GATE 5.A.1 — ... — SURGICAL GREEN`
