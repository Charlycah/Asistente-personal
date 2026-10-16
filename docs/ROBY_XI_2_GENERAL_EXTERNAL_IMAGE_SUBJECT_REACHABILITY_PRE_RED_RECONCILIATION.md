# ROBY XI.2 — General External Image Subject Reachability
## PRE-RED RECONCILIATION

## Certified starting state

The selected starting state is:

`POST-EXTERNAL-IMAGE-REACHABILITY GLOBAL PRODUCTIVE HORIZON RESELECTION`

Its inherited Owner-certified product baseline is:

- 13,513 passes;
- zero failures;
- Ruff clean;
- M361 reproducible.

This PRE-RED changes documentation only.

## Selected residual

`GENERAL_EXTERNAL_IMAGE_SUBJECT_REACHABILITY`

Target natural form:

`mostrame imágenes de <sujeto abierto>`

Example:

`mostrame imágenes de las pistas de Nazca`

The goal is not to enumerate every possible subject as an `InterestTopic`.

## Existing visual admission

`AppliedConversationalIntelligence` already recognizes the bounded visual form:

- `mostrame`;
- an image noun;
- an existing governed topic.

However, its current interpretation returns `NOT_RECOGNIZED` when no topic is
matched.

Therefore the language gate is only the first topic dependency.

## Existing governed request contract

`GovernedConversationalSourceSelectionRequest` already preserves:

- original text;
- `query_text`;
- limit;
- region;
- temporal bounds;
- parameters.

This is useful existing infrastructure.

But it also requires a non-empty `topics` set.

There is no discovered `open_query`, `free_text`, or generic subject contract
in the current application code.

## Existing governed query contract

`GovernedSourceQuery` also preserves `query_text` and the other bounded query
fields.

It independently requires at least one topic.

Therefore allowing an empty topic only in conversational admission or source
selection request would not make the query executable.

## Existing source declarations and eligibility

`GovernedInformationSource` requires at least one declared topic.

`GovernedInformationItem` also requires at least one topic.

Source eligibility is currently determined in part by:

`request.topics.issubset(source.topics)`

This is a real source-governance boundary.

An empty topic set would be a dangerous accidental wildcard because the empty
set is a subset of every source topic set.

Therefore a future GREEN must not obtain generality by simply allowing empty
topics.

## Existing query-text reuse

The existing governed path already carries `query_text`.

The NASA adapter uses `query.query_text` as its search text when present and
falls back to topic-derived text otherwise.

This demonstrates that arbitrary search text can already survive inside a
selected governed source query.

It does not demonstrate that NASA, or any current source, is a universal image
source.

NASA remains a governed space-information source.

`pistas de Nazca` must not be routed to NASA merely because NASA accepts
`query_text`.

## Source availability finding

The current source model is topic-declared and deterministic.

No evidence was found in this PRE-RED of an existing registered general-purpose
external image source whose declared authority is arbitrary visual subjects.

Therefore two different concerns must not be conflated:

1. representing an open visual subject;
2. having an eligible governed source for that subject.

The first is a semantic/request representation issue.
The second is a governed source-capability issue.

## Exact demonstrated residuals

The global residual is refined into two ordered seams:

`OPEN_VISUAL_SUBJECT_GOVERNED_REQUEST_REPRESENTATION`

followed by:

`OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY`

The second seam is conditional on actual existing source capability evidence.

No new source is authorized by this PRE-RED.

## Classification

The first seam is not safely reducible to the previously changed
`AppliedConversationalIntelligence` vocabulary.

It crosses existing request/query invariants and source eligibility semantics.

Therefore:

`CLASS_2_APPLIED_ADMISSION_ONLY: REJECTED`

This PRE-RED does not yet authorize a broader class change.

Before CONTRACT RED, a surgical contract-design reconciliation is required to
identify whether an existing semantic dimension can distinguish:

- topic-constrained requests;
- explicit open-subject visual requests;

without making empty topics a wildcard and without weakening source governance.

## Required next reconciliation

The next step must inspect and design the minimum semantic contract for:

`OPEN_VISUAL_SUBJECT_GOVERNED_REQUEST_REPRESENTATION`

It must preserve:

- one `OfficialConversationGateway` owner;
- registered sources only;
- deterministic source selection;
- source declarations and policy;
- explicit unavailable behavior;
- existing topic-constrained behavior unchanged;
- existing `query_text` transport;
- no autonomous fetch;
- no presentation changes;
- no freshness semantics.

It must also determine whether a current source can truthfully declare general
visual-subject coverage. If none can, representation and source acquisition
must remain separate blocks.

## Prohibitions

Do not:

- remove topic validation mechanically;
- treat empty topics as a wildcard;
- route arbitrary subjects to NASA;
- add Nazca or arbitrary entities one by one to `InterestTopic`;
- create a parallel image search router;
- create a parallel source selector or executor;
- bypass source registration or policy;
- alter desktop visual presentation;
- implement freshness in this block.

## Integrity

No productive Python changed.
No test Python changed.
No new authority was introduced.

## Status

`PRE_RED_RECONCILIATION: COMPLETE`

`OPEN_QUERY_REPRESENTATION_ALREADY_EXISTS: NO`

`QUERY_TEXT_TRANSPORT_ALREADY_EXISTS: YES`

`EMPTY_TOPICS_AS_WILDCARD: FORBIDDEN`

`NASA_AS_GENERAL_IMAGE_SOURCE: REJECTED`

`FIRST_REFINED_SEAM: OPEN_VISUAL_SUBJECT_GOVERNED_REQUEST_REPRESENTATION`

`SECOND_REFINED_SEAM: OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY`

`CONTRACT_RED_AUTHORIZATION: NO`

`PRODUCTIVE_GREEN_AUTHORIZATION: NO`

`NEW_AUTHORITY: NONE`

`NEXT: OPEN VISUAL SUBJECT GOVERNED REQUEST REPRESENTATION — CONTRACT DESIGN
RECONCILIATION`

STOP before RED.
