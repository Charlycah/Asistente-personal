# ROBY XI.2 — Higher Cognitive Evolution
## Governed Strategy Structural Identity & Future Influence Wave

**Baseline de entrada:** 13.389 tests PASS + Ruff limpio.
**Estado:** CLOSED / PROMOTED — full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.

## Purpose

Close the governed future-influence bridge without turning metacognitive history into a second
planning authority.

The wave separates:

- strategy **instance identity** (`source_fingerprint`);
- reusable strategy **structural identity** (`structural_fingerprint`).

## Structural identity

`CognitiveStrategyCandidate.structural_fingerprint` is derived only from:

- ordered cognitive capabilities;
- ordered step topology;
- step dependencies;
- evidence-requirement classes;
- Decision requirement;
- a bounded structural schema version.

It does not include request text.

Therefore semantic paraphrases with the same cognitive topology share structural identity while
retaining different instance fingerprints.

## Eligible future structures

`UnifiedCognitiveCoordinator.synthesize_eligible_strategy_advisories(...)` first calls the existing
`CognitivePlanner` path.

It then derives only bounded topological variants of the **same planner-derived capabilities and
dependencies**.

It cannot add or remove cognitive needs.

The current synthesis remains unchanged when no metacognitive influence is supplied.

## Future influence

`GovernedFutureStrategyInfluence` is a read-only decision value under the same
`unified_cognitive_coordination` authority.

A metacognitive advisory may influence a future strategy only when:

- advisory scope matches the current session/evaluation scope;
- advisory status is `ADAPTATION_SUGGESTED`;
- the recommended historical strategy instance is available;
- its structural identity is currently eligible;
- current planner-derived capability needs are preserved.

The influenced strategy is a **new instance** with a new `source_fingerprint`.

The historical instance fingerprint is never reused.

## Fail-closed behavior

- incompatible scope → `NO_INFLUENCE`;
- missing historical recommended instance → `NO_INFLUENCE`;
- recommended structure not currently eligible → `NO_INFLUENCE`;
- insufficient evidence → `NO_INFLUENCE`;
- ambiguous history → `AMBIGUOUS`;
- review-required history → `REVIEW_REQUIRED`.

The advisory identifier is now checked against its provenance fingerprint prefix to detect
tampering.

## Boundaries

Future influence:

- is read-only;
- does not persist;
- creates no Learning;
- creates no Memory;
- does not modify `CognitivePlanner`;
- does not execute actions;
- grants no authority.

No StrategyPreferenceManager, MetaPlanner, second coordinator, repository, scheduler or durable
strategy preference was introduced.

## Causal chain closed

`historical strategy applications`
→ `strategy-linked outcomes`
→ `metacognitive advisory`
→ `historical structural identity`
→ `current planner-derived eligible structures`
→ `bounded future influence`
→ `new strategy instance`.

## Validation

Initial RED failed because the future-influence/structural-identity contracts did not exist.

New contract: **10 PASS**.

Focused matrix across Strategy Synthesis, Strategy Application, Metacognitive Adaptation,
Unified Cognitive Coordination, Method Outcome, Effectiveness Awareness, Comparative Awareness,
Historical Advisory and Longitudinal Improvement: **109 PASS**.

Full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.
