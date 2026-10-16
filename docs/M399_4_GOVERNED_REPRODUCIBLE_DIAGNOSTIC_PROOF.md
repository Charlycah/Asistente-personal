# M399.4 — Governed Reproducible Diagnostic Proof

M399.4 extiende Self-Diagnostics desde **evidencia → prueba reproducible** sin cambiar
la autoridad canónica `self_diagnostics`.

La prueba reproducible no prueba causalidad. Congela una hipótesis candidata explícita,
su política de confianza y un digest SHA-256 de la evidencia diagnóstica utilizada para
que el mismo diagnóstico pueda repetirse de forma determinista y de sólo lectura.

Resultados posibles:

- `reproduced`: la misma evidencia reproduce nivel y score de confianza;
- `not_reproduced`: cambió evidencia, métrica, autoridad o resultado;
- `inconclusive`: la reproducción ya no satisface las precondiciones diagnósticas.

Invariantes permanentes:

- **predicción ≠ certeza**;
- una prueba reproducida **no prueba causalidad** ni convierte una hipótesis en hecho;
- no genera hipótesis nuevas;
- no escribe ni modifica código, configuración, memoria operativa o runtime;
- sin proposals, sandbox, patch, diff, apply, rollback o reparación;
- no ejecuta comandos ni monitorización residente;
- toda evidencia permanece atribuida a su autoridad original.

M399.4 prepara el terreno para una futura propuesta aislada, pero esa capacidad no
pertenece a este incremento.
