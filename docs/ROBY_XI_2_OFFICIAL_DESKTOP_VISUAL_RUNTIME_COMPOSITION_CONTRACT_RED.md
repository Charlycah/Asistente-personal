# ROBY XI.2 — Official Desktop Visual Runtime Composition
## CONTRACT RED

## Certified starting state

Owner-certified PRE-RED baseline:

- 13,455 tests passed;
- 0 tests failed;
- Ruff clean.

Certified missing seam:

`SAME_TURN_GOVERNED_VISUAL_RESULT_EXPOSURE`

## RED purpose

Fix the contract for exposing optional governed visual evidence from the exact
owner turn that produces the desktop text.

This RED adds architecture tests only.

No productive implementation of the seam is included.

## Contract target

The deliberately absent mechanical seam is:

`app.same_turn_governed_visual_result_exposure`

It is not a new source, query, reasoning, controller, or cognitive authority.

It must only preserve the exact turn and optional admitted applied result from
one canonical execution path.

## Contract dimensions

The RED fixes these requirements:

1. same-turn exposure is immutable;
2. a recognized applied path executes once and does not execute fallback;
3. an unrecognized applied path falls through to the normal owner turn once;
4. exact admitted applied-result identity is preserved;
5. visual identity is never parsed from response text;
6. `LocalConversationTurn` remains backward compatible;
7. `UIResponse` remains backward compatible;
8. the exposure seam owns no parallel authority, worker, or main loop;
9. reachability and freshness semantics remain outside this block;
10. `UnifiedBrain` exposes a same-turn visual-result processing surface;
11. `LocalConversationUIAdapter` exposes an optional visual companion transport;
12. `DesktopConversationController` exposes an optional same-turn visual surface.

The last three contracts prevent another isolated foundation from being added
without a productive desktop transport path.

## Execution rule

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION`

For a recognized existing applied-intelligence request, the admitted result and
the text turn must derive from that same path.

For an unrecognized request, the normal owner-turn path may execute once.

The RED does not authorize calling the normal owner-turn path and then calling
applied intelligence again.

## Preserved contracts

Do not change the dataclass fields of:

- `LocalConversationTurn`;
- `UIResponse`;
- `DesktopMessage`.

The visual result is an optional same-turn companion, not a mutation of text
identity.

## Required reuse

Future GREEN must reuse:

- the existing official gateway/source authorities;
- `UnifiedBrain`;
- the existing decorated UI adapter chain;
- the existing desktop controller;
- the certified desktop visual runtime binding;
- the existing desktop worker;
- existing UI-thread handoff mechanisms.

## Forbidden duplicate authorities

Do not create:

- another `OfficialConversationGateway`;
- another `UnifiedBrain`;
- another source-query executor;
- another NASA/Web source authority;
- another desktop controller;
- another projection, companion, presenter, or runtime binding;
- another worker, scheduler, dispatcher, or main loop.

No generic browser/crawler is authorized.

## Explicitly separate residuals

Still outside scope:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

The RED must not encode `mostrame fotos`, `ultimas`, `latest`, or `newest`
behavior.

## Expected RED

With the productive seam absent, the new contract suite must fail only for the
missing same-turn exposure and its missing productive transport surfaces.

The existing baseline must remain green.

`CONTRACT_RED: DELIVERED / PENDING OWNER CERTIFICATION`

`SURGICAL_GREEN: NOT YET AUTHORIZED`

STOP for Owner local certification.
