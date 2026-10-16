# ROBY XI.2 — Open Visual Subject Governed Request Representation
## CONTRACT RED

## Owner-certified input

Starting point:

`OPEN VISUAL SUBJECT GOVERNED REQUEST REPRESENTATION — CONTRACT DESIGN
RECONCILIATION`

Certified baseline:

- 13,513 passes;
- zero failures;
- Ruff clean;
- M361 reproducible.

## Authorized scope

This RED covers only:

`OPEN_VISUAL_SUBJECT_GOVERNED_REQUEST_REPRESENTATION`

It does not authorize:

- a general external-image source;
- source capability implementation;
- freshness ordering;
- presentation changes;
- a new selector, executor, router, or authority.

## Contract file

Added:

`tests/architecture/test_open_visual_subject_governed_request_representation_contract_re
d.py`

No productive Python changed.

## Contract obligations

The RED requires:

1. an explicit request-mode discriminator;
2. `TOPIC_CONSTRAINED` legacy semantics;
3. `OPEN_VISUAL_SUBJECT` semantics;
4. preservation of an open `query_text`;
5. non-empty query text for open visual requests;
6. empty topics valid only in explicit open-visual mode;
7. empty topics never acting as a source wildcard;
8. NASA remaining ineligible for `pistas de Nazca`;
9. governed query propagation of the explicit mode;
10. the existing selector remaining canonical;
11. no parallel router, selector, or executor;
12. no freshness or presentation semantics.

## Local focal RED result

Local focal execution:

`7 failed, 3 passed`

The seven intended failures share the same missing contract root:

`GovernedConversationalRequestMode` does not yet exist.

The three passing safeguards demonstrate that the RED itself does not require:

- a parallel visual router;
- a parallel source selector/executor;
- freshness or presentation behavior.

## Expected GREEN boundary

The future GREEN must be surgical.

It may deepen existing request/query contracts and selector eligibility only as
needed to represent the explicit mode safely.

It must not add an eligible general image source in this block.

Therefore an open visual request with no explicitly capable source must remain
`UNAVAILABLE`.

## Integrity

Productive Python delta: zero.

Test Python delta: exactly one new architecture contract file.

No historical guard or hash is mechanically rewritten.

No new authority is introduced.

## Status

`CONTRACT_RED: COMPLETE`

`FOCAL_RED: 7 INTENTIONAL FAIL / 3 PASS`

`MISSING_ROOT: GOVERNED_CONVERSATIONAL_REQUEST_MODE`

`PRODUCTIVE_PYTHON_DELTA: ZERO`

`TEST_PYTHON_DELTA: ONE CONTRACT FILE`

`GENERAL_IMAGE_SOURCE: NOT_AUTHORIZED`

`FRESHNESS: EXCLUDED`

`PRESENTATION: EXCLUDED`

`NEW_AUTHORITY: NONE`

`NEXT: OWNER RED CERTIFICATION`

STOP before GREEN.
