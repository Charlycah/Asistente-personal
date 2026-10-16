# ROBY XI.2 — GREEN: exact recorded E2 → RR2 terminal closure

Incoming certified baseline: **13,656 PASS + Ruff clean**.

## Implemented governed cut

`GovernedLongHorizonInvestigationRR2TerminalClosureV1` accepts only the exact certified
long-horizon E2 admission that already preserves a canonical recorded step-2 execution.
It forwards the same `execution_reentry` object and the caller-supplied `now` exactly once
to the existing `GovernedMultiStepInvestigationReasoningClosureV1` owner.

No new Reasoning authority, episode authority, planner, authorizer, executor, requirement
producer, retry loop, persistence layer, Memory/World Model mutation, conversation output,
curiosity path, or background process is introduced.

## Success invariant

Success is accepted only when the existing owner returns its exact canonical terminal
closure with:

- one RR2 invocation;
- one episode `record_reentry`;
- new RR2 lineage relative to prior reentries;
- exact E2/A2/P2/R2/source/snapshot/episode lineage;
- episode status `CLOSED`;
- stopping reason `BUDGET_EXHAUSTED`;
- `remaining_acquisitions == 0`.

The exact canonical `GovernedInvestigationReasoningClosureResult`, RR2 product and terminal
episode state are preserved by identity.

## Fail-closed behavior

Ineligible or forged E2 fails before the historical closure owner. Owner exceptions,
non-CLOSED canonical results, identity mismatch, reused RR2, or terminal lineage mismatch
become `REVIEW_REQUIRED` without retry or trusted terminal projection.

## Mandatory terminal cut

The resulting long-horizon product exposes no eligibility for R3/P3/A3/E3 and cannot create
a requirement, invoke curiosity, retry, persist, mutate Memory/World Model, emit conversation,
or start background work.

This GREEN closes the fixed two-acquisition long-horizon episode rather than extending the
horizon. Any future horizon deepening must be separately reconciled at the governed episode
policy level; it must not reopen this terminal product implicitly.
