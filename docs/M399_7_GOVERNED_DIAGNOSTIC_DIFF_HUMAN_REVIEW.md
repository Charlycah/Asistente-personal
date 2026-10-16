# M399.7 — Governed Diagnostic Diff & Human Review

## Propósito

M399.7 extiende la cadena gobernada de Self-Diagnostics únicamente desde
**sandbox → tests → diff → explicación → decisión humana**.

`GovernedSelfDiagnostics` conserva la única autoridad técnica `self_diagnostics`.
No se crea un segundo engine, manager, cerebro ni autoridad.

## Diff gobernado

El diff se calcula entre la baseline operativa y los archivos candidatos de un
sandbox M399.6 con resultado `passed`. Sólo se incluyen archivos candidatos
explícitos del sandbox. El diff es evidencia inerte para revisión: no es un patch
ejecutable y no se aplica al árbol operativo.

La explicación conserva propuesta, intención de cambio, cantidad de tests
declarados y archivos cambiados. El éxito del sandbox es evidencia técnica, no
autorización.

## Decisión humana

La decisión exige `review_id`, revisor explícito, decisión y explicación.
Puede registrar aprobación para aplicación manual o rechazo, pero
**aprobación ≠ aplicación**. M399.7 no contiene ningún mecanismo para aplicar el
cambio.

Los artefactos permanecen bajo
`.roby/review/proposals/<proposal_id>/review/<review_id>/`.

## Límites permanentes

- **predicción ≠ certeza**;
- una proof reproducida no demuestra verdad causal;
- sandbox passed no equivale a aprobación;
- aprobación humana no equivale a aplicación;
- sin aplicación automática;
- sin `git apply`, checkout, rollback, reparación ni automodificación silenciosa;
- cualquier cambio al código operativo sigue fuera de M399.7.
