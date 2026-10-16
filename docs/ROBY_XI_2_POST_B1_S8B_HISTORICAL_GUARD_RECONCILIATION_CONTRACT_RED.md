# ROBY XI.2 — POST-B1-S8B HISTORICAL GUARD RECONCILIATION — CONTRACT RED

**Classification:** CONTRACT RED / DOCUMENTARY ONLY  
**Product change:** NONE  
**Existing historical test rewrite:** NONE  
**B2/B3/B4:** STOP

## Purpose

Freeze the missing documentary precedence contract between historical byte/order guards
and later governed repository truth. This RED does not authorize changing product,
reverting current governed state, reordering the capability registry, or silently
re-anchoring an old baseline.

## Reconciled evidence

The locally supplied post-B1-S8B full suite reports 12 failures and 13,308 passes.
The same residual classes were already recorded after LX1-S6-C at 12 failures and
13,302 passes: historical/protected hash expectations and historical capability-registry
ordering expectations.

The three residual families are:

1. Seven Gate5-era `.roby/config.json` byte guards still anchored to
   `11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5`,
   while the current deployment configuration is
   `0d61f2ec940f87939d32b9bad27150de857cca535cd2f4a405dfdacc0422a451`.
2. Two historical Desktop guards still anchored to
   `475d9fca8ac05946936410a5b98e056ee70b945b9c6398e52842106e98929cec`,
   while the governed post-S6-C Desktop state is
   `60a70c140370a43843854b99f788df4701e31e26ae522d7088bb8391990476f6`.
3. Three registry tests retain ordering/position assumptions predating productive
   registration of `knowledge.local_library.read`.

## Missing contract

The repository does not yet contain the canonical documentary register that explicitly
preserves each old guard as historical evidence while separately identifying the current
governed state and its governing transition.

The future GREEN for this RED must be documentary. It must not modify product or rewrite
the twelve historical tests merely to make the full suite green.

## Required GREEN semantics

The missing reconciliation document must make these distinctions explicit:

- historical config hash = `HISTORICAL_BASELINE`;
- current config hash = `CURRENT_GOVERNED_DEPLOYMENT_STATE`;
- registry positional assumptions = `HISTORICAL_ORDER_EXPECTATION`;
- legitimate S6-C Desktop divergence = `DO_NOT_REVERT_PRODUCT`;
- current CAP-17 registry composition = `DO_NOT_REORDER_REGISTRY`;
- historical guards may not be changed by `NO_SILENT_REANCHOR`.

It must state verbatim that:

`historical byte guards remain historical evidence`

and:

`current governed truth requires its own explicit contract`

## RED cause

`tests/architecture/test_post_b1_s8b_historical_guard_reconciliation_contract_red.py`
must fail only because
`docs/ROBY_XI_2_POST_B1_S8B_HISTORICAL_GUARD_RECONCILIATION.md` does not yet exist.

No production seam is missing.

## STOP

PRODUCT_CHANGE: NONE  
TEST_REWRITE: NONE  
B2: STOP  
B3: STOP  
B4: STOP

STOP before documentary GREEN.
