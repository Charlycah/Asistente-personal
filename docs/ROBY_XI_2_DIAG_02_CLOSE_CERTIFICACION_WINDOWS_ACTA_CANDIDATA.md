# ROBY XI.2 — DIAG-02-CLOSE — Acta candidata de reconciliación de certificación Windows

**Naturaleza:** acta documental complementaria, no modificación productiva ni promoción integral.  
**Baseline documental inspeccionado:** `ROBY_XI_2_DIAG_02_CLOSE_RECONCILIADO_CANDIDATO.zip`.  
**Evidencia de ejecución:** salidas PowerShell proporcionadas por el Owner desde `C:\Users\CAHCA\Desktop\HAL` el 12-10-2026.  
**Estado:** reconciliación documental candidata, pendiente de integración gobernada y comprobación final.

## 1. Precedencia y alcance

Se mantienen `architecture_rules.md`, `ROBY_XI_2_CURRENT_TRUTH.md`, `ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md`, inventarios y contratos canónicos. Una autoridad por capacidad; sin nuevas autoridades, módulos, RED, GREEN ni modificación de código. `app/runtime_ui_adapter.py` permanece protegido. M377 HOLD; MODEL_ACQUISITION UNMAPPED / DENY / NO-GO.

El acta DIAG-02 original (`docs/ROBY_XI_2_R_COGNITIVE_INTEGRATION_EVAL_DIAG_02_CLOSE.md`) continúa siendo la fuente del dictamen cognitivo V1–V4. Este documento registra exclusivamente evidencia posterior de certificación local.

## 2. Evidencia Windows comunicada por el Owner

| Verificación | Resultado observado | Límite |
|---|---|---|
| Ruta de ejecución | `C:\Users\CAHCA\Desktop\HAL` | Identifica carpeta local, no hash del ZIP desplegado |
| Líneas de `ROBY_XI_2_CURRENT_TRUTH.md` | 400 | Control de estructura |
| Markdown en raíz | 12 | Control de estructura |
| Cinco módulos de contratos documentales | 40 PASS | Alcance dirigido |
| M225 aislado | 3 PASS | Alcance dirigido |
| M224 aislado | 7 PASS | Alcance dirigido |
| M224 + M225 | 10 PASS | Alcance dirigido |
| Suite integral, primer recorrido reconciliado | 13.723 PASS / 48 FAIL | 47 M377 y 1 M224 |
| Suite integral, recorrido posterior | 13.724 PASS / 47 FAIL | 47 M377; sin fallo ajeno a M377 |
| `pytest -k "not m377"` | **13.680 PASS / 91 DESELECTED**, 249,83 s | Certificación local de selección no-M377; no cubre 91 pruebas deseleccionadas |
| Ruff sobre este candidato desplegado | No aportado en esta secuencia | No declarar Ruff PASS para esta versión sin salida específica |

La exclusión previa `--ignore-glob="test_m377_*"` **no** eliminó los contratos M377, por lo que su resultado no constituye la certificación no-M377. El filtro `-k "not m377"` sí dejó 91 pruebas deseleccionadas. Los 47 fallos M377 de la suite integral son RED contractuales conocidos; 91 deseleccionadas no equivale a 91 fallos.

## 3. Anomalía M224 y alcance de conclusión

El test `test_second_turn_reconstructs_context_from_journal` falló una vez en suite integral con `IndexError: list index out of range`. Pasó posteriormente en el módulo aislado, en combinación con M225, en la suite integral posterior y en la selección no-M377. No se demostró causa raíz, ni se acredita una corrección productiva. Se conserva como **observación histórica de intermitencia**, sin autorizar intervención.

## 4. Dictamen de certificación

**PASS LOCAL — SELECCIÓN NO-M377:** 13.680 pruebas aprobadas, 0 fallidas, 91 deseleccionadas.

**NO GREEN INTEGRAL:** la suite integral conserva 47 RED M377 deliberadamente pendientes. No se levanta HOLD ni se promociona una capacidad por esta acta.

**DIAG-02 SIN CAMBIO SEMÁNTICO:** V1–V3 COVERED acotado; V4 negativo COVERED; V4 positivo M326 DESIGN_LIMIT provisional / INCONCLUSIVE; M359 independiente; GAP_DEMONSTRATED ninguno.

**RUFF Y TRAZABILIDAD:** no inferir Ruff PASS actual de salidas anteriores; antes de promover documentalmente un nuevo ZIP, verificar `ruff check .`, baseline de calidad y correspondencia de archivos/hashes del despliegue Windows.

## 5. STOP y próximos controles documentales

1. Conservar este acta como complemento sin sustituir el acta DIAG-02 ni reescribir el estado histórico.
2. Contrastar el punto de integración con inventarios, registros, master state y límites de 400 líneas / 12 Markdown raíz.
3. Si se integra al repositorio, ubicarla bajo `docs/`, revisar contratos documentales, verificar Ruff y pruebas dirigidas. No alterar código productivo.
4. Mantener M377 HOLD, MODEL_ACQUISITION NO-GO y STOP antes de nuevos RED/GREEN o promoción integral.

**No se genera ZIP completo en esta etapa:** se evita transferir nuevamente ~102 MB sin necesidad contractual.
