# ROBY XI.2 — R-RIQ-S2-H2-AUTHORIZATION-EVIDENCE-RECONCILIATION
## Existing Access Policy & Research Admission Evidence (Static)

**Estado:** ACTA CANDIDATA — aprobación del Owner pendiente  
**Naturaleza:** investigación documental y lectura estática de `ultima version corregida(9).zip`  
**Control:** `STOP_PRODUCTIVE: ACTIVE`; sin ejecución de ROBY, pruebas, instrumentación o modificaciones productivas.

## 1. Propósito y frontera
Contrastar autoridades existentes de permisos y consentimiento con los requisitos de admisión de una observación científica H2. La aprobación de esta investigación documental no es consentimiento operativo para extraer conversaciones ni para ejecutar experimentos. Se preservan las certificaciones previas, en especial la frontera Desktop de diagnóstico sin contenido conversacional.

## 2. Fuentes estáticas examinadas
- `core/permission_consent.py` — política, concesiones, decisiones y motor M63.
- `core/unified_permission_consent/models.py` y `engine.py` — contratos M158, concesiones ligadas a propietario/contexto y evaluación.
- `core/development_console_observability/observer.py` — observación del runtime y de turnos.
- `core/development_console_observability/renderer.py` — proyección de datos con `reveal_prompt=False` predeterminado.
- Antecedentes R-RIQ-S2-H2: READ-CALLER-TRACE, OBSERVER-BOUNDARY-ASSESSMENT y OBSERVER-CONSUMER-GATE-TRACE (documentación incorporada localmente por el Owner; no se presupone que esté incluida en el ZIP base).

## 3. Evidencia comprobada
### M63 — `core/permission_consent.py`
`PermissionConsentPolicy` distingue ámbitos y permite ciertas lecturas de bajo riesgo sin consentimiento según política. `PermissionGrant` identifica capacidad, ámbito, otorgante, motivo, instante e ID. `ConsentDecision` expresa `ALLOWED`, `REQUIRES_CONSENT` o `DENIED`, y `PermissionConsentEngine.evaluate_capability()` evalúa una capacidad solicitada.

**Límite:** la existencia de un ámbito READ o de una regla genérica para lecturas de bajo riesgo no clasifica automáticamente la lectura de prompts, respuestas o mensajes conversacionales como de bajo riesgo, ni prueba que el observador invoque M63 por consulta.

### M158 — `core/unified_permission_consent/models.py` y `engine.py`
`UnifiedConsentGrant` incluye `owner`, capacidad, ámbito, contextos y datos temporales. El motor comprueba correspondencia del propietario y requisitos contextuales. El modelo `UnifiedPermissionConsentResult` prohíbe explícitamente que M158 autorice capacidades downstream (`M158 cannot authorize downstream capabilities`).

**Límite:** un resultado de consentimiento M158 no es un permiso autónomo para abrir una nueva superficie de observación H2 ni una autorización de respuesta, ejecución o exposición de contenido.

### Observador y renderer
`DevelopmentConsoleObserver` expone observaciones del runtime y turnos y consulta el repositorio del pipeline por `pipeline_result_id`. `DevelopmentConsoleRenderer.render_turn(..., reveal_prompt=False)` omite el contenido de prompt/mensajes en la salida ordinaria; si se habilita `reveal_prompt`, puede representarlo. La ocultación de presentación no es un control de autorización de acceso a los objetos subyacentes.

**Límite:** en las superficies inspeccionadas no se acreditó una cadena completa `identidad de solicitante → decisión autorizante aplicable → consulta → filtrado de contenido → evidencia auditable` para investigación H2. Esto no demuestra que tal cadena sea inexistente en todo ROBY ni que haya una vulnerabilidad.

## 4. Matriz de admisión científica
| Requisito | Estado | Evidencia o condición pendiente |
|---|---|---|
| Motor de permisos por capacidad/ámbito | `CONFIRMED_STATICALLY` | M63 |
| Modelo de concesión con propietario y contexto | `CONFIRMED_STATICALLY` | M158 |
| Autorización downstream derivada de M158 | `FORBIDDEN_BY_CONTRACT` | Prohibición explícita del modelo |
| Consulta interna del observador | `CONFIRMED_STATICALLY` | `DevelopmentConsoleObserver` |
| Filtrado predeterminado en renderer | `CONFIRMED_STATICALLY` | `reveal_prompt=False` |
| Comprobación de permiso H2 por cada consulta del observador | `NOT_DEMONSTRATED` | No identificada en la ruta observada |
| Clasificación de sensibilidad de respuestas/prompts H2 | `NOT_DEMONSTRATED` | No inferir bajo riesgo por ser READ |
| Consentimiento específico para lectura científica de contenido | `NOT_DEMONSTRATED` | No consta concesión aplicable |
| Aislamiento de propietario/sesión en acceso investigador | `NOT_DEMONSTRATED` | Identificadores no bastan |
| Vía autorizada de extracción histórica | `NOT_DEMONSTRATED` | Persistencia/acceso no acreditados |
| Vínculo evaluación H2–respuesta final | `NOT_DEMONSTRATED` | Correlación causal pendiente |
| Ejecución C0/C1 | `EXPERIMENT_NOT_ENABLED` | No admitida |

## 5. Regla de no inferencia
Ni la aprobación del Owner para elaborar estas actas, ni una concesión genérica de lectura, ni el uso de un renderer que oculta prompts autorizan automáticamente la extracción de contenido conversacional. No utilizar Desktop para sortear su frontera `metadata-only`; no reactivar consola histórica; no ejecutar harness diagnóstico para fingir observación pasiva; no crear autoridades paralelas.

## 6. Dictamen
**`POLICY_AUTHORITIES_EXIST / H2_RESEARCH_ADMISSION_NOT_DEMONSTRATED / NOT_EXECUTION_READY`.**

Se ha demostrado la existencia de autoridades de permisos y consentimiento, pero no su aplicación completa a la ruta de consulta científica H2. La ausencia de demostración no equivale a ausencia global ni a vulnerabilidad. No hay base para habilitar extracción, observación de contenido o experimentos C0/C1.

## 7. Próxima decisión sugerida (no iniciada)
`R-RIQ-S2-H2-RESEARCH-ADMISSION-GAP-CLOSURE — Evidence Sufficiency & STOP Decision (Documentary)` para consolidar exactamente qué evidencia falta y decidir si cerrar H2 en `INSUFFICIENT_EVIDENCE` o si existe una ruta documental adicional justificada. No abrir código ni repetir auditorías.

## 8. Gobierno
- `DOCUMENT_PREPARED / OWNER_APPROVAL_PENDING`
- `PRODUCTIVE_CHANGES: NONE`
- `TESTS_EXECUTED: NONE`
- `C0/C1: EXPERIMENT_NOT_ENABLED`
- `STOP_PRODUCTIVE: ACTIVE`
