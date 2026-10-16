# M399.3 — Governed Diagnostic Hypothesis & Confidence

## Propósito

M399.3 extiende la frontera M399.2 hasta:

**Observación → tendencia → anomalía → hipótesis → confianza → evidencia**

El incremento mantiene el principio permanente **predicción ≠ certeza**. Una
hipótesis diagnóstica es una explicación candidata sometida a evidencia, nunca
una causa demostrada por el solo hecho de existir una anomalía.

## Autoridad única

`GovernedSelfDiagnostics` conserva la única autoridad técnica
`self_diagnostics`. M399.3 no crea otra authority, manager, engine u
orchestrator. El módulo de evaluación de hipótesis es lógica interna subordinada
a esa autoridad.

Las autoridades fuente continúan siendo propietarias de sus observaciones y
`UnifiedBrain.diagnostics` conserva el ámbito cognitivo definido antes de M399.

## Hipótesis explícita

M399.3 no genera causas desde una anomalía. La evaluación requiere una
**hipótesis candidata explícita** con:

- `hypothesis_id` explícito;
- statement no vacío;
- `observation_id` que la apoyan;
- `observation_id` que la contradicen, cuando existan.

Toda evidencia debe pertenecer al `SelfDiagnosticReport` evaluado. Una misma
observación no puede apoyar y contradecir simultáneamente la misma hipótesis.
La evaluación sólo se habilita cuando M399.2 ya produjo una anomalía `observed`.

## Confianza explicable

`DiagnosticConfidencePolicy` hace visibles los criterios de evaluación:

- mínimo de evidencias de soporte;
- ratio mínimo para considerar la hipótesis soportada;
- ratio mínimo para confianza alta.

El `confidence_score` es el cociente reproducible entre evidencias de soporte y
el total de evidencias explícitamente clasificadas como soporte o contradicción.
La clasificación `insufficient_evidence`, `low`, `medium` o `high` conserva la
política utilizada y un rationale trazable.

Una confianza `high` sigue sin significar certeza causal. M399.3 no transforma
un score en verdad, no elimina evidencia contradictoria y no inventa evidencia
para elevar confianza.

## Evidencia

El assessment conserva los `evidence_codes` de las observaciones realmente
referenciadas. No consulta fuentes externas, archivos, procesos, providers ni
hardware para completar evidencia ausente.

## Límites permanentes de M399.3

- sólo lectura;
- hipótesis explícita, nunca generación causal automática;
- confianza derivada únicamente de evidencia explícita;
- sin persistencia nueva;
- sin proposals;
- sin `.roby/review/proposals/...`;
- sin sandbox;
- sin tests de reparación ni generación de diff;
- sin patch, apply, rollback o modificación de código;
- sin polling ni monitorización residente;
- sin acción correctiva automática;
- sin elevar una hipótesis a certeza.

La etapa posterior podrá añadir prueba reproducible y preparación de propuestas,
pero deberá conservar la evidencia y confianza de M399.3 y requerir decisión
humana antes de cualquier modificación operativa.
