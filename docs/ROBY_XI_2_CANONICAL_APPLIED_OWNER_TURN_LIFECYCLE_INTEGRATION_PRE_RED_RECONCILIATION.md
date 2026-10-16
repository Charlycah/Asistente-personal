# ROBY XI.2 — Canonical Applied Owner-Turn Lifecycle Integration
## PRE-RED Reconciliation

## Owner-certified starting state

The preceding POST-GREEN reconciliation is Owner-certified:

- 13,479 tests passed;
- 0 tests failed;
- Ruff clean.

The certified additive applied owner-turn composition is retained as reusable
foundation.

This PRE-RED changes no productive Python code and adds no RED tests.

## Question under audit

Can the certified applied owner-turn result enter the canonical owner-turn
lifecycle while preserving, exactly once:

- gateway accounting;
- cognitive observer begin/complete/fail;
- conversation-entry evidence begin/seal;
- post-turn reflection;
- reflection evidence;
- cognitive analysis;
- explicit-context precedence;
- exact applied-result exposure?

The answer from current code is:

`NO EXISTING INJECTABLE LIFECYCLE SEAM DEMONSTRATED`

Therefore CONTRACT RED is not authorized by this PRE-RED.

## Canonical lifecycle owner

`OfficialConversationGateway.submit` owns the canonical lifecycle envelope.

Before branch selection it performs:

- cognitive observer `begin_turn`;
- conversation-entry evidence `begin`;
- coordination/input/context evidence capture.

Inside that envelope it selects existing internal turn branches.

After a branch yields `LocalConversationTurn`, the same method performs:

- response-status evidence;
- optional `_post_turn_observer`;
- reflection evidence;
- learning/diagnostic evidence;
- failure handling;
- `_submitted_turns += 1`;
- last-origin/session accounting;
- cognitive observer `complete_turn`;
- conversation-entry evidence `seal`.

On failure it performs observer failure and evidence sealing before re-raising.

This is one integrated lifecycle authority.

## Existing interceptor precedent

The gateway already has multiple internal interceptor branches that create
`LocalConversationTurn` before the common finalization section.

Examples include:

- identification;
- governed revision;
- governed learning;
- curiosity question;
- GCDR advisory;
- decision advisory.

These branches demonstrate the correct architectural shape:

`BRANCH INSIDE CANONICAL GATEWAY LIFECYCLE -> COMMON FINALIZATION`

They do not demonstrate an externally injectable interceptor seam.

## Applied bridge location

The same gateway already owns:

- applied conversational intelligence;
- interpretation;
- governed source selection;
- governed query execution;
- natural governed response composition.

`execute_applied_conversational_intelligence` already executes interpretation
internally and returns the exact applied result needed by later visual
presentation.

Therefore the capability authority is already in the canonical gateway.

The missing issue is lifecycle placement, not a missing applied capability.

## Additive GREEN composition

The certified additive module correctly proves:

- explicit-context precedence;
- one applied bridge execution;
- recognized versus fallback branching;
- exact applied-result retention;
- unchanged `LocalConversationTurn`.

It intentionally does not mutate:

- `_submitted_turns`;
- observer internals;
- evidence internals;
- reflection internals.

It therefore cannot independently become the canonical lifecycle owner.

It remains reusable as behavioral evidence and composition logic, but it is
not a substitute for the gateway lifecycle envelope.

## UnifiedBrain lifecycle

`UnifiedBrain.process` calls `submit_observed` when available.

Its callback performs post-turn reflection.

After the gateway returns, `UnifiedBrain.process` performs completed-turn
cognitive analysis.

Consequently a recognized applied owner turn must still pass through the
gateway's observed lifecycle exactly once if it is to remain equivalent to an
ordinary official owner turn.

Executing applied composition before or after `UnifiedBrain.process` would
either bypass lifecycle effects or execute the owner turn twice.

Neither is authorized.

## Search for existing extension seams

The audit inspected gateway, brain, runtime composition, runtime root and
desktop composition for reusable mechanisms such as:

- interceptor registration;
- turn-handler registration;
- turn-executor injection;
- submit hooks;
- turn factories;
- response factories suitable for gateway branch admission.

No mechanism was found that can inject an applied `LocalConversationTurn`
inside `OfficialConversationGateway.submit` before its common finalization.

The gateway exposes governed source adapter registration, but that is a source
extension seam and is not an owner-turn lifecycle extension seam.

`UnifiedBrain` exposes no owner-turn execution strategy injection.

`OfficialROBYRuntime` exposes the canonical conversation object but no
lifecycle finalization API.

## Protected-file constraint

Both lifecycle-bearing files are protected by existing architectural
byte-identity contracts:

`app/official_conversation_gateway.py`

SHA-256:

`0f8896575116a7ebaac908486d897e22c2f6adff59a05b3cc2997d028b5e0b11`

`app/unified_brain.py`

SHA-256:

`05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750`

This PRE-RED does not reinterpret those protections as permission to change
their historical hashes.

## Architectural decision

A CONTRACT RED that merely demands an external wrapper to update private
gateway accounting or observer/evidence state would encode the wrong
architecture.

A CONTRACT RED that demands a second gateway/brain lifecycle would also encode
the wrong architecture.

A CONTRACT RED that silently requires modifying either protected lifecycle
file is not authorized without an explicit governance decision on that
protection.

Therefore:

`STOP BEFORE CONTRACT RED`

The project needs an explicit lifecycle-extension architecture decision first.

## Smallest valid next decision

The next step is not implementation.

The next governed block should be:

`CANONICAL OWNER-TURN LIFECYCLE EXTENSION SEAM — ARCHITECTURAL DECISION`

That decision must choose one of only two acceptable directions:

1. identify a presently overlooked existing canonical seam and prove it; or
2. explicitly authorize a surgical evolution of the canonical lifecycle owner
   under the project's protected-file governance.

It must not authorize:

- private-state mutation from an external wrapper;
- duplicated lifecycle authorities;
- a second gateway;
- a second brain;
- a second observer;
- a second reflection authority;
- historical hash rewriting to legitimize a change.

If protected-file evolution is considered, the decision must specify why the
change is a governed evolution rather than a regression and which historical
contracts must remain as immutable evidence of the earlier certified state.

No code change is authorized by this PRE-RED.

## Desktop consequence

Desktop visual composition-root binding remains deferred.

The existing worker, decorators, explicit-context transport, controller and
UI-thread handoff must not be changed to work around this lifecycle boundary.

## Separate residuals

Still outside scope:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

## Status

`CANONICAL_APPLIED_OWNER_TURN_LIFECYCLE_INTEGRATION_PRE_RED:
COMPLETE / PENDING OWNER CERTIFICATION`

`CANONICAL LIFECYCLE OWNER: OfficialConversationGateway.submit`

`EXISTING INTERNAL INTERCEPTOR PRECEDENT: PRESENT`

`EXISTING INJECTABLE OWNER-TURN LIFECYCLE SEAM: NOT DEMONSTRATED`

`PROTECTED GATEWAY: PRESERVE`

`PROTECTED UNIFIED BRAIN: PRESERVE`

`CONTRACT RED: NOT AUTHORIZED`

`STOP BEFORE RED: REQUIRED`

`NEXT GOVERNED BLOCK:
CANONICAL OWNER-TURN LIFECYCLE EXTENSION SEAM — ARCHITECTURAL DECISION`

`NEW COGNITIVE/SOURCE AUTHORITY: NONE`

STOP for Owner local certification.
