# M399.5 — Governed Isolated Diagnostic Proposal

## Objetivo

M399.5 extiende la cadena de Self-Diagnostics gobernado desde **prueba reproducible → propuesta aislada** sin conceder a ROBY autoridad para reparar, aplicar, aprobar ni ejecutar cambios sobre su código operativo.

La cadena alcanzada queda:

**Observación → tendencia → anomalía → hipótesis → confianza → evidencia → prueba reproducible → propuesta aislada**

## Autoridad

`GovernedSelfDiagnostics` conserva la única autoridad técnica `self_diagnostics`. `proposal.py` no crea un manager, engine, authority ni cerebro paralelo. Las autoridades fuente continúan siendo dueñas de las observaciones que originaron el diagnóstico.

## Condiciones de entrada

Una propuesta sólo puede prepararse si:

- existe una `DiagnosticProofSpecification` M399.4;
- su `DiagnosticProofResult` es `reproduced`;
- `proof_id`, `hypothesis_id` y `evidence_digest` coinciden;
- la intención de cambio fue suministrada explícitamente mediante `DiagnosticProposalRequest`;
- se declaran archivos potencialmente afectados y tests de validación previstos.

M399.5 **no infiere una corrección** desde una anomalía o hipótesis. La intención de remediación debe ser explícita y permanece sólo como texto estructurado para revisión.

## Aislamiento

El único destino persistente permitido es:

`.roby/review/proposals/<proposal_id>/proposal.json`

Ese artefacto contiene metadatos diagnósticos y de revisión. No contiene un patch ejecutable, no modifica los archivos listados en `affected_files` y no autoriza que esos archivos sean tocados.

La escritura falla si el artefacto ya existe. M399.5 no sobrescribe silenciosamente propuestas previas.

## Estado

Toda propuesta nace como `draft`. En M399.5 no existen transiciones de aprobación o rechazo automáticas. Tampoco existe `apply`.

**crear una propuesta ≠ autorizar una modificación**

## Límites permanentes

M399.5 permanece:

- sin sandbox;
- sin patch ni diff ejecutable;
- sin `apply`, reparación o rollback;
- sin ejecución de comandos;
- sin modificación de `core/`, `app/`, `tests/` u otro código operativo;
- sin background, polling o monitorización residente;
- sin aprobación automática;
- sin automodificación silenciosa.

La regla epistemológica continúa vigente:

**predicción ≠ certeza**

Una proof reproducida prueba reproducibilidad del assessment, no causalidad. Una propuesta basada en esa proof sigue siendo una propuesta para decisión humana, no una corrección cierta.
