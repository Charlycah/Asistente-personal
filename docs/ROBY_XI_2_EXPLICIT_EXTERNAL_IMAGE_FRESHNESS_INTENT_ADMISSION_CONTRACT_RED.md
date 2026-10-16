# ROBY XI.2 — Explicit External Image Freshness Intent Admission
## CONTRACT RED

### Owner-certified starting state
Input is the Owner-certified Contract Design Reconciliation. Owner evidence: Ruff CLEAN and 13,602 PASS / 0 FAIL.

This increment changes tests/documentation only. Productive Python is unchanged.

## Contract seam
Parent: `EXTERNAL_IMAGE_FRESHNESS_ORDERING`.
Residual: `EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`.
Canonical owner: `AppliedConversationalIntelligence.interpret()`.
Required mapping: `EXPLICIT_IMAGE_FRESHNESS_INTENT -> GovernedSourceQueryOrder.NEWEST_FIRST`.

The RED deepens ACI only. No freshness parser, manager, router, selector, provider authority, executor, planner, agent, or loop is introduced.

## New RED contract
Canonical RED: `tests/architecture/test_explicit_external_image_freshness_intent_admission_contract_red.py`.

It freezes accented/unaccented `las últimas|ultimas fotos de <subject>` and `las imágenes|imagenes más|mas recientes de <subject>`; exact subject extraction; `order is NEWEST_FIRST`; no implicit date bounds; ordinary visual `order=None`; subjectless/punctuation-only fail-closed behavior; known-topic authority preservation; rejection of unbounded/English freshness as a NEWEST_FIRST trigger; and no parallel authority, local sorting, provider selection, or date filtering inside ACI.

Permanent distinctions: `LATEST_INTENT != ARBITRARY_DATE_WINDOW` and `TIME_FILTER != RESULT_ORDER`.

## Historical contract reconciliation
The historical general-open-visual contract contained a pre-residual source-text assertion forbidding `newest` inside ACI. That one obsolete nominal assertion is removed and its guard is renamed `test_red_admission_does_not_execute_or_date_filter_freshness`. The enduring prohibitions on `sorted(`, `order_by`, and `published_after` remain. Existing architecture contracts continue to protect downstream ownership.

## RED evidence
Focused execution of the new RED plus the reconciled historical contract produced `6 failed, 22 passed`. The failures are exactly the intended seam: four bounded Spanish open-subject forms remain NOT_RECOGNIZED; freshness subject extraction is absent; and known-topic freshness retains `order=None`.

The RED does not expose a missing enum, request field, selector capability gate, or Wikimedia projection. It fails because canonical ACI does not yet recognize the frozen freshness grammar and project the existing `NEWEST_FIRST` order.

## Explicit exclusions
GREEN must not redesign request/order types, source capabilities, selector ranking/gating, executor ordering, Wikimedia projection, NASA semantics, presentation sorting, generic temporal NLP, or cognitive-cycle authorities. No fixed date window or relevance fallback is authorized.

## Formal state
`CONTRACT_RED: ESTABLISHED / PENDING OWNER CERTIFICATION`
`EXPECTED_RED: 6 FAIL / 22 PASS`
`RED_FAILURE_SEAM: CANONICAL_ACI_FRESHNESS_ADMISSION`
`HISTORICAL_CONTRACT_RECONCILIATION: SURGICAL / COMPLETE`
`NEW_AUTHORITY: NONE`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`GREEN_AUTHORIZATION: AFTER_OWNER_RED_CERTIFICATION`
`NEXT_AFTER_OWNER_CERTIFICATION: SURGICAL GREEN`
`STOP_BEFORE_GREEN: YES`
