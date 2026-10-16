# ROBY XI.2 — Open Visual Subject Governed Request Representation
## SURGICAL GREEN

## Owner-certified RED input

The starting RED is Owner-certified at:

- 13,516 passes;
- seven intentional contract failures;
- zero unexpected failures;
- Ruff clean;
- M361 reproducible.

## Surgical implementation

Added:

`app/governed_conversational_request_mode.py`

with one semantic discriminator:

- `TOPIC_CONSTRAINED`;
- `OPEN_VISUAL_SUBJECT`.

Deepened existing canonical contracts:

- `GovernedConversationalSourceSelectionRequest`;
- `GovernedConversationalSourceSelector`;
- `GovernedSourceQuery`.

No source adapter was changed.

## Legacy preservation

`TOPIC_CONSTRAINED` remains the default.

It continues to require at least one `InterestTopic`.

Existing topic-subset source eligibility remains unchanged for this mode.

## Open visual representation

`OPEN_VISUAL_SUBJECT`:

- permits an empty topic set only as explicit representation;
- requires non-empty normalized `query_text`;
- propagates its mode into `GovernedSourceQuery`;
- does not infer source eligibility from empty topics.

The canonical selector explicitly returns no eligible current source for this
mode because no source capability declaration exists yet.

Therefore:

`pistas de Nazca`

is representable but not silently routed to NASA or any other current source.

## Authority preservation

No new selector exists.
No new executor exists.
No new router exists.
No new source exists.

The new enum is semantic contract vocabulary, not an execution authority.

## Verification

Focused RED plus historical M344 request/query contracts:

`26 passed`

Relevant governed query/selection suite:

`55 passed`

The local container does not provide the project Ruff executable, so Ruff
certification remains an Owner-side requirement.

No test Python was changed from the Owner-certified RED.

## Exclusions

No general external-image source was added.
No source capability declaration was added.
No freshness behavior was added.
No presentation behavior was changed.

## Status

`SURGICAL_GREEN: COMPLETE`

`RED_CONTRACT_LOCALLY_GREEN: YES`

`RELEVANT_REGRESSION_SUITE: 55 PASS`

`TOPIC_CONSTRAINED_DEFAULT: PRESERVED`

`OPEN_VISUAL_SUBJECT_REPRESENTATION: IMPLEMENTED`

`EMPTY_TOPICS_SOURCE_WILDCARD: PREVENTED`

`NASA_GENERAL_IMAGE_ELIGIBILITY: PREVENTED`

`GENERAL_IMAGE_SOURCE: NOT_IMPLEMENTED`

`SOURCE_CAPABILITY_SEAM: UNTOUCHED`

`FRESHNESS: UNTOUCHED`

`PRESENTATION: UNTOUCHED`

`NEW_EXECUTION_AUTHORITY: NONE`

`OWNER GREEN FUNCTIONAL SUITE: 13,523 PASS / 0 FAIL`

`OWNER RUFF AFTER CORRECTED IMPORT ORDER: CLEAN`

`CORRECTED_GOVERNED_SOURCE_QUERY: INTEGRATED`

`NEXT: OWNER CERTIFICATION OF CORRECTED COMPLETE ZIP`
