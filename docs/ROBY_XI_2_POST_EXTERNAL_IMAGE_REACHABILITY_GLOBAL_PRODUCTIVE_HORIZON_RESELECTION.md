# ROBY XI.2 — Post External Image Reachability
## Global Productive Horizon Reselection

## Owner-certified starting state

The starting state is Owner-certified at:

- 13,513 passes;
- zero failures;
- Ruff clean;
- M361 regenerated and reproducible.

The closed natural-language reachability block has no demonstrated internal
residual.

## Global candidates

Two external-image residuals remain demonstrated:

1. `GENERAL_EXTERNAL_IMAGE_SUBJECT_REACHABILITY`;
2. `EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

They are not equivalent peers.

## Current governed path

The certified visual path remains:

OWNER EXPLICIT VISUAL REQUEST
-> existing applied conversational admission
-> existing governed source selection
-> existing governed source execution
-> existing immutable governed result
-> existing external-image presentation
-> official desktop surface.

No second source selector, query executor, image authority, or presentation
authority is justified.

## General subject reachability evidence

The current applied conversational admission recognizes a visual request but
still requires at least one existing `InterestTopic`.

The current `GovernedConversationalSourceSelectionRequest` also requires a
non-empty `topics` set.

Therefore:

`mostrame imágenes de las pistas de Nazca`

cannot be generalized correctly merely by adding another visual word or by
removing the topic gate.

The architectural question is how an explicit open external-image subject/query
can be represented through the existing governed selection contract without
enumerating every possible subject as an `InterestTopic`.

This is a contract/representation reachability residual.

It must not be solved with an entity-by-entity topic list.

## Freshness evidence

Freshness semantics concern ordering or constraining results after a request has
become representable and has reached governed source selection/execution.

The existing request already contains temporal bounds such as
`published_after` and `published_before`, but the demonstrated residual concerns
user-facing latest/newest semantics and ordering.

Freshness does not solve the inability to represent an arbitrary visual
subject.

## Dependency decision

The dependency is:

`GENERAL_EXTERNAL_IMAGE_SUBJECT_REACHABILITY`
-> `EXTERNAL_IMAGE_FRESHNESS_ORDERING`

Reason:

A request such as:

`mostrame las últimas imágenes de las pistas de Nazca`

first requires the open subject `pistas de Nazca` to survive admission and be
represented in the governed query path. Only then can `últimas` meaningfully
constrain or order the reachable result set.

Implementing freshness first would improve only the already enumerated subject
subset and leave the more fundamental reachability boundary intact.

## Selected productive horizon

`NEXT_PRODUCTIVE_RESIDUAL: GENERAL_EXTERNAL_IMAGE_SUBJECT_REACHABILITY`

`LATER_PRODUCTIVE_RESIDUAL: EXTERNAL_IMAGE_FRESHNESS_ORDERING`

The two residuals remain separate and must not be merged into one RED/GREEN.

## Classification status

No implementation classification is authorized by this reselection alone.

The next step must be a PRE-RED reconciliation that determines whether the
existing governed request/selection contract can be deepened without changing
its authority boundaries.

That PRE-RED must inspect:

- existing request invariants around non-empty topics;
- source eligibility semantics;
- query-text preservation/extraction;
- information region semantics;
- source policy and registration;
- failure behavior when no registered source can serve an open subject;
- existing tests protecting topic-driven source selection;
- whether an existing generic/open-query representation already exists
  elsewhere and can be reused.

Only after that evidence may the seam be classified.

## Permanent prohibitions

The next block must not:

- add a new generic image search authority;
- add a parallel intent router;
- add a parallel source selector or query executor;
- enumerate arbitrary subjects as new `InterestTopic` values;
- bypass registered-source or source-policy governance;
- alter the certified desktop visual presentation path;
- implement freshness as a side effect;
- change code before PRE-RED reconciliation closes.

## Integrity

This reselection changes documentation only.

No productive Python is changed.
No test Python is changed.
No new authority is introduced.

## Status

`GLOBAL_PRODUCTIVE_HORIZON_RESELECTION: COMPLETE`

`NEXT_PRODUCTIVE_RESIDUAL: GENERAL_EXTERNAL_IMAGE_SUBJECT_REACHABILITY`

`LATER_PRODUCTIVE_RESIDUAL: EXTERNAL_IMAGE_FRESHNESS_ORDERING`

`DEPENDENCY: GENERAL SUBJECT REACHABILITY -> FRESHNESS ORDERING`

`CONTRACT_RED_AUTHORIZATION: NO`

`PRODUCTIVE_GREEN_AUTHORIZATION: NO`

`NEW_AUTHORITY: NONE`

`NEXT: GENERAL EXTERNAL IMAGE SUBJECT REACHABILITY — PRE-RED RECONCILIATION`

STOP before RED.
