# ROBY XI.2 — CAP-07 Productive Abstraction Admission — GREEN-1 → GREEN-4

**Authority:** `governed_reasoning`  
**Scope:** isolated admission core; no composition-root wiring.  
**Persistence:** none.  
**Automatic Learning:** none.  
**Automatic Structural Transfer:** none.

## Implemented

- Frozen governed admission/result/episode contracts.
- Normalization from already-certified contextual semantic grounding only.
- Bounded, session-local, scope-isolated accumulation.
- Idempotence by grounding fingerprint.
- Selective reuse of the existing `GovernedRelationalAbstractionInducer` after minimum support.
- Deterministic abstraction/episode identity for the same admitted evidence set.

## New implementation anchor

`core/governed_reasoning/productive_abstraction_admission.py`

## New contractual test

`tests/architecture/test_cap_07_productive_abstraction_admission_green_1_4.py`

## Preserved boundaries

The component does not read arbitrary free text, does not add another semantic grounder or abstraction engine, does not write Memory or Learning, does not register inference rules, does not call Structural Transfer, and is not yet instantiated by the productive composition root.

## Current residual

GREEN-1 → GREEN-4 closes the isolated admission core but **does not yet make relational abstraction productively reachable**. The next decision point is gateway/composition integration and read-only productive consumption, corresponding to GREEN-5 → GREEN-7 after a focused wiring audit.

## Local verification in the implementation environment

- New GREEN-1 → GREEN-4 suite: **8 PASS**.
- New suite plus existing CAP-07/CAP-08 focused perimeter: **41 PASS**.
- Ruff is not installed in the implementation environment; local `ruff check .` remains a promotion gate.
