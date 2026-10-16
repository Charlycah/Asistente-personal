# ROBY XI.2 — Probe B1-S8A
## ROBY-Initiated Unique-Candidate Regression — Surgical Reconciliation

Status: RECONCILED — no productive change authorized in this increment.

## Baseline

This reconciliation starts from the B1-S8 Surgical GREEN that converted the
three B1-S7 same-request catalogue-reuse contracts to GREEN but exposed three
pre-existing CAP-17 ROBY-initiated unique-candidate regressions in the full
local suite.

## Observed regression

The three affected contracts are:

- `test_cap17_unique_candidate_preserves_provenance`
- `test_cap17_unique_candidate_uses_existing_unified_runtime`
- `test_cap17_roby_initiated_decision_is_one_shot_not_reused`

All three reach the unique-candidate path but the conversation result becomes
`failed` instead of `completed`.

## Exact seam

`GovernedLocalLibraryConversationV1` accepts a library object and passes that
same object to `GovernedLocalDocumentRetrieverV1`.

The pre-existing ROBY-initiated CAP-17 contract uses `CountingLibrary`, a
transparent test double around `GovernedLocalLibraryCatalogueV1`. Its exposed
library surface is:

- `search(...)`
- `catalogue()`
- `resolve_entry(...)`

B1-S8 changed `GovernedLocalDocumentRetrieverV1._validate_selection()` from
validation through the previously available surface to an unconditional call
to:

`self._library.validate_selected_entry(...)`

`CountingLibrary` does not expose that newly required method. The unified
retrieval execution converts the resulting retrieval failure into an execution
without an artifact; the conversation therefore reports `failed`.

This is an interface/substitutability regression introduced by B1-S8. It is
not evidence that provenance, unified runtime, one-shot initiation, EPUB
reading, query admission, or the catalogue-reuse objective are themselves
incorrect.

## Architectural finding

The point-validation algorithm added in B1-S8 belongs to the existing
`GovernedLocalLibraryCatalogueV1` authority and must not be duplicated in the
retriever or in a parallel helper/manager.

At the same time, B1-S8 expanded the retriever's required collaborator surface
without reconciling the already-supported library substitution used by the
ROBY-initiated CAP-17 path. A surgical GREEN must preserve both properties:

1. point validation remains owned by the canonical catalogue authority; and
2. the established conversation/retrieval collaborator contract remains
   substitutable without forcing a second full catalogue traversal.

No cache, index, new manager, new authority, second validation implementation,
or weakening of stale/provenance checks is justified by this reconciliation.

## Evidence

Focused execution of the three affected pre-existing contracts on the B1-S8
baseline reproduces exactly three failures: each expected `completed` and
received `failed`.

Source inspection shows that the test collaborator delegates catalogue/search
operations to the canonical `GovernedLocalLibraryCatalogueV1` but lacks
`validate_selected_entry`, while B1-S8's retriever now invokes that method
unconditionally.

## Classification

- B1-S7 same-request catalogue-reuse target: GREEN.
- B1-S8 directed contracts: GREEN.
- B1-S8 full regression gate: RED.
- B1-S8A exact regression seam: DEMONSTRATED.
- Root cause class: collaborator interface/substitutability expansion.
- CAP-17 catalogue authority: remains canonical.
- Product change in B1-S8A: NONE.
- CONTRACT RED: not required for the already failing pre-existing contracts.
- B2/B3/B4: STOP.

## Authorized next increment

`Probe B1-S8B — Library Validation Collaborator Compatibility — SURGICAL GREEN`

The GREEN must be the smallest change that restores the three pre-existing
ROBY-initiated unique-candidate contracts while retaining all three B1-S7
same-request reuse contracts and the canonical point-validation authority.

STOP before any broader optimization or Probe B2/B3/B4.
