# ROBY XI.2 — Official Desktop Visual Runtime Composition
## SURGICAL GREEN

## Owner-certified starting state

The CONTRACT RED is Owner-certified:

- 13,457 existing tests passed;
- 10 expected contract failures;
- 0 unexpected regressions;
- Ruff clean.

The certified residual is:

`SAME_TURN_GOVERNED_VISUAL_RESULT_EXPOSURE`

## RED-to-GREEN protection reconciliation

The first local GREEN attempt exposed a governance conflict.

A historical architecture contract protects
`app/runtime_ui_adapter.py` by exact byte identity.

Mutating `LocalConversationUIAdapter` made the new RED pass but caused one
historical contract failure.

The protected hash was not updated.

The protected file was restored byte-for-byte.

The RED transport requirement was reconciled to an additive composition around
the protected adapter authority.

This preserves the Owner-certified intent:

- same-turn visual transport exists;
- no second source or cognitive authority exists;
- the protected canonical adapter remains unchanged.

`app/unified_brain.py` was also restored and remains unchanged.

## Surgical implementation

The GREEN adds:

`app.same_turn_governed_visual_result_exposure`

It defines:

- immutable `SameTurnGovernedVisualResult`;
- `expose_same_turn_governed_visual_result`;
- `SameTurnVisualRuntimeComposition`;
- `SameTurnVisualUIAdapterComposition`.

The seam accepts injected existing execution authorities.

It does not instantiate a gateway, brain, source executor, NASA adapter,
controller, worker, scheduler, dispatcher, or main loop.

## Execution semantics

The exposure algorithm is exclusive:

1. call the injected same-turn applied execution once;
2. if it returns an admitted execution, preserve its exact `turn` and
   `applied_result`;
3. do not call fallback;
4. otherwise call the injected normal owner-turn fallback once;
5. return the normal turn with no applied visual result.

Therefore:

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION`

is preserved by the seam.

## Productive transport surfaces

The additive runtime composition exposes:

`process_with_visual_result`

The additive UI composition exposes:

`submit_text_with_visual_companion`

The existing `DesktopConversationController` gains:

`submit_with_visual_companion`

That controller surface consumes the optional composition method when present
and otherwise falls back to its existing `submit` path.

`DesktopMessage` remains unchanged.

`UIResponse` remains unchanged.

`LocalConversationTurn` remains unchanged.

## Important composition boundary

This GREEN does not bind a concrete same-turn applied executor in
`desktop_bootstrap.py`.

Doing so without first proving the correct existing executor would risk a
second governed execution.

Therefore the GREEN supplies the contractually required productive callable
transport surface but does not claim final desktop worker/Tk reachability.

POST-GREEN reconciliation must inspect the composition root before any further
binding.

## Validation

Focused visual architecture contracts:

- 54 passed;
- 0 failed.

Nearby tests touching `UnifiedBrain`, `LocalConversationUIAdapter`, or
`DesktopConversationController`:

- 551 passed;
- 0 failed.

The historical byte-identity protection remains green.

## Preserved exclusions

No second:

- gateway;
- brain;
- source query;
- controller;
- projection;
- companion;
- presenter;
- runtime binding;
- worker;
- scheduler;
- dispatcher;
- main loop.

No generic browser/crawler.

No automatic Vision, repository, Memory, Learning, diagnostics, Proposal,
Planning, or Execution side effects.

## Separate residuals

Still outside scope:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

## Status

`SURGICAL_GREEN: DELIVERED / PENDING OWNER CERTIFICATION`

`RED CONTRACT INTENT: PRESERVED`

`PROTECTED ADAPTER HASH: PRESERVED`

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION: PRESERVED`

`FINAL DESKTOP COMPOSITION ROOT BINDING: NOT CLAIMED`

`POST_GREEN_RECONCILIATION: NOT YET AUTHORIZED`

STOP for Owner local certification.
