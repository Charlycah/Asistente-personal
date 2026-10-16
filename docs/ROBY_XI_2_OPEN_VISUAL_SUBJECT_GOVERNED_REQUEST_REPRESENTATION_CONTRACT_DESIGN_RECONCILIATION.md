# ROBY XI.2 — Open Visual Subject Governed Request Representation
## CONTRACT DESIGN RECONCILIATION

## Owner-certified starting state

The starting PRE-RED reconciliation is Owner-certified at:

- 13,513 passes;
- zero failures;
- Ruff clean;
- M361 reproducible.

This reconciliation changes documentation only.

## Problem to solve

ROBY must eventually be able to preserve an explicit request such as:

`mostrame imágenes de las pistas de Nazca`

without:

- inventing an `InterestTopic` for Nazca;
- treating empty topics as a wildcard;
- routing the request to NASA;
- creating a second source selector or query executor.

## Existing reusable contract

The current governed request/query path already carries `query_text`.

This transport must be reused.

`query_text` is search payload, not source eligibility authority.

That distinction is permanent.

## Existing constraint

Topics currently serve two different roles:

1. semantic characterization of the request;
2. source eligibility and declaration validation.

For topic-constrained requests this is valid.

For an explicit open visual subject, forcing an `InterestTopic` would confuse a
finite personal-interest taxonomy with an arbitrary external search subject.

Allowing no topics without another explicit semantic dimension would be worse:
the current subset checks would make an empty set eligible against every
topic-declared source.

## Minimum semantic contract

The minimum future representation should add an explicit bounded request mode,
not an artificial topic.

Contract concept:

`GovernedConversationalRequestMode.TOPIC_CONSTRAINED`

`GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT`

The mode is a request semantic discriminator only.

For `TOPIC_CONSTRAINED`:

- existing non-empty topic requirements remain unchanged;
- existing source topic-subset eligibility remains unchanged;
- existing behavior must remain byte-for-behavior compatible.

For `OPEN_VISUAL_SUBJECT`:

- `query_text` must be non-empty;
- the request must originate from explicit visual language;
- an empty topic set is permitted only as representation, never as eligibility;
- source selection must require an explicit source declaration/capability that
  authorizes open visual-subject queries;
- absence of such a source must produce typed `UNAVAILABLE`;
- no fallback to all registered sources is allowed.

## Source-side contract boundary

Current `GovernedInformationSource` has no demonstrated media/image/open-subject
capability dimension.

Therefore request representation alone cannot authorize a source.

A future source-side capability declaration is a separate seam and must be
introduced only when an actual governed source can truthfully support it.

Conceptually required later capability:

`OPEN_VISUAL_SUBJECT_QUERY`

The exact name/type is not authorized here.

It must be declarative source metadata, not a new source-selection authority.

## Query contract propagation

If a source is eventually selected for an open visual subject, the existing
`GovernedSourceQuery` must preserve the request mode and `query_text`.

Its validation must distinguish:

- topic-constrained query: non-empty topics required;
- open-visual-subject query: non-empty query text required and source capability
  already proven by canonical selection/preparation.

The query must never infer source eligibility from an empty topic set.

## Canonical ownership

`OfficialConversationGateway` remains the owner.

`GovernedConversationalSourceSelector` remains the selector.

`GovernedSourceQueryExecutor` remains the executor.

Existing source adapters remain source-specific.

Existing desktop visual presentation remains presentation-only.

No new cognitive or execution authority is required.

## Applied conversational boundary

`AppliedConversationalIntelligence` may eventually identify explicit visual
language and extract/preserve the open subject as `query_text`.

It must not choose a source.

It must not declare arbitrary source capability.

It must not turn every noun phrase into an `InterestTopic`.

## Failure semantics

The safe first behavior is:

explicit open visual request
-> represented as open visual subject
-> canonical selector evaluates declared eligible sources
-> none eligible
-> typed `UNAVAILABLE`.

This is preferable to silently routing to an unrelated source.

Thus representation can be certified independently before a general external
image source becomes reachable.

## Contract ordering

The work must remain split:

1. `OPEN_VISUAL_SUBJECT_GOVERNED_REQUEST_REPRESENTATION`;
2. `OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY`;
3. `EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

Do not merge these blocks.

## RED design authorization

The evidence is now sufficient to authorize a bounded RED for the first seam.

The RED must demonstrate, without productive implementation:

1. a request mode distinguishes topic-constrained and open-visual requests;
2. legacy topic-constrained requests preserve all current invariants;
3. open-visual requests require non-empty `query_text`;
4. empty topics are valid only with explicit open-visual mode;
5. empty topics never make every source eligible;
6. without an explicitly capable source, selection is `UNAVAILABLE`;
7. NASA is not eligible for `pistas de Nazca`;
8. the gateway remains canonical owner;
9. the existing selector and executor remain canonical;
10. no source capability implementation is added in this RED;
11. no freshness behavior is added;
12. no presentation behavior is changed.

The RED may expose the missing contract through failing tests, but must not
prescribe a parallel implementation.

## Classification

This is a bounded evolution of existing governed request/query contracts and
their canonical selector semantics.

`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`

The classification does not authorize a new source or a new authority.

## Prohibitions

Do not:

- use empty topics as wildcard;
- create `InterestTopic.NAZCA`;
- route arbitrary visual subjects to NASA;
- create a generic image router;
- create a second selector or executor;
- add a source merely to make the RED pass;
- implement freshness;
- modify presentation.

## Integrity

No productive Python changed.
No test Python changed.
No new authority was introduced.

## Status

`CONTRACT_DESIGN_RECONCILIATION: COMPLETE`

`REQUEST_MODE_DISCRIMINATOR: REQUIRED`

`OPEN_VISUAL_QUERY_TEXT: REQUIRED`

`EMPTY_TOPICS_REPRESENTATION: BOUNDED_BY_EXPLICIT_MODE`

`EMPTY_TOPICS_SOURCE_WILDCARD: FORBIDDEN`

`SOURCE_CAPABILITY_DECLARATION: SEPARATE_LATER_SEAM`

`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`

`CONTRACT_RED_AUTHORIZATION: YES / FIRST_SEAM_ONLY`

`PRODUCTIVE_GREEN_AUTHORIZATION: NO`

`NEW_AUTHORITY: NONE`

`NEXT: OPEN VISUAL SUBJECT GOVERNED REQUEST REPRESENTATION — CONTRACT RED`

STOP before GREEN.
