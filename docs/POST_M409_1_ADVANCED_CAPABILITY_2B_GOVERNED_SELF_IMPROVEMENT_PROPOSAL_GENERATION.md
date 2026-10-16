# ROBY XI.2 — Advanced Capability 2B

## Governed Self-Improvement Proposal Generation

Estado: implementación mínima subordinada.

Cadena autorizada:

`reproduced diagnostic proof → hash-bound project evidence → DiagnosticProposalRequest → M399.5 existing isolated proposal pipeline`

`GovernedSelfDiagnostics` / `self_diagnostics` conserva la única autoridad diagnóstica. Esta etapa no modifica el paquete congelado `core/self_diagnostics`, no crea authority, manager, engine, planner ni cerebro paralelo.

La generación sólo acepta una prueba M399.4 con estado `REPRODUCED` y evidencia explícita de archivos del proyecto enlazada por SHA-256. Los archivos afectados deben existir, los tests de validación deben ser tests existentes y cualquier divergencia de digest falla cerrada.

La intención de cambio se genera de forma determinista y acotada desde `source_authority`, `metric`, proof y archivos respaldados por evidencia. No se afirma causalidad: **reproduced diagnostic proof ≠ causal truth**.

Quedan protegidos por defecto `core/self_diagnostics/`, documentación constitucional, quality manifests y superficies de authority/permission/consent. Esta etapa no puede proponer cambios ordinarios sobre esas fronteras.

No hay escritura de código operativo, patch, apply, approval, auto-approval, rollback, Memory/Learning/world-model mutation, acción, background ni authority gain. El resultado es únicamente un `DiagnosticProposalRequest` inerte que reutiliza M399.5 y sigue requiriendo revisión humana antes de cualquier cambio.

## Closure hardening

The subordinate producer now enforces an explicit bounded proposal scope: at most four affected files and eight validation tests per candidate. Wider requests fail closed and must be decomposed or handled through a separate governed review.

Protected-scope enforcement now covers the self-improvement producer itself, the frozen `core/self_diagnostics/` package, unified permission/consent surfaces, quality certification artifacts, root constitutional/governance documents, and files whose names identify authority, approval, permission, consent, constitution, governance, self-diagnostics, self-improvement, or quality-baseline responsibilities. Hash validity never overrides those exclusions.

These guards do not add an authority, do not alter M399, and do not authorize proposal application.

