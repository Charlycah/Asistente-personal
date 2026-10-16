# ROBY XI.2 — R-RIQ-S2-H2-FEASIBILITY
## Canonical Experimental Route & Measurement Feasibility

**Estado:** CANDIDATE / STATIC REVIEW / OWNER APPROVAL PENDING  
**Baseline:** `ultima version corregida(9).zip`  
**Protocolo:** `docs/R_RIQ_S2_H2_EXPERIMENTAL_DESIGN_CANDIDATE.md` (incorporación y SHA-256 confirmados por el Owner)  
**Límite:** Sin pruebas ejecutadas, sin experimentos, sin cambios productivos ni nuevos módulos.

## 1. Alcance

Determinar si las superficies canónicas existentes permiten observar las categorías epistemológicas y medir resultados de respuesta final en condiciones C0/C1 comparables, sin alterar autoridades ni restaurar superficies retiradas.

## 2. Evidencia estática directamente inspeccionada

- `core/cognitive_maturity/unified_epistemic_evidence.py`: `UnifiedEpistemicCategory` enumera `observed`, `inferred`, `possible`, `insufficient_information`; `UnifiedEpistemicRecord` exige procedencia, evidencia trazable y restringe `allows_fact_statement` a `OBSERVED`. La autoridad normaliza informes ejecutivos estructurados; esto no prueba cobertura universal de respuestas ordinarias.
- `tests/architecture/test_m389_8_unified_epistemic_evidence.py`: contratos de normalización y tratamiento de niveles epistemológicos; su presencia no equivale a ejecución actual.
- `core/governed_reasoning/epistemic_sufficiency.py`: `EpistemicSufficiencyStatus` tiene `sufficient`, `insufficient`, `indeterminate`. El assessment es consultivo, derivado y contextual; declara `closes_reasoning=False` y `authorizes_stopping=False`.
- `core/governed_reasoning/derived_epistemic_sufficiency_assessment.py`: carrier derivado de solo lectura, `is_evidence=False`, `is_claim=False`, `establishes_truth=False`, `authorizes_stopping=False`.
- `app/response_presenter.py`: presenta `body`, `source`, `link` y filtra metadatos; no implementa política universal de abstención epistemológica.
- `tests/architecture/test_post_m409_1_epistemic_sufficiency_productive_projection_retirement.py`: exige ausencia de `app/governed_epistemic_sufficiency_productive_consumption.py` y prohíbe dependencias productivas de esa proyección retirada.

## 3. Factibilidad por unidad de medida

| Unidad | Dictamen | Justificación |
|---|---|---|
| Categoría epistemológica M389.8, en su alcance | FEASIBLE_STATIC | Contrato de categorías, procedencia y restricciones explícito |
| Suficiencia contextual derivada | FEASIBLE_STATIC | Estados y carrier existentes, no autorizantes |
| Abstención universal de respuesta final | NOT_DEMONSTRATED | No hay contrato universal acreditado por las superficies inspeccionadas |
| Comparación C0/C1 sin modificar el producto | NOT_ENABLED_ON_CURRENT_EVIDENCE | No se ha acreditado un par de rutas canónicas distinguibles y comparables |
| Estudio observacional de una condición | CONDITIONALLY_FEASIBLE | Requiere identificar punto de captura read-only y criterios de etiquetado; aún no habilitado para ejecución |

**Dictamen agregado:** `PARTIALLY_FEASIBLE` para medición de mecanismos internos; `EXPERIMENT_NOT_ENABLED` para comparación causal C0/C1 de respuestas finales con la evidencia actual. No implica bug ni residual productivo.

## 4. Brechas documentales que requieren evidencia, no código

1. Localizar una ruta productiva canónica de episodio ordinario hasta la respuesta final y demostrar qué señales epistemológicas atraviesan cada límite.
2. Precisar el punto de observación read-only ya admitido, o declarar su ausencia; no crear instrumentación automáticamente.
3. Verificar que C0 y C1 son distinguibles por entradas autorizadas, con modelo, contexto y herramientas equivalentes, sin desactivar capacidades ni restaurar proyecciones retiradas.
4. Congelar definiciones de etiqueta, adjudicación, abstención, denominadores, exclusiones y umbrales estadísticos antes de experimentar.
5. Obtener aprobación separada del Owner para cualquier prueba o experimento posterior.

## 5. Decisión recomendada

**STOP experimental.** Mantener H2 como hipótesis no contrastada. Autorizar, si el Owner lo decide, solo un siguiente subpaso documental: `R-RIQ-S2-H2-ROUTE-TRACE`, trazado de la ruta canónica hasta la salida final y observabilidad existente. Si no aparece ruta válida, cerrar factibilidad como `EXPERIMENT_NOT_ENABLED` y considerar una evaluación observacional sin inferencia causal, siempre con autorización separada.

## 6. Gobierno y trazabilidad

- No se ejecutaron tests ni corpus experimental.
- No se modificaron archivos del ZIP, maestros, código o memoria.
- No se abrió RED/GREEN ni se identificó un nuevo residual productivo.
- `R-RIQ-00`: aprobado por Owner.
- `R-RIQ-S1-FINAL`: aprobado por Owner.
- Protocolo H2: integridad verificada, aprobación específica no presumida.
- `STOP_PRODUCTIVE`: activo.
- Este dictamen es **candidato**, no cierre certificado ni autorización de ejecución.
