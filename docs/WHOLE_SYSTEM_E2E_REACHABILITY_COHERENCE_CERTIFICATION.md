# ROBY XI.2 — Whole-System E2E Reachability & Coherence Certification

Estado: **CERTIFICATION PASS / CLOSURE VALIDATION PENDING**.

## Contrato congelado

Esta certificación es exclusivamente diagnóstica y de solo lectura sobre producción. No crea capability, authority, manager, gateway, persistence ni autonomía; no modifica `app/`, `core/` ni `domain/` para obtener PASS. Cualquier futura divergencia `PARTIAL` o `FAIL` debe volver a **Audit → Contract / Go-No-Go** antes de intervenir producción.

El harness certifica exactamente 16 cadenas existentes en forma `entry → authority/capability → productive consumer → observable autorizado`, preservando las obligaciones de provenance, scope y rutas históricas declaradas por cada cadena. El vocabulario de resultado está congelado en `PASS`, `PASS_BY_DESIGN`, `PARTIAL` y `FAIL`.

## Certificación E2E

Las 16 cadenas certificadas son: información gobernada→relevancia; regla temporal→reasoning; intake de decisión→GCDR advisory; advisory→realización conversacional; proof diagnóstico→proposal inerte; scale benchmark; reasoning-quality benchmark; independent reasoning evaluation; clasificación de autonomía→decisión acotada; ToolRequest→ToolGateway; memory runtime; planning runtime; reflection runtime; living-conversation runtime; governed-world integration; y la ruta histórica Whole-System Integration M210.

Resultado: **16 PASS / 0 PARTIAL / 0 FAIL**.

## Controles negativos de no-escalación

Se certifican ocho controles: el harness no define authority, manager/gateway ni persistencia productiva; no concede ejecución/autonomía; la mutación continúa limitada por consentimiento; capacidades no registradas y deshabilitadas siguen fail-closed; y self-improvement permanece proposal-only.

Resultado: **8 PASS_BY_DESIGN / 0 FAIL**.

## Artefactos

- Harness: `scripts/whole_system_e2e_reachability_coherence_certification.py`.
- Pruebas: `tests/architecture/test_whole_system_e2e_reachability_coherence_certification.py`.
- Reporte reproducible: `docs/quality/WHOLE_SYSTEM_E2E_REACHABILITY_COHERENCE_CERTIFICATION.json`.

## Closure Audit

El cierre exige `ruff check .` y `pytest -q` limpios. En el entorno de construcción actual, la certificación específica pasó 9/9 y el conjunto dirigido de rutas relacionadas pasó 78/78. La colección completa reconoce 12.556 tests (12.547 baseline + 9 nuevos), pero `pytest -q` no pudo finalizar dentro del límite de ejecución disponible y Ruff no está instalado en el entorno; el intento de instalación falló por ausencia de red. Por lo tanto, el cierre global queda explícitamente pendiente de esas dos validaciones obligatorias en el entorno oficial.

El harness sólo puede escribir el reporte diagnóstico solicitado; declara explícitamente `production_roots_modified_by_harness=()` y no contiene un camino de reparación automática. Un gap observado se conserva como evidencia y no autoriza una modificación de producción.
