# P5Y03-IMP-SCOPE-03 — Revisión de autorización y checkpoints Git

**ROBY XI.2 · R01-P5Y-03 · DOCUMENTARY / PROPOSED**
**Base Git reportada:** `master` / `754012c` · **Fecha:** 2026-10-29

> La autorización del usuario se limita a crear dos documentos nuevos. No habilita modificaciones del Plan Maestro, GUI-06 u otros archivos; tampoco pruebas, staging, commit o push. M377 HOLD; STOP_PRODUCTIVE ACTIVE; MODEL_ACQUISITION UNMAPPED / DENY / NO-GO; RED DENY; GREEN DENY; GUI-06 PROTECTED; R01-P5Y-03 OPEN — DOCUMENTARY; ONE BRAIN — ONE AUTHORITY PER CAPABILITY.

## 1. Dictamen y alcance

**PROPOSED — DOCUMENTARY.** Los archivos visuales rastreados y sin modificaciones visibles en el `git status` aportado fueron `app/desktop_governed_floating_image_viewer.py`, `app/desktop_governed_image_preview_coordinator.py`, `app/external_image_presentation.py` y `app/governed_conversational_source_selection.py`. Otros candidatos sujetos a revisión son `app/desktop_ui.py`, `app/governed_information_normalizer.py`, `app/governed_information_sources.py` y `app/official_conversation_gateway.py`. Ninguno queda autorizado para edición por esta lista.

## 2. Paquetes mínimos

| Paquete | Alcance | Dependencia | Estado |
|---|---|---|---|
| PKG-01 | Identidad, reserva, ordinal, resultado individual | Contratos VIC | PROPOSED |
| PKG-02 | Imagen + ordinal y limpieza parcial Tk | PKG-01 | PROPOSED |
| PKG-03 | Aislamiento de excepciones dispatcher | Consumidores UI | PROPOSED |
| PKG-04 | Comprobante VIC y admisión E2 oficial | PKG-01/02 y puente físico por localizar | PROPOSED |
| PKG-05 | Correspondencia semántica y lenguaje natural flexible | Frontera con intención conversacional | PROPOSED |
| PKG-06 | Pruebas incrementales y aceptación | Paquetes pertinentes | PROPOSED |

## 3. Gates

- **GATE-A — Contratos:** identidad, ordinal, resultado VIC, correspondencia y autoridad E2 sin ambigüedad; pendiente aprobación.
- **GATE-B — Alcance físico:** archivos, consumidores, dependencias y exclusiones GUI-06 verificados; parcial.
- **GATE-C — Autorización:** permiso explícito por operación y paquete; no concedido para implementación ni Git.
- **GATE-D — Evidencia:** pruebas gobernadas antes de cierre productivo; no ejecutado.

## 4. Checkpoints incrementales

| ID | Unidad | Estado |
|---|---|---|
| CP-DOC-01 | Inspección contractual SCOPE-02 | Creación documental autorizada; Git pendiente |
| CP-DOC-02 | Revisión SCOPE-03 | Creación documental autorizada; Git pendiente |
| CP-IMP-01 a CP-IMP-05 | Paquetes de implementación respectivos | DENY |
| CP-VER-01 | Verificación integral | DENY |
| CP-MASTER-RECONCILE | Reconciliación independiente del Plan Maestro | PROPOSED; fuera de alcance |

Secuencia por unidad: documento → revisión → archivos exactos → autorización de staging → commit autorizado → push autorizado → registro de SHA, rama, remoto y pendientes. La autorización documental no habilita por sí misma Git de escritura. No agrupar cambios ajenos ni acumular grandes lotes.

## 5. Exclusiones y estado previo

Seis archivos modificados preexistentes:

- `ROBY_XI_2_PLAN_MAESTRO_EVOLUCION_POST_INTEGRACION_ES.txt`
- `app/desktop_bootstrap.py`
- `app/unified_experience_layer.py`
- `core/governed_provider_execution_adapter/adapter.py`
- `core/local_provider_runtime_adapter/adapter.py`
- `core/operational_response_assembly/assembler.py`

Dos archivos no rastreados:

- `app/gui06_diagnostic_desktop_adapter.py`
- `core/gui06_diagnostic_probe.py`

**Excluir los ocho del staging y commits R01-P5Y-03.** `app/desktop_ui.py` es compartido y requiere verificar consumidores antes de intervenir.

## 6. Plan Maestro — reconciliación separada

El diff mostrado registró 27 líneas añadidas y 87 eliminadas y advertencia de LF→CRLF. Cambios en GROW longitudinal, composición multimodal y autoexplicación sustituyen o eliminan afirmaciones de realización certificada en la versión base. No se determina autoría ni se verifica independientemente esa certificación. No restaurar, editar ni incluir el archivo en estos checkpoints. La reconciliación corresponde a otro proceso.

## 7. Ubicación y autorización exacta

La inspección encontró `docs/` rastreado, sin coincidencias por nombre para P5Y-03, y `Test-Path=False` para los dos nombres candidatos. Los artefactos aprobados para **creación solamente** son:

- `docs/P5Y03_IMP_SCOPE_02_INSPECCION_CONTRACTUAL_FINAL.md`
- `docs/P5Y03_IMP_SCOPE_03_AUTORIZACION_Y_CHECKPOINTS_GIT.md`

Estos documentos se entregan como archivos descargables para colocación posterior en el repositorio local; **no se afirma que hayan sido escritos en `C:\Users\CAHCA\Desktop\HAL`**.

| Operación | Autorización |
|---|---|
| Crear los dos documentos | AUTORIZADO |
| Modificar archivos existentes | NO AUTORIZADO |
| Ejecutar pruebas o cambios productivos | DENY |
| `git add`, commit o push | NO AUTORIZADO |
| Levantar HOLD/STOP/RED/GREEN | NO AUTORIZADO |

**Dictamen final:** dos documentos preparados para revisión; checkpoints Git pendientes; gobernanza inalterada.
