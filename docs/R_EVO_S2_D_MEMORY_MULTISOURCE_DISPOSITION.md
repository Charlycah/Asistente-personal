# ROBY XI.2 — R-EVO-S2-D — MEMORY-PLUS-MULTISOURCE CONTRACT DISCRIMINATION & OWNER STOP

**Clase:** acta candidata de disposición documental.  
**Baseline:** `ultima version corregida(8).zip` (inspección estática, sin modificación).  
**Estado:** OWNER CERTIFICATION PENDING / STOP PRODUCTIVE.

## 1. Alcance

Discriminar la ruta de memoria recuperada frente a la ruta de selección explícita de múltiples fuentes, sin presumir integración ausente ni crear nuevas autoridades.

## 2. Evidencia del código

- `app/governed_reasoning_runtime.py`, `CanonicalProductiveReasoningSource.__call__`, líneas 353–414: recibe `recalled_memory_evidence`; si existe selección explícita (documentos, fuentes o referencias), delega a `ordinary_turn_multisource_reachability_adapter.admit_and_reason()` y retorna inmediatamente (líneas 366–389), **sin transportar** ese argumento. Si no hay selección explícita, pasa `recalled_memory_evidence` a `gateway.evaluate_productive_episode()` (líneas 391–414).
- `app/ordinary_turn_multisource_reachability_adapter.py`, líneas 16–43: la firma y la delegación transportan solo las selecciones explícitas, contribución visual y tiempo; no reciben `recalled_memory_evidence`.
- `app/same_episode_explicit_evidence_convergence_adapter.py`, líneas 30–84: registra las evidencias explícitas admitidas y llama una vez a `reasoning_gateway.reason()`; no acepta `recalled_memory_evidence`.
- `tests/architecture/test_post_12776_single_reasoning_multisource_convergence_contract_red.py`, líneas 39–105: exige transporte de selección explícita por la etapa única de Reasoning y prohíbe crear una segunda ruta desde preparación. No demuestra ni exige convergencia simultánea con `recalled_memory_evidence`.

## 3. Discriminación contractual

**Confirmado:** existe una bifurcación observable: la selección explícita usa el adaptador multisource; la ruta ordinaria puede entregar memoria recuperada a `evaluate_productive_episode`. Ambas preservan la autoridad canónica de Reasoning.

**No confirmado:** que la exclusión de `recalled_memory_evidence` en la rama explícita sea una decisión contractual deliberada; tampoco se ha probado una regresión o que una necesidad productiva exija ambas entradas en el mismo episodio. No se debe convertir esta ausencia de transporte en un defecto supuesto.

**Límite adicional:** la presencia de referencias explícitas no acredita por sí sola que sean equivalentes a recuerdos recuperados o que el resultado final exponga toda la procedencia al usuario.

## 4. Disposición

- `SINGLE_REASONING_AUTHORITY: PRESERVED`
- `EXPLICIT_MULTISOURCE_ROUTE: PRESENT`
- `ORDINARY_RECALLED_MEMORY_ROUTE: PRESENT`
- `SIMULTANEOUS_MEMORY_PLUS_EXPLICIT_EVIDENCE: NOT CONTRACTUALLY DEMONSTRATED`
- `INTENTIONAL_SEPARATION: NOT ESTABLISHED`
- `PRODUCTIVE_REGRESSION: NOT REPRODUCED`
- `NEW_PRODUCTIVE_RESIDUAL: NOT DEMONSTRATED`
- `RED_GREEN_AUTHORIZATION: NONE`
- `OWNER_CERTIFICATION: PENDING`
- `STOP_PRODUCTIVE: PRESERVED`

## 5. Criterio de eventual reentrada

Solo ante un caso de uso aprobado que requiera simultáneamente memoria recuperada y selección explícita, contrastar el contrato de entrada, los límites de admisión y la respuesta observada; reproducir el comportamiento mediante pruebas existentes antes de proponer un RED quirúrgico. No modificar firmas, adaptadores, memoria, Reasoning ni documentación canónica durante este cierre.
