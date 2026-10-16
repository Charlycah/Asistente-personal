# ROBY XI.2 — POST-B1-S8B HISTORICAL GUARD RECONCILIATION

**Classification:** DOCUMENTARY GREEN / CLASS 0  
**PRODUCT_CHANGE: NONE**  
**TEST_REWRITE: NONE**  
**Authority change:** NONE  
**New capability:** NONE

## 1. Purpose

Close the documentary precedence gap demonstrated after B1-S8B without changing
productive behavior or rewriting historical guards merely to obtain a green full suite.

Historical byte guards remain historical evidence. Current governed truth requires its
own explicit contract.

## 2. Configuration guard classification

The Gate5-era protected `.roby/config.json` baseline is:

`11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5`

Classification: `HISTORICAL_BASELINE`.

The current deployment configuration is:

`0d61f2ec940f87939d32b9bad27150de857cca535cd2f4a405dfdacc0422a451`

Classification: `CURRENT_GOVERNED_DEPLOYMENT_STATE`.

The current configuration contains the governed deployment projection for
`ROBY_LOCAL_LIBRARY_ROOT`. CAP-17 Productive Runtime Wiring authorizes consumption of
that configured root but did not authorize mutating `.roby/config.json`. The exact
byte-transition provenance therefore remains historical deployment provenance rather
than a CAP-17 Productive Runtime Wiring product change.

`NO_SILENT_REANCHOR`: the Gate5 historical hash must not be silently replaced with the
current hash merely to make historical tests pass.

## 3. Desktop guard classification

The historical Desktop guard is:

`475d9fca8ac05946936410a5b98e056ee70b945b9c6398e52842106e98929cec`

The current governed Desktop state is:

`60a70c140370a43843854b99f788df4701e31e26ae522d7088bb8391990476f6`

LX1 POST-S6-C H5 reconciliation already records that S6-C legitimately changed
`app/desktop_ui.py` and explicitly refuses restoration merely to satisfy historical
hash expectations.

Classification: `DO_NOT_REVERT_PRODUCT`.

## 4. Capability registry guard classification

Productive CAP-17 legitimately registers the canonical
`knowledge.local_library.read` capability in the existing official runtime registry.

Older positional and whole-tuple expectations that predate that registration are
classified as `HISTORICAL_ORDER_EXPECTATION`.

Classification: `DO_NOT_REORDER_REGISTRY`.

The registry must not be reordered, capability registration removed, or productive
composition changed merely to satisfy those historical positional assumptions.

## 5. Precedence rule

The governed rule is:

`historical byte guards remain historical evidence`

and:

`current governed truth requires its own explicit contract`

Historical contracts remain evidence of the baseline they originally protected. A
later governed transition does not retroactively falsify that baseline, and an old
guard does not gain authority to revert a later governed state.

Any future reconciliation of the twelve historical failing contracts requires its own
explicit scope and evidence. This documentary GREEN does not rewrite them.

## 6. B1-S8B boundary

B1-S8B remains outside these historical residuals. Its surgical correction does not
modify `.roby/config.json`, Desktop historical semantics, or capability-registry order
for the purpose of satisfying old guards.

No new B1 product change is authorized here.

## 7. STOP

PRODUCT_CHANGE: NONE  
TEST_REWRITE: NONE  
B2: STOP  
B3: STOP  
B4: STOP

This block closes only the missing documentary precedence register. It stops before
any historical-test reconciliation or further Probe B execution.
