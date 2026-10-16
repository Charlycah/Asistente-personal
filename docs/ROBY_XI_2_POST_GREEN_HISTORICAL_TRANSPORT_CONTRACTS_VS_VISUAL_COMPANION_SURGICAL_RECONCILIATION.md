# ROBY XI.2 — Historical Transport Contracts vs Visual Companion
## SURGICAL RECONCILIATION

## Certified input

The input is the Owner-executed visual root binding GREEN plus the
Owner-supplied corrected `desktop_ui.py`.

Owner evidence reported:

- Ruff initially found only import ordering in `desktop_ui.py`;
- after the supplied correction, Ruff is clean;
- full suite: 13,501 passed / 3 failed;
- two failures are historical Desktop transport assertions;
- one failure is M361 snapshot reproducibility.

## Owner-supplied desktop correction

The supplied file is integrated in this reconciliation.

Compared with the delivered GREEN, its changes are formatting only:

- corrected import ordering;
- compacted already-existing calls without semantic change;
- no owner-turn, source, visual, cognitive or presentation behavior changed.

No line exceeds 88 characters.

## Historical contract 1 — unified attachment re-entry

The LX1-S3E2D contract proves that an explicitly selected document re-enters
existing turn transport.

Its durable behavioral obligations are:

- the Desktop exposes the existing unified attachment control;
- document admission reuses existing governed boundaries;
- `explicit_document_ids` reaches the ordinary turn transport;
- no archive extraction or reasoning authority is created in the Desktop.

The assertion requiring the literal text `self.controller.submit(` is an
implementation-name anchor, not the durable authority boundary.

The current GREEN still forwards `explicit_document_ids` through the existing
Desktop controller. The method is now `submit_with_visual_companion` so the
same owner turn can also return the exact gateway-owned applied result.

Therefore the behavioral contract survives while its literal method-name
anchor is stale.

## Historical contract 2 — four-source single deliberation

The certified LX1-S6-C documentation states that an ordinary Desktop turn
carries all four explicit source channels through exactly one existing
Desktop controller call and then through one adapter submission into canonical
Reasoning.

The durable invariant is:

`FOUR SOURCE CHANNELS -> ONE CONTROLLER TURN -> ONE ADAPTER TURN -> ONE REASONING`

It is not:

`THE CONTROLLER METHOD MUST FOREVER BE NAMED submit`

The visual GREEN replaces the worker call with
`submit_with_visual_companion`, but that method is still owned by the existing
`DesktopConversationController` and the repaired visual contract requires one
owner-turn execution.

The four explicit channels remain forwarded in that single call.

Therefore the S6-B test helper that recognizes only an attribute named
`submit` is now syntactically stale while the certified single-deliberation
invariant remains authoritative.

## M361 reproducibility failure

The M361 generator derives static repository metrics from the current Python
tree.

The committed snapshot was stale after the legitimate productive GREEN.
Regenerating it from the current tree is deterministic and restores the
reproducibility contract.

This reconciliation regenerates M361 after integrating the Owner-supplied
formatting correction.

Focused verification after regeneration:

- historical attachment + S6-B + M361 set: 13 passed / 2 failed;
- the two remaining failures are exactly the stale literal controller-method
  anchors described above;
- all M361 tests pass.

## Decision

The two historical tests must not be deleted, weakened or mechanically made
green.

Their next governed treatment is a narrow semantic contract migration:

1. preserve all attachment and four-source behavioral obligations;
2. recognize the existing controller visual-companion seam as the current
   owner-turn transport;
3. continue proving exactly one controller call;
4. continue proving all four explicit source channels are forwarded together;
5. continue proving one adapter submission and no parallel reasoning;
6. add no new authority and make no productive change.

The migration is test-only plus documentation.

## Status

`SURGICAL_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`

`OWNER-SUPPLIED DESKTOP_UI: INTEGRATED`

`DESKTOP_UI SEMANTIC DELTA FROM GREEN: ZERO`

`M361 SNAPSHOT: REGENERATED`

`M361 REPRODUCIBILITY: GREEN LOCALLY`

`HISTORICAL CONTRACTS: BEHAVIOR VALID / METHOD-NAME ANCHORS STALE`

`NEXT STEP: HISTORICAL TRANSPORT CONTRACT SEMANTIC MIGRATION — CONTRACT REPAIR`

`NEW AUTHORITY: NONE`

STOP before test migration.
