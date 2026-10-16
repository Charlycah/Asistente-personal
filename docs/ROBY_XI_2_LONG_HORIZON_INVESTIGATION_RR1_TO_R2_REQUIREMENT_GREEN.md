# ROBY XI.2 — RR1 → R2 Requirement Admission — GREEN

## Productive cut

The certified RR1 `RECORDED_CONTINUATION` may now consume one explicit revised
`GovernedHypothesisDeepeningReport` through the existing governed discrimination
surface and admit zero or one resulting exact `DiscriminatingEvidenceRequirement`
through the existing investigation productive-continuation surface.

## Canonical owners preserved

- Requirement production remains owned by `governed_reasoning`, exposed through
  `GovernedMultiHypothesisProductiveConsumptionV1`.
- Episode continuation remains owned by
  `GovernedMultiStepInvestigationProductiveContinuationV1` and its existing episode
  boundary.
- The long-horizon adapter does not instantiate a discriminator directly and does not
  create, rewrite, rank or select requirements.

## Eligibility and lineage

The adapter accepts only RR1 recorded continuation in `AWAITING_REQUIREMENT`, step 1,
with exactly one acquisition remaining. The revised report must preserve exact source
and world-snapshot lineage and must contain the exact RR1 `evidence_id` in at least one
hypothesis assessment before discrimination can run.

## Cardinality

- zero requirements: the exact canonical continuation receives `None` and must close
  with `CLOSED / NO_NEW_REQUIREMENT`;
- one requirement: the exact requirement object is forwarded once and the exact same
  episode must reach `READY_FOR_PLANNING`, step 2, with one acquisition remaining;
- more than one requirement: `REVIEW_REQUIRED`, without arbitrary selection or episode
  continuation.

## Governed stop

Even when R2 is admitted, this GREEN only exposes
`eligible_for_existing_planning=True`. It does not invoke Planning, Authorization,
Execution, Reasoning, Curiosity, Memory, World Model, persistence, retry or background
work, and it does not establish truth.
