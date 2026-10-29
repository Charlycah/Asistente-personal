# P5Y03-IMP-SCOPE-02 — Inspección contractual final

**ROBY XI.2 · R01-P5Y-03 · DOCUMENTARY / PROPOSED**
**Base Git reportada:** `master` / `754012c` · **Fecha:** 2026-10-29

> Documento basado en las salidas de inspección aportadas en conversación. No certifica ejecución directa en el repositorio. Bloqueos vigentes: M377 HOLD; STOP_PRODUCTIVE ACTIVE; MODEL_ACQUISITION UNMAPPED / DENY / NO-GO; RED DENY; GREEN DENY; GUI-06 PROTECTED; R01-P5Y-03 OPEN — DOCUMENTARY; ONE BRAIN — ONE AUTHORITY PER CAPABILITY.

## 1. Objeto

Inspeccionar las fronteras de selección y proyección de imágenes, entrega asíncrona, incorporación Tk, ordinal individual, despacho UI y conexión posible entre VIC y E2. Separar evidencia observada, brechas y decisiones propuestas.

## 2. Matriz contractual

| Control | Evidencia observada | Estado |
|---|---|---|
| S02-01 | Localizados `DesktopGovernedFloatingImageViewer`, `GovernedImagePreviewCoordinator`, `PreviewViewer` y `PreviewDispatcher` | VERIFIED en rutas examinadas |
| S02-02 | `present()` agenda recuperaciones; `_deliver()` invoca `render_preview()` sin consumir el `bool` | VERIFIED |
| S02-03 | Existe `_generation`; no se observó reserva explícita de `presentation_id`, `slot_id` y `visible_ordinal` | BRECHA LOCALIZADA |
| S02-04 | `render_preview()` crea imagen Tk, pero no incorpora ordinal visible; limpieza parcial y excepciones posteriores requieren atención | BRECHA LOCALIZADA |
| S02-05 | `UIThreadDispatcher.drain()` no aísla excepciones por callback; el sondeo podría interrumpirse | VERIFIED como riesgo potencial |
| S02-06 | Autoridad conversacional y gateways E2 localizados; puente físico VIC→E2 no confirmado | PARTIAL |
| S02-07 | Selector, normalizador, admisión de fuentes y proyección visual inspeccionados; no prueban correspondencia semántica individual con petición original | VERIFIED en métodos examinados |
| S02-08 | Git `master` / `754012c`; cuatro archivos visuales rastreados sin cambios visibles; ocho rutas con cambios preexistentes | VERIFIED para estado mostrado |

## 3. Evidencia técnica

**Coordinador:** `app/desktop_governed_image_preview_coordinator.py`, `present()` aproximadamente líneas 72–99 y `_deliver()` 139–156. Comprueba generación e identidad antes de entregar, pero descarta resultado booleano. La entrega asíncrona no demuestra compromiso visual individual.

**Visor:** `app/desktop_governed_floating_image_viewer.py`, `render_preview()` aproximadamente 138–173. Comprueba hilo, ventana, pertenencia del artefacto, tipo PNG y bytes; crea `PhotoImage`, `Label` y `pack`. No se observó ordinal visible asociado. Un `True` no certifica percepción de píxeles, observación humana ni aceptación E2. El cierre y la limpieza parcial requieren pruebas futuras.

**Dispatcher:** `app/desktop_ui.py`, `UIThreadDispatcher` aproximadamente 138–155 y `poll_ui_dispatcher()` 1273–1277. Una excepción de callback podría impedir programar el siguiente `root.after`. No se ha observado un incidente en ejecución.

**Fuente y normalización:** `app/governed_information_sources.py:337–350` acepta solo si la fuente está `DECLARED` y los temas son subconjunto de los declarados; retorna `RelevanceCandidate`, sin recibir la solicitud original. `app/governed_information_normalizer.py:111–147` llama a ese método y conserva metadatos; no demuestra validación independiente del sujeto. `app/governed_conversational_source_selection.py` selecciona fuentes, no acredita por sí mismo la identidad de cada imagen.

**Proyección visual:** `app/external_image_presentation.py:8–52` define procedencia y artefacto con identificadores, título, descripción, fecha, tipo, URL y verificación recibida. `project_external_image()` líneas 55–66 exige `media_type == "image"`, URL HTTPS con `netloc` y construcción válida. Esto no valida contenido remoto, sujeto, temporalidad o correspondencia con intención original.

**Precisión transversal:** distinguir Curiosity de Perseverance y de una imagen genérica de Marte, así como distinguir objetos específicos en dominios domésticos. Comprender paráfrasis, elipsis, referencias contextuales y correcciones sin comandos rígidos. No se concluye que toda la aplicación carezca de validación semántica: el hallazgo se limita a los métodos inspeccionados.

## 4. Decisiones — todas PROPOSED

| ID | Propuesta |
|---|---|
| S02-D01 | Reservar identidad de presentación, slot, artefacto y ordinal antes de tareas asíncronas; preservar compatibilidad de `render_preview() -> bool` hasta integrar un resultado explícito |
| S02-D02 | Aislar excepciones por callback y preservar continuidad de sondeo UI |
| S02-D03 | Integrar comprobantes VIC con autoridad conversacional existente, sin cerebro paralelo |
| S02-D04 | Reutilizar selector de fuentes; selección no equivale a coincidencia semántica |
| S02-D05 | Separar selección, ejecución, normalización, admisión y correspondencia |
| S02-D06 | No convertir el normalizador en segunda inteligencia conversacional |
| S02-D07 | Mantener `accept()` como control de fuente y temas, no como certificación semántica |
| S02-D08 | Preservar proyección visual y verificar correspondencia individual en frontera adecuada |

## 5. VIC individual y E2 — contrato pendiente

Se propone correlacionar `presentation_id`, `slot_id`, `artifact_id`, `visible_ordinal`, token de generación, `committed` y `failure_reason`. `committed=True` únicamente para imagen y ordinal correctos incorporados conjuntamente a la ocurrencia reservada; no equivale a aceptación E2. Rechazar generación obsoleta, duplicados contradictorios y asociación ambigua. E2 acepta solo comprobantes válidos bajo autoridad oficial.

## 6. Evidencia futura y límites

Pendientes pruebas gobernadas de orden asíncrono, misma URL en ocurrencias distintas, fallos `PhotoImage`/`Label`/`pack`, ordinal incorrecto, cierre, limpieza parcial, generación obsoleta, callbacks fallidos, idempotencia, rechazo E2 y correspondencia semántica contextual. Referencias de planificación: `P5Y03-RED`, `IMP05-RED`, `IMP06-RED`, `SEM-RED`. **No ejecutadas en esta revisión.**

**Dictamen:** inspección documental completada para evidencia disponible; conexión física VIC→E2, validación semántica integral y aislamiento de dependencias compartidas siguen pendientes. Sin autorización de implementación, pruebas ni Git de escritura.
