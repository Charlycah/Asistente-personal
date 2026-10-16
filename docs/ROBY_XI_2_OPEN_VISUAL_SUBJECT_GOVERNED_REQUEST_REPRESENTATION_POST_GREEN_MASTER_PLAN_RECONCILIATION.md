# ROBY XI.2 — Open Visual Subject Governed Request Representation
## POST-GREEN MASTER PLAN RECONCILIATION

## Certified baseline

The corrected surgical GREEN is Owner-certified:

- 13,523 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated and reproducible;
- no unexpected regressions.

The Owner-corrected `app/governed_source_query.py` is part of this baseline.

## Closed seam

`OPEN_VISUAL_SUBJECT_GOVERNED_REQUEST_REPRESENTATION` is complete.

The productive state now provides one governed semantic discriminator:

- `TOPIC_CONSTRAINED`;
- `OPEN_VISUAL_SUBJECT`.

`TOPIC_CONSTRAINED` remains the default and preserves the existing non-empty
`InterestTopic` contract.

`OPEN_VISUAL_SUBJECT` permits an empty topic set only as explicit
representation and requires non-empty normalized `query_text`.

The mode is preserved in `GovernedSourceQuery`.

## Safety property now demonstrated

An empty topic set is not source eligibility authority.

The canonical selector explicitly rejects current source eligibility for
`OPEN_VISUAL_SUBJECT` before applying the legacy topic-subset rule.

Therefore an open subject such as `pistas de Nazca` is representable without
becoming a wildcard over all registered sources.

NASA is not promoted to a general image source.

## Remaining source-side gap

`GovernedInformationSource` still declares topic coverage and source
classification, but no explicit capability for open visual-subject queries.

Accordingly, the current `UNAVAILABLE` result is intentional and correct.

The next residual is not request representation. It is source-side governed
eligibility and reachability for the already represented request mode:

`OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY`

This residual must determine how an existing or future governed source can
declare that capability without creating a parallel selector, executor,
router, or authority.

The exact source-capability representation is not authorized by this
reconciliation and must be established by its own pre-RED evidence review.

## Authority preservation

The canonical ownership chain remains unchanged:

- `OfficialConversationGateway` owns the conversational path;
- `GovernedConversationalSourceSelector` remains source selector;
- `GovernedSourceQueryExecutor` remains executor;
- source adapters remain source-specific;
- desktop visual composition remains presentation-only.

No new execution authority was introduced by the closed seam.

## Master-plan ordering

The previously established dependency remains valid:

1. `OPEN_VISUAL_SUBJECT_GOVERNED_REQUEST_REPRESENTATION` — CLOSED;
2. `OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY` — NEXT;
3. `EXTERNAL_IMAGE_FRESHNESS_ORDERING` — LATER.

Freshness must not be pulled forward. A general subject first needs a governed
eligible source path before newest/latest ordering can be meaningful.

## Reconciliation decision

No internal residual remains in the representation seam.

No evidence justifies reopening natural-language admission, desktop visual
presentation, canonical owner-turn binding, or the representation contract.

The next step is a surgical pre-RED reconciliation for source eligibility and
reachability only.

## Status

`POST_GREEN_MASTER_PLAN_RECONCILIATION: COMPLETE`

`REPRESENTATION_SEAM: CLOSED / OWNER-CERTIFIED INPUT`

`INTERNAL_RESIDUAL: NONE`

`NEXT_PRODUCTIVE_RESIDUAL: OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY`

`LATER_PRODUCTIVE_RESIDUAL: EXTERNAL_IMAGE_FRESHNESS_ORDERING`

`NASA_AS_GENERAL_IMAGE_SOURCE: FORBIDDEN`

`EMPTY_TOPICS_AS_SOURCE_WILDCARD: FORBIDDEN`

`CONTRACT_RED_AUTHORIZATION_FOR_NEXT_SEAM: NO`

`PRODUCTIVE_GREEN_AUTHORIZATION_FOR_NEXT_SEAM: NO`

`PRODUCTIVE_PYTHON_DELTA: ZERO`

`TEST_PYTHON_DELTA: ZERO`

`NEW_AUTHORITY: NONE`

NEXT:

`OPEN VISUAL SUBJECT ELIGIBLE GOVERNED SOURCE REACHABILITY — PRE-RED RECONCILIATION`
