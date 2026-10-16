# ROBY XI.2 --- CAP-07 Governed Productive Abstraction Admission Contract & RED Evidence

**Baseline:** corrected full ZIP with Master Capability Registry,
Cognitive Inventory Reconciliation Master Surgical Guide, and CAP-07
Deep Surgical Capability Map in project root.\
**Mode:** contract design + external RED evidence. No production code
was modified.\
**Authority:** `governed_reasoning`.

------------------------------------------------------------------------

## 1. Decision

The Productive Reachability Trace proved that CAP-07 has a real
upstream/downstream gap:

**productive grounded evidence** → **canonical relational examples** →
**selective abstraction induction** → **read-only productive
consumption**

The existing `GovernedRelationalAbstractionInducer` must be reused
unchanged unless a later RED test proves an actual defect in its
contract.

The new work is therefore **admission/wiring**, not a second abstraction
engine.

------------------------------------------------------------------------

## 2. Contract name and placement

Proposed bounded owner file:

`core/governed_reasoning/productive_abstraction_admission.py`

This is not a new authority. It is an adapter/lifecycle component
subordinated to `governed_reasoning`.

Proposed public contract types:

-   `ProductiveAbstractionAdmissionStatus`
-   `GovernedProductiveAbstractionEvidence`
-   `GovernedProductiveAbstractionAdmissionResult`
-   `CanonicalProductiveAbstractionEpisode`
-   `GovernedProductiveAbstractionAdmission`

Names are provisional until implementation review, but the
responsibilities are fixed by this contract.

------------------------------------------------------------------------

## 3. Source contract

V1 MUST NOT consume arbitrary free text.

It may consume only **already-certified grounded relational artifacts**
produced under the existing semantic-grounding ecosystem.

The adapter must derive a `RelationalAbstractionExample` without
inventing a new semantic interpretation.

Minimum provenance:

-   session/episode identity;
-   `scope_reference`;
-   source reference/fingerprint;
-   canonical grounded relation;
-   canonical outcome;
-   stable example identity.

If relation/outcome cannot be derived from an existing certified
artifact without reinterpretation, admission returns a fail-closed
status.

------------------------------------------------------------------------

## 4. Accumulation contract

Accumulation is:

-   session-local;
-   transient;
-   bounded;
-   keyed by exact scope;
-   deterministic;
-   idempotent by evidence identity/fingerprint.

It MUST NOT use:

-   Memory;
-   Learning persistence;
-   Knowledge persistence;
-   World Model mutation;
-   a new database/store.

V1 should use a small in-memory accumulator owned by the admission
component, analogous in spirit to existing session-local bounded intake
patterns.

------------------------------------------------------------------------

## 5. Trigger contract

The inducer is not called on every conversational turn.

Induction is eligible only when:

1.  at least two unique admitted supporting examples exist for one exact
    scope;
2.  each example has explicit provenance;
3.  all examples use the existing bounded relation/outcome vocabulary;
4.  no source identity is duplicated;
5.  the evidence set is stable enough to produce a deterministic
    fingerprint.

A single example yields an admitted/insufficient state, not an
abstraction.

------------------------------------------------------------------------

## 6. Counterexample contract

Counterexamples must also come from certified grounded evidence.

They are accumulated separately but under the same scope identity.

The admission component MUST NOT infer a counterexample merely because
text contains negation or lexical opposition.

The existing inducer remains responsible for deciding whether an
admitted counterexample actually contradicts the shared invariant.

------------------------------------------------------------------------

## 7. Canonical productive episode

`CanonicalProductiveAbstractionEpisode` must carry exact lineage
comparable to the existing productive reasoning/epistemic episode
contracts.

Required semantics:

-   `canonical_authority = "governed_reasoning"`
-   `read_only = True`
-   `session_local = True`
-   `persists = False`
-   `creates_memory = False`
-   `creates_learning = False`
-   `executes_transfer = False`
-   `grants_authority = False`

It should contain:

-   episode ID;
-   owner/session/turn lineage;
-   scope;
-   admitted evidence fingerprints;
-   abstraction candidate;
-   source fingerprint;
-   status/rationale.

No durable write is permitted in V1.

------------------------------------------------------------------------

## 8. Consumer contract

The first productive consumer is **consultative governed reasoning**,
not Learning and not Structural Transfer.

The episode may expose a read-only abstraction candidate to the existing
reasoning lifecycle.

It MUST NOT automatically:

-   register an inference rule;
-   create a learning candidate;
-   call `GovernedRelationalAbstractionLearningBridge`;
-   call structural transfer;
-   write Memory;
-   establish truth.

A later wave may explicitly connect a reviewable abstraction to the
already-certified learning bridge.

------------------------------------------------------------------------

## 9. Composition-root contract

The admission component may be instantiated beneath
`OfficialGovernedReasoningRuntimeGateway` or an adapter strictly owned
by that gateway.

It must not be attached directly to:

-   conversation entry;
-   generic capability routing;
-   Memory;
-   Knowledge persistence;
-   every-turn hooks outside reasoning governance.

The gateway decides whether an eligible certified grounded artifact is
offered to the admission component.

------------------------------------------------------------------------

## 10. Status model

Recommended V1 statuses:

-   `NOT_APPLICABLE`
-   `ADMITTED`
-   `DUPLICATE`
-   `INSUFFICIENT_EVIDENCE`
-   `ABSTRACTION_AVAILABLE`
-   `CONTESTED`
-   `ABSTAIN`

The exact enum may be refined, but it must distinguish admission state
from the existing `RelationalAbstractionStatus`; the adapter must not
replace the inducer's epistemic result.

------------------------------------------------------------------------

## 11. Hard invariants

1.  One authority: `governed_reasoning`.
2.  No arbitrary text interpretation.
3.  No duplicate semantic grounder.
4.  No duplicate abstraction inducer.
5.  No persistence.
6.  No automatic learning.
7.  No automatic transfer.
8.  Exact scope isolation.
9.  Exact provenance.
10. Idempotent repeated evidence.
11. Deterministic candidate identity.
12. Fail closed on ambiguity/missing provenance.
13. Bounded session-local state.
14. Existing inducer remains the only abstraction decision primitive.

------------------------------------------------------------------------

## 12. RED evidence

A RED test artifact was created outside the project baseline:

`test_cap_07_governed_productive_abstraction_admission_contract_red.py`

It deliberately references the not-yet-existing module:

`core.governed_reasoning.productive_abstraction_admission`

The artifact proves/records these residuals:

-   no productive admission module exists;
-   no grounded-evidence → canonical-example adapter exists;
-   no bounded session-local accumulation contract exists;
-   no productive abstraction episode exists;
-   no idempotence contract exists;
-   no cross-scope fail-closed admission exists;
-   no read-only productive consumer contract exists.

The first test explicitly verifies that the module is absent. The
remaining contract tests are marked strict `xfail` so the RED artifact
can be executed without contaminating the certified baseline.

------------------------------------------------------------------------

## 13. RED-to-GREEN implementation order

### GREEN-1 --- Contract dataclasses/status only

Add the bounded result/episode contracts with governance invariants. No
runtime wiring.

### GREEN-2 --- Certified evidence normalization

Add adapter from one existing grounded artifact family into
`RelationalAbstractionExample`.

### GREEN-3 --- Bounded session-local accumulation

Add scope isolation, deduplication, pruning/bounds, deterministic
ordering.

### GREEN-4 --- Selective induction

Call the existing `GovernedRelationalAbstractionInducer` only after
admission criteria are met.

### GREEN-5 --- Read-only productive episode

Return the candidate through a canonical episode without
persistence/learning/transfer.

### GREEN-6 --- Gateway wiring

Wire the component beneath `OfficialGovernedReasoningRuntimeGateway` at
one explicit eligible source point.

### GREEN-7 --- Productive consumer

Expose the episode consultatively to reasoning; still no durable
learning.

Only after GREEN-7 and full gates should Hierarchical Concept
Composition be reconsidered.

------------------------------------------------------------------------

## 14. Tests required for GREEN

At minimum:

1.  one grounded item does not induce;
2.  two unique compatible items induce;
3.  duplicate evidence does not inflate support;
4.  different scopes never co-accumulate;
5.  missing provenance fails closed;
6.  unsupported/ambiguous semantic grounding is not admitted;
7.  contradictory certified evidence reaches existing `CONTESTED`
    semantics;
8.  ordering does not change fingerprint;
9.  session separation is strict;
10. bounded accumulator cannot grow without limit;
11. result is read-only;
12. no Memory write;
13. no Learning creation;
14. no Structural Transfer call;
15. no rule registration;
16. no action execution;
17. gateway preserves existing behavior when admission is not
    applicable;
18. existing CAP-07/CAP-08/CAP-09 tests remain unchanged and green.

------------------------------------------------------------------------

## 15. Existing green perimeter

Before implementation, the current baseline still passes the focused
CAP-07 perimeter:

**33 PASS**

covering:

-   governed relational abstraction;
-   abstraction → approved learning → later reuse;
-   bounded semantic grounding;
-   structural knowledge transfer candidate.

This establishes the pre-change behavioral control.

------------------------------------------------------------------------

## 16. Promotion gates

No promotion until:

1.  new focused tests GREEN;
2.  existing 33-test CAP-07 perimeter GREEN;
3.  adjacent reasoning runtime tests GREEN;
4.  `ruff check .` clean;
5.  complete `pytest -q` returns at least the certified baseline plus
    legitimate new tests;
6.  root documentation updated;
7.  Master Capability Registry CAP-07 card updated;
8.  no parallel authority/persistence path introduced.

------------------------------------------------------------------------

## 17. Surgical verdict

**CONTRACT: READY.**\
**RED RESIDUAL: DEMONSTRATED.**\
**PRODUCTION IMPLEMENTATION: NOT YET PERFORMED.**

The next safe operation is:

# CAP-07 Productive Abstraction Admission --- GREEN-1 to GREEN-4

That first implementation block should stop after:

**contract + normalization + bounded accumulation + selective call to
the existing inducer**

and should still avoid composition-root wiring if the focused tests
reveal any contract ambiguity.

This preserves the project's rule:

> integration before expansion, one authority per capability, and
> minimum justified change.
