# M103 — Shared Intellectual Interests

## Objetivo

Identificar intereses intelectuales compartidos mediante evidencia
conversacional explícita y trazable, preservando incertidumbre y fronteras con
memoria, aprendizaje, continuidad y generación.

## Componentes

- `IntellectualInterestEvidenceKind`
- `SharedIntellectualInterestStatus`
- `SharedIntellectualInterestStrength`
- `SharedIntellectualInterestsPolicy`
- `IntellectualInterestEvidence`
- `SharedIntellectualInterestsRequest`
- `SharedIntellectualInterest`
- `SharedIntellectualInterestsAssessment`
- `SharedIntellectualInterestsRepository`
- `InMemorySharedIntellectualInterestsRepository`
- `SharedIntellectualInterests`

## Invariantes

- El propietario debe coincidir con M102.
- Toda evidencia posee tema, confianza y fuente.
- Los temas se agregan sin distinguir mayúsculas y minúsculas.
- Los resultados insuficientes o no aplicables no contienen intereses.
- Un interés detectado no se convierte automáticamente en memoria.
- El identificador deriva determinísticamente de sus entradas y timestamp.

## Validación

- Ruff limpio.
- 1520 tests pasando.
- 35 tests específicos de M103.
