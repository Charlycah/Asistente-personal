# ROBY XI.2 — Official Desktop Same-Turn Visual Composition Root Binding
## CONTRACT RED

## Owner-certified starting state

PRE-RED baseline:

- 13,467 tests passed;
- 0 tests failed;
- Ruff clean.

Certified residual:

`APPLIED_CONVERSATIONAL_INTELLIGENCE_OWNER_TURN_INTERCEPTOR`

## Protection discovered before RED

`app/official_conversation_gateway.py` is protected by an existing exact-hash
architecture contract.

Certified SHA-256:

`0f8896575116a7ebaac908486d897e22c2f6adff59a05b3cc2997d028b5e0b11`

Therefore this RED does not require surgery inside the protected gateway file
and does not update its historical hash.

The owner-turn interceptor contract is expressed as additive composition over
the canonical gateway instance.

The composition may call existing gateway capabilities but may not instantiate
another gateway or source authority.

## RED contract

The missing module is:

`app.applied_conversational_intelligence_owner_turn_composition`

It must expose:

- immutable `AppliedConversationalOwnerTurnResult`;
- `AppliedConversationalIntelligenceOwnerTurnComposition`;
- `compose_applied_conversational_owner_turn`.

The contract fixes exclusive execution.

### Recognized request

For an eligible recognized text request:

1. interpret once through the existing gateway;
2. execute the existing applied bridge once;
3. do not call normal `gateway.submit`;
4. create the canonical same-turn `LocalConversationTurn`;
5. retain the exact applied result for presentation.

### Non-recognized request

For an unrecognized request:

1. interpret once;
2. do not execute the applied bridge;
3. call normal `gateway.submit` once;
4. expose no applied companion result.

### Explicit-selection precedence

If any current-turn explicit context is present:

- document ids;
- sources;
- evidence references;
- integrated visual context;

the composition must not probe or execute applied intelligence.

It delegates directly to the normal owner-turn path once.

## Preserved contracts

`LocalConversationTurn` fields remain unchanged.

The certified gateway file remains byte-identical.

No visual identity may be parsed from response text.

No new gateway, brain, source executor, controller, worker, dispatcher, or
main loop may be created.

## Separate residuals

The RED does not add:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

or:

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

No `mostrame fotos` or `ultimas` behavior belongs here.

## Expected RED

The new contract file contains 12 tests.

Expected result after M361 regeneration:

- 10 expected RED failures;
- 2 new preservation tests pass;
- M361: 5 pass.

The failures must be attributable only to the missing additive composition.

No productive implementation is included.

## Status

`SAME_TURN_VISUAL_COMPOSITION_ROOT_BINDING_CONTRACT_RED:
DELIVERED / PENDING OWNER CERTIFICATION`

`PROTECTED GATEWAY HASH: PRESERVED`

`EXPECTED CONTRACT RED: 10 FAIL`

`PRODUCTIVE IMPLEMENTATION: ABSENT BY DESIGN`

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION: CONTRACTUALLY FIXED`

`NEW COGNITIVE/SOURCE AUTHORITY: NONE`

`SURGICAL GREEN: NOT YET AUTHORIZED`

STOP for Owner local certification.
