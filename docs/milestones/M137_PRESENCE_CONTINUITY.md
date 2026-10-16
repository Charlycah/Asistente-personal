# M137 — Presence Continuity

## Objective
Evaluate anonymous temporal continuity across governed M136 presence-understanding results without identifying, counting, or tracking individuals.

## Inputs
- Two or more `PresenceUnderstandingResult` samples from M136.
- A declared continuity-evaluation request.

## Output
- Immutable `PresenceContinuityResult`.

## Responsibilities
- Validate owner and exact M134 ambient-context lineage across M136 samples.
- Filter non-understood, weak, stale, future, or duplicate samples.
- Order accepted samples deterministically by governed timestamp.
- Distinguish stable continuity, state transition, and temporal interruption.
- Classify coarse anonymous transitions as arrival, departure, occupancy change, transient change, or uncertain change.
- Persist the result through an abstract repository contract.

## Continuity semantics
M137 compares only coarse ambient presence states produced by M136. Continuity means that the latest governed samples preserve the same anonymous state within the configured temporal gap. A transition records a change between coarse states. An interruption records that the temporal gap is too large to claim continuity.

These semantics do not imply that the same person remained present, arrived, departed, or moved. They describe only anonymous ambient-state evolution within one governed context lineage.

## Explicit exclusions
M137 does not access sensors, identify people, perform biometrics, count individuals precisely, correlate identities, reconstruct trajectories, track individuals or movement, infer activity, execute automation, call providers, or mutate platform state.

## Architectural result
M137 extends the governed chain M134 → M135 → M136 → M137 with a dedicated temporal layer. Presence understanding remains separate from continuity evaluation, and continuity remains anonymous, deterministic, provider-neutral, and safe for later Ambient Context integration.
