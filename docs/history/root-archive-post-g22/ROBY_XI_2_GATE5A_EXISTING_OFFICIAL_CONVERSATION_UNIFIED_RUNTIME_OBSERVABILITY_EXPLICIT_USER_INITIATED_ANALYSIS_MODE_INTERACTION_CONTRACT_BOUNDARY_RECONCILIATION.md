# ROBY XI.2 — GATE 5.A
## Existing Official Conversation + UnifiedRuntimeObservability → Explicit User-Initiated Analysis Mode Interaction — CONTRACT BOUNDARY RECONCILIATION

**Tipo:** reconciliación contractual / inventario de frontera.  
**Cambio productivo:** NO.  
**Baseline de entrada certificada por usuario:** 13,975 PASS + Ruff limpio + 0 FAIL.  
**Autoridad arquitectónica:** una autoridad por capacidad; un solo cerebro gobernado.

## 1. Pregunta contractual

¿Dónde puede vivir un Modo Análisis explícito, persistente sólo durante la interacción/sesión, sin crear un segundo cerebro ni convertir una solicitud ordinaria de análisis en un cambio de modo?

**Respuesta:** la frontera canónica es la conversación oficial existente. `OfficialConversationGateway` ya es la entrada única de los turnos interactivos y ya resuelve `session_id`. El Modo Análisis debe ser un **estado subordinado de interacción por sesión**, consultado desde esa frontera y alimentado por `UnifiedRuntimeObservability`; no es una nueva autoridad cognitiva.

No se justifica `AnalysisModeManager`, `AnalysisBrain`, `IntrospectionManager`, otro runtime cognitivo ni otro registro.

## 2. Autoridades reales reconciliadas

### 2.1 OfficialConversationGateway

`app/official_conversation_gateway.py::OfficialConversationGateway`

- Es la frontera única gobernada para cada turno interactivo.
- `submit(...)` acepta `session_id`.
- `_effective_session_id(...)` resuelve la sesión efectiva.
- `snapshot` publica actividad conversacional básica.
- Ya coordina las autoridades cognitivas existentes; no debe ser reemplazado.

**Dictamen:** `CANONICAL INTERACTION ENTRY / SUITABLE OWNER OF SUBORDINATE SESSION INTERACTION STATE`.

### 2.2 RuntimeSessionProfile

`core.personal_identity_and_session_profiles.models.RuntimeSessionProfile`

- Modela identidad/lifecycle de sesión: `session_id`, `profile_id`, status y tiempos.
- No modela modos conversacionales o cognitivos.

**Dictamen:** NO sobrecargarlo con Modo Análisis. El modo es estado efímero de interacción, no identidad de sesión ni perfil personal.

### 2.3 Existing guided analysis

`cognitive.guided_analysis` ya está registrado en `OfficialRuntimeCapabilityRegistry` y `CognitivePlanner.assess_cognitive_needs(...)` ya detecta verbos como analizar/razonar/evaluar/comparar.

**Dictamen:** una petición como `analizá X` continúa siendo una solicitud cognitiva ordinaria. **No activa Modo Análisis.**

### 2.4 UnifiedRuntimeObservability

`app/unified_runtime_observability.py::UnifiedRuntimeObservability`

Es la proyección read-only certificada para:

- runtime/readiness;
- conversación;
- capability registry;
- cognitive core;
- Self Model publicado;
- Reflection estructural/publicada;
- Self Diagnostics honesto sin fabricar reporte.

**Dictamen:** fuente canónica de datos introspectivos para el Modo Análisis. No debe ejecutar capacidades para completar una vista.

## 3. Semántica contractual del Modo Análisis

### 3.1 Estado mínimo

El estado mínimo futuro debe ser por `session_id` y contener solamente:

- `active: bool`;
- `level: PERSONAL | TECHNICAL | ARCHITECTURAL` cuando está activo.

No necesita persistencia durable, Memory ni Learning. Debe desaparecer con el lifecycle de la interacción/sesión o mediante salida explícita.

### 3.2 Activación explícita

La entrada requiere una orden inequívoca de cambio de modo, por ejemplo semánticamente:

- `entrar en modo análisis`;
- `activar modo análisis`;
- `modo análisis técnico`;
- `entrar en modo análisis arquitectónico`.

Una solicitud que sólo contiene `analizá`, `razoná`, `evaluá` o `compará` **no cambia el estado del modo** y sigue por `cognitive.guided_analysis`/autoridades cognitivas existentes.

### 3.3 Salida explícita

Debe existir una orden inequívoca de salida, semánticamente equivalente a:

- `salir del modo análisis`;
- `desactivar modo análisis`;
- `volver al modo normal` cuando el Modo Análisis está activo.

La salida no borra Memory, no altera Self Model y no ejecuta ninguna capacidad.

### 3.4 Consulta de estado

Debe poder consultarse explícitamente si el modo está activo y su nivel. La consulta es read-only.

## 4. Niveles

Los niveles son **proyecciones/presentaciones**, no autoridades.

### PERSONAL

Puede proyectar sólo estado personal/cognitivo ya publicado y seguro desde observability, por ejemplo estado general del cognitive core y Self Model publicado. No revela razonamiento privado, no inventa emociones/conciencia y no consulta Memory automáticamente.

### TECHNICAL

Puede proyectar runtime/readiness, capability registry, presencia/health del cognitive core, conversación y disponibilidad explícita de diagnósticos. No ejecuta capabilities, recovery, diagnostics ni scanners para llenar huecos.

### ARCHITECTURAL

Puede proyectar la arquitectura **ya publicada/certificada** disponible en observability y metadata canónica (por ejemplo Reflection authority). No equivale a una auditoría viva del repositorio. Si no existe evidencia actual de código/docs/tests para una afirmación arquitectónica, debe declarar `unavailable/not provisioned` en lugar de fabricar un diagnóstico.

## 5. Frontera de evidencia arquitectónica

El Modo Análisis no autoriza:

- escanear el repositorio automáticamente;
- ejecutar `GovernedSelfDiagnostics.diagnose()`;
- correr Ruff/pytest;
- leer archivos privados o documentación por iniciativa propia;
- generar un nuevo diagnóstico técnico para completar la pantalla/respuesta.

Una futura auditoría arquitectónica productiva requerirá una solicitud explícita y una costura contractual separada hacia evidencia real. No es residual de esta interacción.

## 6. Residuales demostrados para implementación

### G5A-R1 — Session interaction state seam absent

`OfficialConversationGateway` resuelve sesión pero no publica/almacena todavía `analysis_mode active + level` por sesión.

### G5A-R2 — Explicit command classifier absent

No existe aún contrato productivo que distinga cambio de modo de una solicitud ordinaria `analizá X`.

### G5A-R3 — Level projection adapter absent

No existe aún proyección conversacional Personal/Technical/Architectural sobre `UnifiedRuntimeObservability`.

### G5A-R4 — Analysis-mode status exposure absent

El snapshot conversacional oficial no expone todavía estado del modo para consulta/observabilidad.

Estos son **residuales de costura**, no capacidades cognitivas faltantes.

## 7. Costura canónica mínima recomendada

```text
OfficialConversationGateway.submit(... session_id ...)
        |
        +-- explicit analysis-mode command recognition
        |       |
        |       +-- enter / set level / status / exit
        |       +-- session-scoped subordinate interaction state
        |
        +-- ordinary "analizá X"
                |
                +-- existing cognitive.guided_analysis / cognitive authorities

Analysis-mode read-only view
        |
        +-- existing OfficialRuntime.observability(...)
                |
                +-- UnifiedRuntimeObservability
```

La implementación debe reutilizar la conversación oficial y observability. Si se necesita un pequeño value object/helper de estado, será subordinado y no tendrá autoridad cognitiva, ejecución ni persistencia durable.

## 8. Invariantes recomendados para GATE 5.A.1 CONTRACT RED

1. `OfficialConversationGateway` permanece la única entrada interactiva oficial.
2. El estado de Modo Análisis está aislado por `session_id`.
3. Estado mínimo: inactive/active + nivel Personal/Technical/Architectural.
4. Entrada sólo por comando explícito de modo.
5. `analizá X` no activa el modo.
6. Salida explícita desactiva sólo la sesión actual.
7. Consulta de estado no ejecuta capacidades.
8. Las vistas del modo consumen `UnifiedRuntimeObservability` existente.
9. Personal no consulta Memory/Learning automáticamente.
10. Technical no ejecuta capability/recovery/diagnostics.
11. Architectural no escanea código/docs/tests ni llama `diagnose()` automáticamente.
12. Datos ausentes se representan como unavailable/not provisioned; no se inventan.
13. No `AnalysisModeManager`, `AnalysisBrain`, `IntrospectionManager` ni segundo runtime/registry.
14. No Planning N+1, Memory/Learning writes, repair, code modification o background monitoring.
15. No chain-of-thought/private reasoning exposure.
16. `.roby/config.json` permanece byte-identical.
17. `credencial.json`, si existe, se preserva.

## 9. Exclusiones de GATE 5.A.1

- persistencia durable del modo;
- preferencias aprendidas del nivel;
- activación automática por heurística;
- auto-escalado Personal→Technical→Architectural;
- ejecución de diagnostics/tests/scanners;
- reparación o modificación de código;
- nuevo motor de reasoning/planning/reflection;
- Memory/Learning;
- autonomía ampliada.

## 10. Clasificación

`EXISTING OFFICIAL CONVERSATION + CERTIFIED UNIFIED OBSERVABILITY + MINIMAL SESSION-SCOPED INTERACTION/LEVEL PROJECTION SEAM REQUIRED`

## 11. STOP y próximo gate

**STOP:** esta reconciliación no implementa Modo Análisis.

Próximo paso permitido:

`GATE 5.A.1 — Official Conversation Session-Scoped Explicit Analysis Mode Interaction + Existing UnifiedRuntimeObservability Projection — CONTRACT RED`

Sólo después de certificar ese RED podrá existir un SURGICAL GREEN.
