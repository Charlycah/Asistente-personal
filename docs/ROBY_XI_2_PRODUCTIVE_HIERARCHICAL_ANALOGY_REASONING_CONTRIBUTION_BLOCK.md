# ROBY XI.2 — Productive Hierarchical Analogy

## Concept Comparison → Reasoning Contribution

**Entry baseline:** 13,490 PASS + Ruff clean.

## Reconciliation

CAP-08 already owns the bounded HCC structural comparison primitive through
`GovernedHierarchicalStructuralAnalogyMatcher`. HCC Productivo Ordinario already
produces canonical concept episodes and the canonical reasoning source already
consumes same-turn abstraction/concept context.

The remaining gap was productive reachability: ordinary HCC concept episodes were
not retained as a bounded comparison history, the CAP-08 matcher was not invoked by
the official productive gateway, and a valid analogy therefore could not reach the
reasoning contributor.

No new cognitive primitive or authority was required.

## Implemented path

ordinary productive turns
→ R1/R2 abstractions
→ HCC concept episode
→ exact owner/session/scope concept history
→ next distinct HCC concept episode
→ existing `GovernedHierarchicalStructuralAnalogyMatcher`
→ governed analogy candidate
→ same-turn canonical reasoning source references
→ consultative reasoning context
→ existing `ReasoningRuntimeContributor`.

## Bounded history

The gateway retains only the latest canonical productive concept episode per exact
`owner + session + scope` for comparison. A new concept replaces that prior
comparison point after evaluation.

No durable concept or analogy store was added.

## Fail-closed behavior

Only `ANALOGY_CANDIDATE` results are exposed productively. Scope mismatch,
insufficient structure, ambiguity or no-analogy results do not become reasoning
context.

The first concept in a scope has no previous comparison point and therefore cannot
produce an analogy.

## Governance

The analogy remains:

- read-only;
- session-local;
- non-persistent;
- non-truth-establishing;
- non-authoritative for inference;
- no Memory;
- no Learning;
- no Structural Transfer execution;
- no rule registration;
- no action.

Reasoning receives the analogy only as explicit consultative and revisable context.

## Validation

Five new end-to-end architecture tests cover productive ordinary reachability,
same-turn reasoning-source contribution, session/scope isolation, absence of
cross-scope borrowing, and preservation of all non-authoritative boundaries.

Expanded affected perimeter: **90 PASS**.

`py_compile` passed for modified production and test files.

Official promotion remains gated by local:

`ruff check .`
`pytest -q`

Expected full count if no unrelated test changes exist: **13,495 PASS**.
