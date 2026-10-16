# ROBY XI.2 — Diagnostic Evidence Harness F1–F10

**Baseline:** 12.606 tests + Ruff limpio (baseline oficial aportado)  
**Modo:** diagnóstico / producción congelada  
**Harness:** `whole-system-cognitive-limits-diagnostic-evidence-harness-v1`

## Resultado ejecutivo

- Suite compartida: **156 passed in 4.48s**
- F1–F10: **8 PASS · 1 PASS_BY_DESIGN · 1 PARTIAL · 0 FAIL**
- Fingerprint `app/core/domain` preservado: **True**
- L2 Governed Cross-Capability Transfer: **True**
- L3 Flexible Cognitive Composition: **False**

## Matriz F1–F10

| Familia | Dimensiones | Estado | Objetivo | Interpretación contractual |
|---|---|---|---|---|
| F1 | D1 | PASS | Capability selection by relevance | PASS means operational selection is executable; it does not by itself certify general cognitive relevance selection. |
| F2 | D2, D8 | PASS | Variable cross-capability composition | PASS certifies governed composition mechanisms, not open-ended L3 composition. |
| F3 | D3, D7, D15 | PASS | Same-context learned knowledge reuse | PASS is causal evidence of governed reuse inside certified memory pathways. |
| F4 | D4, D6, D7, D15 | PASS | Novel-context structural transfer | PASS demonstrates bounded structural transfer machinery; productive conversational reachability is assessed separately. |
| F5 | D5, D6, D14, D15 | PASS_BY_DESIGN | Negative transfer rejection | PASS_BY_DESIGN is expected when bounded transfer rejects structural/scope/provenance mismatch. |
| F6 | D6, D7 | PASS | Analogy versus superficial similarity | PASS establishes structural discrimination within the bounded transfer grammar; broader analogy remains unproven unless adversarial evidence exists. |
| F7 | D14, D15 | PASS | Provenance and owner/scope preservation | PASS certifies explicit transfer boundary guards; whole-chain preservation is bounded by existing cross-capability evidence. |
| F8 | D9, D10, D12 | PASS | Novelty, curiosity, and spontaneous inhibition | PASS demonstrates bounded/productive mechanisms; internally derived general cognitive surprise is a separate higher bar. |
| F9 | D11, D8 | PARTIAL | Improvisation and recomposition | A green test set is insufficient for PASS: unless tests prove non-preprogrammed strategy synthesis, this family remains PARTIAL. |
| F10 | D13, D1, D2 | PASS | Changed conditions and bounded cognitive recomposition | PASS certifies changed-condition advisory; automatic replanning remains outside the frozen autonomy boundary. |

## Lectura arquitectónica

El diagnóstico sostiene que ROBY ya posee selección operacional, composición gobernada, reutilización de conocimiento aprendido, transferencia estructural acotada, rechazo de transferencia inválida, preservación explícita de provenance/scope, mecanismos productivos de curiosidad y manejo bounded de changed conditions.

**F9 permanece PARTIAL por diseño del Contract.** La existencia de planificación + orquestación no prueba todavía improvisación cognitiva. Falta una prueba causal donde ROBY construya una estrategia no representada previamente como escenario/pipeline específico, y donde una ablación demuestre que la combinación de capacidades cambió por las necesidades del problema.

Por tanto, este harness **no autoriza producción**. El siguiente gate debe concentrarse en evidencia adversarial de L3: pares misma estructura/vocabulario distinto, mismo vocabulario/estructura distinta, memoria relevante + distractora, y changed conditions que obliguen a recomposición sin autonomía nueva.

## Integridad

Fingerprint antes: `c0308f43f22116d1e4f1fc65947467f177f2dcf6281f8c48aa1d6e8b3ed025f9`  
Fingerprint después: `c0308f43f22116d1e4f1fc65947467f177f2dcf6281f8c48aa1d6e8b3ed025f9`

No se modificaron `app/`, `core/` ni `domain/` durante el harness.

## Nota de validación

El entorno de ejecución disponible aquí no contiene el ejecutable/módulo `ruff`, por lo que no fue posible ejecutar Ruff sobre los dos archivos diagnósticos nuevos. Esto **no modifica** el estado Ruff-limpio del baseline oficial; simplemente deja pendiente el lint específico del harness en un entorno que tenga Ruff instalado. Los autocontroles del harness dieron **4 passed**, y la suite F1–F10 dio **156 passed**.
