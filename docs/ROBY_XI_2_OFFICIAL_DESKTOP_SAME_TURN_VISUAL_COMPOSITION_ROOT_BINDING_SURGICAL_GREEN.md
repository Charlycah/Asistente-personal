# ROBY XI.2 — Official Desktop Same-Turn Visual Composition Root Binding
## SURGICAL GREEN

## Owner-certified RED

Starting state:

- existing baseline: 13,467 pass;
- RED total: 13,469 pass;
- expected RED failures: 10;
- Ruff clean;
- unexpected regressions: 0.

The protected `app/official_conversation_gateway.py` remains byte-identical.

## RED-to-GREEN semantic reconciliation

Before implementation, the production gateway showed an important fact:

`execute_applied_conversational_intelligence` already performs
`interpret_applied_conversational_intelligence` internally.

Therefore a recognized path that first interpreted and then called the bridge
would interpret twice.

The RED fixture was reconciled to the real certified bridge semantics:

- no explicit context: execute the applied bridge once;
- the bridge performs interpretation once internally;
- recognized result: build the same-turn applied owner-turn result;
- not recognized: delegate once to normal `gateway.submit`;
- explicit context: do not probe the applied bridge and delegate once.

This changes no productive authority and prevents duplicated interpretation.

## Productive implementation

Added:

`app.applied_conversational_intelligence_owner_turn_composition`

It exposes:

- immutable `AppliedConversationalOwnerTurnResult`;
- `AppliedConversationalIntelligenceOwnerTurnComposition`;
- `compose_applied_conversational_owner_turn`.

The composition receives the existing gateway instance.

It does not instantiate:

- another gateway;
- another brain;
- another source executor;
- another controller;
- another worker;
- another dispatcher.

## Recognized path

For a recognized applied result:

- applied bridge: once;
- normal `gateway.submit`: zero;
- answer text: exact governed applied answer;
- applied result: retained by exact object identity;
- `LocalConversationTurn`: existing contract, unchanged;
- response path: interceptor.

No URL or visual identity is parsed from response text.

## Non-recognized path

For an unrecognized applied result:

- applied bridge: once;
- interpretation inside that bridge: once;
- normal `gateway.submit`: once;
- applied companion: absent.

No governed source query occurs when interpretation returns no request.

## Explicit-selection precedence

If the turn carries any:

- explicit document ids;
- explicit sources;
- explicit evidence references;
- integrated visual context;

the composition bypasses the applied probe and delegates directly to the
normal owner-turn path once.

## Scope boundary

This GREEN establishes the additive owner-turn composition contracted by RED.

It does not yet claim productive desktop-bootstrap reachability.

It also does not mutate gateway-private accounting or observer state.

POST-GREEN must reconcile whether the official composition root can consume
this additive result while preserving the gateway's existing submitted-turn
accounting and observer/evidence completion semantics.

No private accounting mutation is introduced here merely to simulate gateway
ownership.

## Preserved protected files

`app/official_conversation_gateway.py` remains at certified SHA-256:

`0f8896575116a7ebaac908486d897e22c2f6adff59a05b3cc2997d028b5e0b11`

Historical hash protections are not updated.

## Validation

Focused GREEN and nearby gateway/applied contracts:

- 30 passed;
- 0 failed.

M361 is regenerated before packaging.

New and reconciled files have no lines over 88 characters.

## Separate residuals

Remain outside this GREEN:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

No `mostrame fotos` or `ultimas` behavior is added.

## Status

`SAME_TURN_VISUAL_COMPOSITION_ROOT_BINDING_SURGICAL_GREEN:
DELIVERED / PENDING OWNER CERTIFICATION`

`CONTRACT RED -> GREEN: 10 FAIL -> 10 PASS`

`PROTECTED GATEWAY: BYTE-IDENTICAL`

`ONE OWNER TURN -> ONE GOVERNED EXECUTION BRANCH: PRESERVED`

`EXPLICIT SELECTION PRECEDENCE: PRESERVED`

`NEW COGNITIVE/SOURCE AUTHORITY: NONE`

STOP for Owner local certification.
