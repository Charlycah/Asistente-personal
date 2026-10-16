# ROBY XI.2 — CAP-17/CAP-11 Governed Evidence → Existing Hypothesis Reassessment → Requirement Continuation — GREEN

## Alcance
Cierre quirúrgico del CONTRACT RED certificado. No abre Planning N+1, Memory, Learning ni nuevas autoridades.

## Integración
- `DiscriminatingEvidenceRequirement` preserva `source_report_id` y el discriminador propaga el `report_id` exacto.
- `GovernedHypothesisDeepener` expone `reassess_with_governed_evidence`, independiente del transporte CAP-17/Level-2.
- El reassessment conserva el mismo conjunto de hipótesis, source/world lineage y autoridad `governed_reasoning`; incorpora una evidencia gobernada sin establecer verdad o causalidad.
- El resultado productivo CAP-17 preserva `local_reasoning_reentry`.
- La ruta productiva respeta: local reasoning re-entry → Episode recording → hypothesis reassessment → existing CAP-11 requirement admission.
- `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1` conserva ownership de discriminación/continuation y admite la variante local sin fabricar lineage Level-2.
- STOP antes de Planning N+1.

## Validación en entorno de construcción
- CONTRACT RED focal: 9 passed.
- Slice CAP-17/CAP-11 adyacente: 40 passed.
- M361 + contrato focal tras regeneración: 14 passed.
- `compileall` de `core/governed_reasoning` y `app`: limpio.
- La suite completa fue iniciada pero excedió el límite de ejecución de este entorno; no se declara certificación completa aquí.
- Ruff no está instalado en este entorno; la certificación final corresponde al entorno local oficial del usuario.

## Baseline de entrada certificado por el usuario
13.921 PASS + Ruff limpio + 7 RED FAIL esperados + 0 fallos externos al contrato.
