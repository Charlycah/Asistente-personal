# ROBY XI.2 --- CAP-07 Multi-Family Productive Abstraction Normalization --- Contract & RED Evidence

**Baseline:** 13,468 PASS + Ruff clean\
**Authority:** `governed_reasoning`\
**Owner:** `GovernedProductiveAbstractionAdmission`\
**Mode:** contract + RED evidence only; no production implementation.

------------------------------------------------------------------------

## 1. Decision

The next change is an **existing-owner deepening**, not a new cognitive
primitive.

The current Productive Abstraction Admission accepts two certified
semantic-grounding families but collapses both to one abstraction pair:

`required_for` → `blocked_when_unavailable`

This prevents ordinary runtime from producing multiple semantically
distinct abstraction episodes for HCC.

The contract therefore introduces one additional bounded normalization
family while preserving R1 unchanged.

------------------------------------------------------------------------

## 2. R1 --- preserved existing family

R1 remains:

**relation:** `required_for`\
**outcome:** `blocked_when_unavailable`

R1 must remain behaviorally identical for the existing approved HCE
path.

No existing R1 tests may be weakened or reinterpreted.

------------------------------------------------------------------------

## 3. R2 --- proposed second bounded family

R2 is derived only from the already-certified semantic family:

`exclusive_dependency_capability_loss_v1`

The grounded structure explicitly contains:

-   dependent → `dependency` → `exclusive`;
-   resource → `availability` → `unavailable`;
-   dependent → `alternative` → `absent`;
-   dependent → `capability` → `unavailable`.

The proposed abstraction normalization is:

**relation:** `exclusive_dependency`\
**outcome:** `capability_unavailable_without_alternative`

This wording deliberately describes the certified structural pattern.

It does **not** claim unrestricted causality.

It does not mean:

`exclusive_dependency causes capability loss` in every context.

It means only that repeated certified observations of this bounded rule
family may support the invariant:

> an exclusive dependency pattern with no alternative is associated with
> capability unavailability within the exact admitted scope.

------------------------------------------------------------------------

## 4. Why R2 is legitimate

R2 is not invented from one semantic slot.

It requires the complete certified family shape.

Admission requires the exact existing family ID plus the expected slot
set:

-   `dependency=exclusive`;
-   `availability=unavailable`;
-   `alternative=absent`;
-   `capability=unavailable`.

If any required slot is absent, ambiguous, duplicated, or inconsistent:

**NOT APPLICABLE / fail closed.**

------------------------------------------------------------------------

## 5. Why R2 is distinct from R1

R1 expresses a prerequisite/requirement structure:

`required_for → blocked_when_unavailable`

R2 expresses an exclusive-dependency/no-alternative structure:

`exclusive_dependency → capability_unavailable_without_alternative`

They are related but not interchangeable.

This distinction is sufficient to give HCC two conceptually different
canonical abstraction components without fabricating arbitrary semantic
diversity.

------------------------------------------------------------------------

## 6. Family identity contract

The normalized productive evidence must preserve which
abstraction-normalization family produced it.

Recommended explicit normalization family IDs:

-   `productive_abstraction:r1_required_for_blocked`
-   `productive_abstraction:r2_exclusive_dependency_no_alternative`

The existing raw grounding `family_id` should also remain available for
provenance.

Do not overload one field so that semantic-grounding family and
abstraction-normalization family become ambiguous.

A minimal implementation may therefore require a new bounded field such
as:

`normalization_family_id`

on `GovernedProductiveAbstractionEvidence`.

This is a representation extension, not a new authority.

------------------------------------------------------------------------

## 7. Normalization decision matrix

### VELAR family

`relational_prerequisite_capability_block_v1`

→ R1\
→ `required_for / blocked_when_unavailable`

### Exclusive dependency family

`exclusive_dependency_capability_loss_v1`

→ R2\
→ `exclusive_dependency / capability_unavailable_without_alternative`

### Unsupported family

→ `None / NOT_APPLICABLE`

No fallback guessing.

------------------------------------------------------------------------

## 8. Repetition rule

A single R2 grounding is not an abstraction.

The existing `GovernedRelationalAbstractionInducer.MINIMUM_SUPPORT`
remains authoritative.

Therefore:

one R2 observation → admitted / insufficient

two or more compatible R2 observations → existing inducer may produce R2
abstraction candidate.

No new inducer.

------------------------------------------------------------------------

## 9. Accumulation isolation

This is the most important implementation detail.

R1 and R2 evidence must not be pooled into one inducer call merely
because they share a scope.

The current accumulator is scope-keyed only.

Multi-family normalization requires evidence partitioning by:

**session + scope + normalization family**

or an equivalent bounded key.

Otherwise mixed R1/R2 evidence would cause the existing inducer to
return `NO_ABSTRACTION` due to multiple relations/outcomes.

This is an existing-owner structural extension.

------------------------------------------------------------------------

## 10. Bounded state rule

Existing limits must remain.

`MAX_ITEMS_PER_SCOPE` and `MAX_SCOPES_PER_SESSION`

must not silently become unbounded because family partitioning is added.

If per-family buckets are introduced, total admitted state per
session/scope still needs a clear global cap.

No background accumulation.

No persistence.

------------------------------------------------------------------------

## 11. Counterexample rule

Counterexamples remain family-local.

An R1 counterexample must not contest R2.

An R2 counterexample must not contest R1.

The existing inducer remains responsible for evaluating counterexamples
inside each family.

------------------------------------------------------------------------

## 12. HCC eligibility contract

HCC must only consider multi-family diversity when there are at least
two distinct canonical abstraction episodes whose normalized pairs
differ.

For example:

R1: `required_for / blocked_when_unavailable`

R2: `exclusive_dependency / capability_unavailable_without_alternative`

Two R1 episodes are not "multi-abstraction diversity" merely because
they came from different turns.

This rule prevents fake conceptual richness.

------------------------------------------------------------------------

## 13. Learning boundary

R2 is **not automatically learnable**.

The existing `GovernedRelationalAbstractionLearningBridge` remains
bounded to the historically approved R1 family unless a separate future
contract explicitly extends Learning.

Therefore:

R2 productive abstraction → HCC/reasoning use allowed when governed

but NOT automatically:

R2 → Learning → Memory.

This separation is mandatory.

------------------------------------------------------------------------

## 14. Structural Transfer boundary

R2 does not automatically become transferable.

Structural Transfer remains untouched.

Any future transfer eligibility for R2 requires a separate CAP-08
audit/contract.

------------------------------------------------------------------------

## 15. Epistemic boundary

R2 remains:

-   candidate;
-   reviewable/contested;
-   non-truth-establishing;
-   read-only;
-   session-local.

No new epistemic authority.

------------------------------------------------------------------------

## 16. RED evidence

The RED artifact records:

1.  current certified grounding families collapse to the same R1 pair;
2.  no distinct R2 exists;
3.  no explicit normalization-family identity exists;
4.  R2 relation/outcome contract is absent;
5.  repeated R2 evidence cannot produce a distinct abstraction;
6.  R1 and R2 cannot yet coexist productively for HCC;
7.  unsupported families still fail closed.

The first and last tests pass today and document existing behavior.

The unmet future contracts are strict `xfail`.

------------------------------------------------------------------------

## 17. GREEN implementation sequence

### MF-GREEN-1

Add explicit normalization-family identity to productive abstraction
evidence.

### MF-GREEN-2

Split normalization: - VELAR → R1 - exclusive dependency → R2 -
unsupported → none.

### MF-GREEN-3

Partition transient accumulation by normalization family while
preserving global bounds.

### MF-GREEN-4

Prove repeated R2 evidence induces via the existing inducer and R1
remains unchanged.

### MF-GREEN-5

Expose HCC eligibility only when two distinct abstraction-family
episodes exist.

### STOP

No Learning or Structural Transfer extension in this block.

------------------------------------------------------------------------

## 18. Required GREEN tests

At minimum:

-   R1 mapping unchanged;
-   R2 exact mapping;
-   incomplete R2 slot shape rejected;
-   unsupported family rejected;
-   one R2 item insufficient;
-   two R2 items induce;
-   duplicate R2 evidence does not inflate support;
-   R1/R2 accumulation isolated;
-   R1 counterexample does not contest R2;
-   R2 counterexample does not contest R1;
-   global bounds preserved;
-   deterministic fingerprints;
-   no Memory;
-   no Learning;
-   no Structural Transfer;
-   HCC receives distinct R1/R2 episode identities only when both exist.

------------------------------------------------------------------------

## 19. Promotion rule

No promotion until:

1.  focused MF tests green;
2.  existing semantic-grounding tests green;
3.  existing CAP-07 R1 tests green;
4.  HCC tests green;
5.  Ruff clean;
6.  full pytest clean;
7.  Master Capability Registry updated;
8.  Deep Surgical Map updated;
9.  Learning bridge remains unchanged unless separately authorized.

------------------------------------------------------------------------

## 20. Final verdict

**CONTRACT: READY**\
**RED RESIDUAL: DEMONSTRATED**\
**NEW AUTHORITY: NOT JUSTIFIED**\
**PRODUCTION CODE: NOT YET MODIFIED**

The next safe block is:

# CAP-07 Multi-Family Productive Abstraction Normalization --- GREEN-1 → GREEN-4

That block should implement only:

**family identity → R1/R2 normalization → family-isolated bounded
accumulation → repeated R2 induction using the existing inducer**

and stop before Learning or Structural Transfer.
