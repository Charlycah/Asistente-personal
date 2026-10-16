# ROBY XI.2 — Long-Horizon Investigation A2 → E2 Execution Surgical Reconciliation

## Baseline
Official incoming baseline: 13,643 PASS + Ruff clean (user-certified).

The user-corrected import ordering for
`tests/architecture/test_long_horizon_investigation_p2_to_a2_authorization_green.py`
is integrated byte-for-byte before this reconciliation.

## Finding
The canonical step-2 Execution owner already exists and is directly compatible with the
exact A2 Authorization re-entry preserved by the certified long-horizon P2 → A2 block:

- `GovernedLongHorizonInvestigationA2AuthorizationReentryV1` preserves the exact historical
  `GovernedInvestigationAuthorizationReentryResult` in `result.authorization_reentry`.
- `GovernedMultiStepInvestigationExecutionReentryV1.consume(...)` already accepts exactly
  `GovernedInvestigationAuthorizationReentryResult` plus explicit `now`.
- That historical owner already validates canonical `AUTHORIZED`, exact execution
  eligibility, a single A2 lineage, step 2, one remaining acquisition, the exact P2 planning
  product and the exact A2 authorization product before executing.
- It delegates execution to the existing `GovernedLevel2ReadOnlyExecutionGatewayV1`, whose
  canonical execution path remains `OfficialCapabilityGateway`.
- It validates E2 authorization/R2/P2/source/snapshot lineage and rejects reuse of an existing
  episode execution id.
- Crucially, it also records the E2 envelope through the existing
  `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_acquisition(...)`. Therefore E2
  execution and its episode acquisition recording are already one governed historical owner
  operation for step 2.
- A successful E2 consumes the second and final acquisition slot, leaves the episode in
  `AWAITING_REENTRY`, and exposes reasoning-reentry eligibility without invoking Reasoning.

Therefore there is no architectural gap in Execution itself and no second executor or episode
admission authority is needed. The remaining long-horizon gap is only governed wiring from the
exact A2 admission carrier into that existing E2 owner while retaining
thread/checkpoint/originating-reasoning lineage.

## Correct cut
`exact canonical A2 + eligible_for_existing_execution`
→ validate exact long-horizon A2 admission and historical A2 re-entry identity/lineage
→ existing `GovernedMultiStepInvestigationExecutionReentryV1.consume(exact_A2, now=now)` once
→ preserve the exact existing E2 re-entry result, evidence envelope and resulting episode state
→ expose existing reasoning-reentry eligibility only for recorded `ACQUIRED` E2
→ STOP before second Reasoning re-entry / terminal closure.

## Why not reuse the earlier generic long-horizon Execution adapter
`governed_long_horizon_investigation_evidence_execution` belongs to the earlier
resume → generic evidence-planning → generic authorization path. It invokes the Level-2 gateway
but intentionally does not record the acquired envelope into a live multistep episode.

At step 2 we already possess the exact live episode state through the specialized P2/A2 chain,
and `GovernedMultiStepInvestigationExecutionReentryV1` already owns both the single E2 execution
and its canonical episode acquisition recording. Routing A2 through the earlier generic adapter
and then through another episode-admission bridge would duplicate wiring and weaken the
specialized step-2 invariants.

## Required fail-closed rules
The long-horizon bridge must reject before E2 when the A2 admission is not `AUTHORIZED`, is not
`eligible_for_existing_execution`, lacks the exact historical `authorization_reentry`, does not
preserve `MAY_INITIATE`, is not step 2 with one acquisition remaining, or breaks
thread/episode/R2/P2/A2/source/snapshot/continuation/state lineage.

The exact `authorization_result.authorization_reentry` object is the only object that may be
forwarded to the existing E2 owner, at most once, together with the caller-supplied explicit
`now`.

After invocation, the bridge must preserve the exact historical E2 result. A successful outcome
is trusted only when the existing owner returns `ACQUIRED`, an exact acquired evidence envelope,
one execution invocation, one episode-record invocation, `AWAITING_REENTRY`, zero remaining
acquisitions, and exact A2/P2/R2/source/snapshot lineage. Only then may
`eligible_for_existing_reasoning_reentry=True` be exposed.

Canonical `STOPPED` or `REVIEW_REQUIRED` E2 outcomes remain stopped/review outcomes and never
become reasoning-eligible. Any exception or structurally inconsistent returned E2 is
`REVIEW_REQUIRED`; no retry is allowed.

## Hard boundary
No new Execution authority; no direct Level-2 gateway call from the long-horizon bridge; no reuse
of the earlier generic long-horizon Execution adapter; no separate episode acquisition admission;
no Reasoning re-entry, reasoning closure, Planning, Authorization, requirement production,
Curiosity, Conversation, Memory/World Model mutation, persistence, retry, scheduler, subprocess,
networking or background process.

## Next residual
Only after this cut is GREEN and certified:
`exact recorded E2 + eligible_for_reasoning_reentry → surgical reconciliation of second reasoning re-entry / terminal fixed-budget closure`.
