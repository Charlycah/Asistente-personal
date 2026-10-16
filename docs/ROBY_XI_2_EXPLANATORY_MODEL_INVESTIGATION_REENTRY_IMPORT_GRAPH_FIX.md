# ROBY XI.2 — Investigation Re-entry Import Graph Fix

**Entry state:** functional block with 13,513 PASS + 1 architectural import-cycle failure;
Ruff clean in user validation.

## Failure

The deep architectural audit detected this production cycle:

`governed_explanatory_model_investigation_reentry`
→ `governed_level2b_productive_entry`
→ `governed_multistep_investigation_episode`
→ `governed_level2_reasoning_reentry`
→ `governed_reasoning_runtime`
→ `governed_explanatory_model_investigation_reentry`.

## Correction

No functional contract or test was weakened.

`governed_level2_reasoning_reentry` no longer imports the concrete official runtime
class. The re-entry foundation only requires the structural runtime contract it
actually uses: an `orchestrator` attribute and a callable `reason` operation.

This removes the reverse dependency from the historical re-entry adapter back to the
top-level runtime and restores the directed production graph.

## Preserved semantics

- same governed reasoning gateway instance remains accepted;
- same evidence registration and one-shot reasoning re-entry;
- same investigation lifecycle;
- same explanatory-model discrimination re-entry;
- no new authority;
- no planning/execution bypass;
- no Memory/Learning/World Model changes.

## Focused validation

The exact global import-cycle test plus the explanatory re-entry and historical
Level-2/multi-step reasoning re-entry perimeter: **76 PASS**.

`py_compile` passed and the modified Python file has no lines over 88 characters.

Official promotion remains gated by local `ruff check .` and full `pytest -q`.
Expected full result: **13,514 PASS + Ruff clean**.
