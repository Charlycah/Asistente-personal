# ROBY XI.2 — Official Desktop Same-Turn Visual Composition Root Binding
## PRE-RED Reconciliation

## Owner-certified starting state

The preceding POST-GREEN reconciliation is Owner-certified:

- 13,467 tests passed;
- 0 tests failed;
- Ruff clean.

Certified residual:

`OFFICIAL_DESKTOP_SAME_TURN_VISUAL_COMPOSITION_ROOT_BINDING`

This PRE-RED changes no productive Python code and adds no RED tests.

## Question resolved by this reconciliation

The required architectural question was:

Can an existing callable already produce both the canonical
`LocalConversationTurn` and the admitted applied conversational result from one
governed owner-turn execution?

The repository evidence answers:

`NO`

The two existing paths are separate today.

## Existing applied-intelligence path

`OfficialConversationGateway.execute_applied_conversational_intelligence`
performs:

1. applied-language interpretation;
2. governed source selection;
3. governed source query;
4. natural governed response composition;
5. return of `AppliedConversationalIntelligenceResult`.

That result contains:

- interpretation;
- selection;
- conversational result;
- natural answer text.

It does not contain or create `LocalConversationTurn`.

Its existing M345 contract explicitly treats it as an applied bridge that
reuses the governed information flow.

## Existing owner-turn path

The canonical desktop owner turn remains:

`UnifiedBrain.process`
-> `OfficialConversationGateway.submit_observed`
-> `OfficialConversationGateway.submit`
-> existing interceptor cascade or
   `EndToEndLocalConversation.converse`
-> `LocalConversationTurn`.

`EndToEndLocalConversation.converse` owns the normal pipeline turn creation,
history sequence, optional trace handling, memory recording, and persistence.

Therefore the applied bridge cannot simply replace that path without an
explicit owner-turn integration.

## Existing gateway interceptor precedent

`OfficialConversationGateway.submit` already owns multiple explicit
interceptors.

When one handles a request, the gateway creates a canonical
`LocalConversationTurn` directly and does not also call the normal runtime
conversation.

Examples include identification, governed learning, curiosity, complex
decision advisory, and decision advisory turns.

These interceptor turns preserve:

- owner;
- session;
- sequence;
- response text;
- pipeline and operational identities;
- retrieval/network flags;
- rationale;
- response path;
- created time.

This is the existing architectural precedent for an applied-result owner turn.

## Exact missing seam

The productive residual is refined to:

`APPLIED_CONVERSATIONAL_INTELLIGENCE_OWNER_TURN_INTERCEPTOR`

This is not a second source or second conversational authority.

It is a missing integration inside the existing
`OfficialConversationGateway.submit` owner-turn cascade.

For a recognized applied request, the existing gateway must be able to:

1. execute the existing applied bridge once;
2. create the canonical interceptor `LocalConversationTurn` from the same
   admitted result;
3. expose that exact applied result as same-turn presentation evidence;
4. avoid calling `EndToEndLocalConversation.converse` for that same turn.

For a non-recognized request, the existing normal owner-turn path continues
once.

## Critical execution invariant

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION`

Forbidden:

normal owner-turn execution
-> applied bridge execution

and:

applied bridge execution
-> normal owner-turn execution

when the applied request was already recognized and handled.

The recognized applied branch must itself be the owner-turn branch.

## Applied owner-turn semantics to fix in RED

Future CONTRACT RED should require that a recognized applied result is
projected into a canonical `LocalConversationTurn` with:

- existing runtime owner;
- effective session id;
- gateway sequence;
- original user text;
- exact natural governed answer text;
- completed status when the bridge returns a usable governed answer;
- retrieval/network flags derived from the admitted governed source result,
  not guessed from response text;
- deterministic lineage from existing governed result identities;
- interceptor response path;
- rationale identifying the existing applied governed bridge.

The applied result itself must remain available as the optional same-turn
visual companion source.

The exact final lineage fields must be derived from existing result objects in
CONTRACT RED and not invented here.

## Explicit-selection precedence

The current owner-turn path transports:

- explicit document ids;
- explicit sources;
- explicit evidence references;
- integrated visual context.

The future applied interceptor must not silently override an explicit
selection supplied by the user or another certified desktop flow.

CONTRACT RED must fix precedence before GREEN.

The safe PRE-RED direction is:

explicit current-turn selection/context
-> preserve existing owner-turn path;

ordinary eligible text with no explicit selection
-> applied interceptor may recognize and handle;

not recognized
-> existing owner-turn path.

This prevents the visual source bridge from stealing authority from explicit
document, evidence, or visual-context turns.

## Existing desktop decorator chain

`desktop_bootstrap.py` currently composes:

`LocalConversationUIAdapter`
-> governed proposal review
-> episodic source constraint
-> optional service guard
-> conversational personality
-> `ROBYDesktopApp`.

These decorators must remain effective.

The applied owner-turn interceptor belongs below them, at the existing
official gateway owner-turn authority.

It must not create a parallel desktop adapter chain.

## Same-turn exposure consequence

Once the gateway owner-turn itself can handle and retain the applied result,
the already-certified same-turn visual exposure may consume that exact result.

The exposure layer must not invoke
`execute_applied_conversational_intelligence` independently.

Its future execution input must be the owner-turn integration, not a second
query.

## Worker and Tk consequence

The official desktop worker remains the only owner-turn background worker.

The worker currently calls `controller.submit`.

Later composition may route through the certified optional visual companion
surface, but it must still execute only one owner turn.

Bounded preview I/O must remain on that background side or another already
certified non-Tk execution boundary.

Tk mutation must use the existing `root.after` or existing
`UIThreadDispatcher`.

No second worker or dispatcher is authorized.

## CONTRACT RED scope

After Owner certification, CONTRACT RED should fix at least:

1. recognized applied request becomes one gateway owner-turn interceptor;
2. exact admitted applied result remains attached to that same turn;
3. recognized branch does not call normal runtime conversation;
4. non-recognized branch calls normal owner-turn path exactly once;
5. explicit document/source/evidence/visual context keeps precedence;
6. existing gateway observer/evidence completion still occurs;
7. gateway submitted-turn accounting remains one;
8. `LocalConversationTurn` fields remain backward compatible;
9. `UIResponse` and `DesktopMessage` remain backward compatible;
10. desktop decorators remain in the official composition chain;
11. same-turn visual exposure reuses the retained applied result;
12. no URL or visual identity is parsed from response text;
13. no second gateway, brain, source executor, controller, worker, or
    dispatcher appears;
14. no reachability or freshness semantics are added.

## Protected-authority warning

Earlier GREEN validation demonstrated that
`app/runtime_ui_adapter.py` is protected by exact historical hash.

Do not mutate that protected file merely to make a new RED pass.

Any future contract must respect existing exact-hash protections and prefer
the canonical gateway integration point demonstrated here.

Historical hashes must never be updated to legitimize an unintended mutation.

## Separate later residuals

Remain outside scope:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

This PRE-RED does not add `mostrame fotos` recognition or `ultimas` ordering.

## Status

`SAME_TURN_VISUAL_COMPOSITION_ROOT_BINDING_PRE_RED:
COMPLETE / PENDING OWNER CERTIFICATION`

`EXACT MISSING SEAM:
APPLIED_CONVERSATIONAL_INTELLIGENCE_OWNER_TURN_INTERCEPTOR`

`EXISTING DUAL-PURPOSE EXECUTOR: ABSENT`

`EXISTING GATEWAY INTERCEPTOR PRECEDENT: PRESENT / REUSE`

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION: MANDATORY`

`EXPLICIT SELECTION PRECEDENCE: PRESERVE`

`DESKTOP DECORATOR CHAIN: PRESERVE`

`NEW COGNITIVE/SOURCE AUTHORITY: NONE`

`CONTRACT RED: NOT YET OWNER-AUTHORIZED`

STOP for Owner local certification.
