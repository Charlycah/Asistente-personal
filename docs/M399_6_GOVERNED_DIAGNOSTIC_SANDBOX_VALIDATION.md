# M399.6 — Governed Diagnostic Sandbox Validation

## Objetivo

M399.6 extiende la cadena de Self-Diagnostics gobernado desde **propuesta aislada → sandbox → tests** sin conceder a ROBY autoridad para aplicar cambios sobre el código operativo.

La cadena alcanzada queda:

**Observación → tendencia → anomalía → hipótesis → confianza → evidencia → prueba reproducible → propuesta aislada → sandbox → tests**

## Autoridad

`GovernedSelfDiagnostics` conserva la única autoridad técnica `self_diagnostics`. `sandbox.py` es un mecanismo subordinado de validación y no crea un manager, engine, authority ni cerebro paralelo.

## Entrada explícita

M399.5 conserva intención y metadatos, no un patch. Por ello M399.6 exige un `DiagnosticSandboxRequest` explícito que contiene los archivos candidatos a validar. Cada archivo candidato debe haber sido declarado previamente en `DiagnosticProposal.affected_files`.

ROBY no inventa el contenido candidato y no deriva una corrección automáticamente desde la hipótesis.

## Copia aislada

La validación crea una **copia aislada** bajo:

`.roby/review/proposals/<proposal_id>/sandbox/<sandbox_id>/`

Se excluyen `.git`, entornos virtuales, caches y el propio árbol `.roby`. Los contenidos candidatos se escriben sólo dentro de esa copia. El archivo equivalente del proyecto operativo no se modifica.

Este aislamiento es una frontera de proyecto y filesystem; M399.6 no afirma proveer virtualización de sistema operativo ni aislamiento host completo.

## Tests gobernados

El sandbox no acepta un comando shell libre. Ejecuta únicamente:

`python -m pytest -q <validation_tests declarados por la propuesta>`

El resultado conserva código de retorno, stdout, stderr, archivos candidatos y tests ejecutados. Un fallo de tests es evidencia diagnóstica; no dispara reparación, retry, rollback ni aplicación.

## Estados

El resultado puede ser `passed`, `failed` o `blocked`. `passed` significa solamente que los tests declarados terminaron correctamente dentro de la copia aislada.

**sandbox passed ≠ cambio autorizado**

M399.6 **no autoriza aplicación** sobre la baseline activa.

## Límites permanentes

M399.6 permanece:

- sin `apply`, aprobación automática o rollback;
- sin `git apply` ni patch sobre el árbol operativo;
- sin shell libre;
- sin modificación de la baseline activa;
- sin background o monitorización residente;
- sin generación autónoma de correcciones;
- sin automodificación silenciosa.

La regla epistemológica sigue vigente:

**predicción ≠ certeza**

Una proof reproducida y un sandbox con tests verdes aumentan la evidencia técnica de una propuesta, pero no prueban causalidad ni sustituyen la decisión humana.
