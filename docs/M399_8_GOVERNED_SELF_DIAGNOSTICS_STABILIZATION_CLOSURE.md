# M399.8 — Governed Self-Diagnostics Stabilization & Closure

## Closure purpose

M399.8 performs the final integration and governance audit for **M399 — Governed
Self-Diagnostics & Self-Maintenance**. It adds no new diagnostic capability, repair
mechanism, runtime authority or automatic application path. Its only purpose is to
prove that M399.2 through M399.7 form one governed, traceable and human-controlled
self-diagnostics chain.

M399.1 remains the audited Current Location prerequisite that opened the stage, but
M399.8 closes the Self-Diagnostics body implemented from M399.2 through M399.7.

## Pre-closure baseline

The M399.7 working baseline reached **10,910 pytest tests** with no functional
failures. The final M399.7 import-order correction is incorporated before this
closure. Formal closure still requires M361 regeneration, Ruff clean and the
complete pytest suite on M399.8.

## Permanent closure invariants

- **M399-C00 — One diagnostic authority.** `GovernedSelfDiagnostics` remains the
  unique technical authority `self_diagnostics`; no second manager, engine or brain
  is introduced.
- **M399-C01 — Source authorities remain owners of observations.** M399 normalizes
  explicit evidence but does not replace provider health, runtime readiness,
  cognitive diagnostics or other source authorities.
- **M399-C02 — Observation precedes inference.** No hypothesis may exist without an
  explicit diagnostic report and an observed anomaly.
- **M399-C03 — Prediction is not certainty.** Confidence and reproduced proof never
  become causal truth.
- **M399-C04 — Evidence is traceable.** Hypotheses, confidence and proof preserve
  explicit observation identities and evidence digests.
- **M399-C05 — Proof means reproducibility only.** A reproduced diagnostic proof
  confirms deterministic reassessment, not causal certainty.
- **M399-C06 — Proposals are isolated and inert.** Proposal artifacts remain under
  `.roby/review/proposals/` and do not authorize code changes.
- **M399-C07 — Sandbox is isolated.** Candidate files are tested only inside the
  governed sandbox copy; the operational baseline is not modified.
- **M399-C08 — Test execution is bounded.** Sandbox execution is restricted to
  explicit safe pytest paths declared by the proposal.
- **M399-C09 — Diff is review evidence, not executable mutation.** Unified diffs are
  generated for explanation and review only.
- **M399-C10 — Human decision is mandatory and separate.** Review decisions require
  explicit reviewer, decision and explanation.
- **M399-C11 — Approval is not application.** Even an approved review does not apply
  code, patch, rollback or repair.
- **M399-C12 — No silent self-modification.** M399 contains no automatic application,
  repair, rollback, auto-approval or operational code mutation path.
- **M399-C13 — Closure is hash-audited and quality-gated.** The complete
  `core/self_diagnostics` package is frozen in the M399.8 closure manifest and final
  closure requires M361 regeneration, Ruff clean and the complete pytest suite.

## Closed governed chain

The closed path is:

**Observación → tendencia → anomalía → hipótesis → confianza → evidencia → prueba
reproducible → propuesta aislada → sandbox → tests → diff → explicación → decisión
humana**

The chain deliberately ends at human decision. There is no automatic application
step inside M399.

## Scope closed by M399

M399 now provides governed technical self-observation, deterministic trend and
anomaly detection, candidate hypothesis assessment, explainable confidence,
reproducible proof, isolated proposals, sandbox validation, inert diffs and explicit
human review records.

## Explicitly outside the closure

M399 does not perform automatic repair, automatic patch generation/application,
auto-approval, silent rollback, autonomous code mutation, unrestricted shell
execution or background self-maintenance. Any future capability that changes
operational code must open a new governed stage with explicit human authorization
rules and must not bypass the M399 evidence/review boundary.

## Formal closure statement

When M399.8 passes M361 regeneration, `ruff check .` and the complete `pytest -q`
suite, **M399 — Governed Self-Diagnostics & Self-Maintenance is CLOSED**. Future
self-maintenance evolution must open a new stage rather than creating M399.9 for new
capability work.
