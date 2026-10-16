# ROBY XI.2 --- Hierarchical Concept Composition --- Contract & RED Evidence

**Baseline:** 13,452 PASS + Ruff clean\
**Authority:** `governed_reasoning`\
**Mode:** pre-production contract + RED evidence; no production code
modification.

------------------------------------------------------------------------

## 1. Contract decision

The new capability is justified as a **bounded primitive under the
existing reasoning authority**.

It must compose multiple already-canonical productive abstraction
episodes into a single higher-order conceptual structure.

It is not:

-   semantic grounding;
-   relational abstraction;
-   structural transfer;
-   knowledge storage;
-   world-model storage;
-   learning;
-   memory;
-   ontology management.

------------------------------------------------------------------------

## 2. Source contract

V1 accepts only canonical abstraction products already emitted by
CAP-07.

Primary source:

`CanonicalProductiveAbstractionEpisode`

Each source episode must provide:

-   exact session/turn lineage;
-   exact scope;
-   canonical authority;
-   deterministic source fingerprint;
-   one existing `GovernedRelationalAbstractionCandidate`;
-   read-only/non-persistent governance.

No free text, raw LLM output, raw `KnowledgeItem`, or raw World Model
fact is accepted in V1.

------------------------------------------------------------------------

## 3. Composition status model

Recommended V1 statuses:

-   `INSUFFICIENT_COMPONENTS`
-   `SCOPE_MISMATCH`
-   `NOT_COMPOSABLE`
-   `REVIEW_REQUIRED`
-   `CONTESTED`
-   `ABSTAIN`

The composer must not invent a "success" status if the underlying
components remain epistemically contested.

A reviewable concept is still a candidate, not truth.

------------------------------------------------------------------------

## 4. Component contract

A concept consists of explicit governed components.

Each component minimally carries:

-   component ID;
-   abstraction episode ID;
-   abstraction fingerprint;
-   relation;
-   outcome;
-   component status;
-   supporting evidence IDs/fingerprints;
-   counterevidence IDs/fingerprints;
-   local rationale codes.

The purpose is to preserve **local epistemic boundaries**.

Counterevidence for one component must not silently invalidate unrelated
components.

------------------------------------------------------------------------

## 5. Hierarchy relation contract

V1 uses a small closed vocabulary only:

-   `PARENT_OF`
-   `CHILD_OF`
-   `CONTAINS_COMPONENT`
-   `RELATED_COMPONENT`

No arbitrary graph predicates.

No automatic taxonomy.

No universal `IS_A`.

No recursive ontology inference.

A relation is admitted only when supplied/derived by an explicit bounded
rule in the composer contract; lexical similarity alone is insufficient.

------------------------------------------------------------------------

## 6. Candidate contract

Proposed type:

`GovernedHierarchicalConceptCandidate`

Minimum responsibilities:

-   `concept_id`
-   `scope_reference`
-   ordered components
-   bounded hierarchy relations
-   optional parent concept reference
-   optional child concept references
-   overall status
-   rationale codes
-   source fingerprint
-   exact constituent episode IDs/fingerprints

Governance flags:

-   `canonical_authority = "governed_reasoning"`
-   `read_only = True`
-   `session_local = True`
-   `persists = False`
-   `creates_memory = False`
-   `creates_learning = False`
-   `modifies_world_model = False`
-   `modifies_personal_knowledge = False`
-   `executes_transfer = False`
-   `registers_rule = False`
-   `executes_actions = False`
-   `grants_authority = False`

------------------------------------------------------------------------

## 7. Determinism contract

Concept identity must be stable across equivalent input ordering.

Required normalization:

-   constituent episodes sorted by canonical episode
    identity/fingerprint;
-   component IDs derived deterministically;
-   relation tuples normalized deterministically;
-   final source fingerprint derived only from normalized governed
    inputs.

No timestamps or random UUIDs may determine conceptual identity.

------------------------------------------------------------------------

## 8. Admission rules

Composition is attempted only when:

1.  at least two unique canonical abstraction episodes are supplied;
2.  each episode belongs to `governed_reasoning`;
3.  each is read-only and non-persistent;
4.  each contains a complete reviewable/contested relational
    abstraction;
5.  all episodes share one compatible exact scope in V1;
6.  no episode/fingerprint is duplicated;
7.  the requested component/hierarchy relation is supported by the
    bounded V1 relation contract.

If any mandatory condition fails, return a fail-closed status.

------------------------------------------------------------------------

## 9. Scope rule

V1 requires exact same `scope_reference`.

Cross-scope concept composition is explicitly out of scope.

A future scope-bridging contract may be studied later, but must not be
inferred implicitly.

------------------------------------------------------------------------

## 10. Counterevidence rule

The composer preserves counterevidence by component.

Example:

-   component A: reviewable;
-   component B: contested;
-   component C: reviewable.

The concept may become `CONTESTED` overall, but the candidate must
preserve which component caused that state.

Do not collapse evidence into one opaque confidence score.

------------------------------------------------------------------------

## 11. Productive episode contract

A later GREEN stage may introduce:

`CanonicalProductiveConceptEpisode`

It must carry:

-   owner/session/turn lineage;
-   concept candidate;
-   source abstraction episode IDs;
-   source fingerprint;
-   canonical authority;
-   read-only/transient governance.

It must not persist or trigger learning/transfer.

------------------------------------------------------------------------

## 12. First consumer

The first consumer remains consultative governed reasoning.

The concept may enrich reasoning context with:

-   concept identity;
-   component relations;
-   boundaries;
-   contested areas.

It must not automatically invoke:

-   Structural Transfer;
-   Learning;
-   Memory;
-   Personal Knowledge persistence;
-   World Model update.

------------------------------------------------------------------------

## 13. Explicit anti-duplication boundaries

### Semantic grounding

Reuse only. No second grounder.

### Relational abstraction

Reuse only. No second inducer.

### Productive abstraction admission

Reuse only as source path.

### Structural transfer

Do not call during composition.

### Personal Knowledge

Do not persist concept candidates.

### Persistent World Model

Do not encode concept candidates as facts.

### Learning/Memory

No V1 use.

### Epistemic assessment

Reuse semantics/statuses where appropriate; do not create another
epistemic authority.

------------------------------------------------------------------------

## 14. RED evidence matrix

The RED artifact records nine absent contracts:

1.  no HCC module;
2.  no hierarchical candidate;
3.  no multi-abstraction composer;
4.  no bounded hierarchy relation model;
5.  no component-local boundary model;
6.  no deterministic concept identity;
7.  no fail-closed composition status model;
8.  no explicit no-persistence/no-learning/no-transfer governance
    fields;
9.  no canonical productive concept episode.

The RED artifact is intentionally external to the certified baseline and
uses strict `xfail` for not-yet-implemented contracts.

------------------------------------------------------------------------

## 15. RED-to-GREEN sequence

### HCC-GREEN-1

Add immutable enums/dataclasses and governance invariants only.

### HCC-GREEN-2

Add deterministic multi-episode normalization and component
construction.

### HCC-GREEN-3

Add bounded hierarchy relation validation, local counterevidence, and
overall status derivation.

### HCC-GREEN-4

Add isolated composer returning a read-only candidate.

### HCC-GREEN-5

Add canonical productive concept episode and consultative gateway
consumption.

### STOP

No transfer or persistence in this wave.

------------------------------------------------------------------------

## 16. Required GREEN tests

At minimum:

-   one episode → insufficient;
-   two unique compatible episodes → reviewable candidate;
-   duplicate episode rejected/deduplicated;
-   order independence;
-   exact-scope enforcement;
-   unsupported hierarchy relation rejected;
-   lexical similarity alone irrelevant;
-   one contested component preserved locally;
-   overall contested state derived without erasing supported
    components;
-   no Memory;
-   no Learning;
-   no Personal Knowledge write;
-   no World Model mutation;
-   no Structural Transfer call;
-   no rule registration;
-   authority remains `governed_reasoning`;
-   deterministic concept fingerprint;
-   read-only productive episode later reuses the same candidate
    identity.

------------------------------------------------------------------------

## 17. Existing green perimeter before implementation

The current pre-HCC perimeter remains:

**68 PASS**

covering:

-   CAP-07 productive abstraction admission;
-   CAP-07 gateway consumption;
-   governed relational abstraction;
-   approved learning/later reuse;
-   structural transfer;
-   Personal Knowledge;
-   Persistent World Model.

This is the behavioral control for the next implementation.

------------------------------------------------------------------------

## 18. Promotion rule

No HCC promotion until:

1.  RED cases are converted to focused GREEN tests;
2.  existing 68-test perimeter remains green;
3.  adjacent reasoning runtime tests remain green;
4.  Ruff clean;
5.  full pytest clean;
6.  Master Capability Registry updated;
7.  Cognitive Inventory/Deep Surgical documentation reconciled;
8.  no new authority or persistence path appears.

------------------------------------------------------------------------

## 19. Verdict

**CONTRACT: READY**\
**RED RESIDUAL: DEMONSTRATED**\
**PRODUCTION CODE: NOT YET IMPLEMENTED**

The next safe implementation block is:

# Hierarchical Concept Composition --- GREEN-1 → GREEN-4

That block should stop after:

**contracts → deterministic composition → bounded hierarchy/local
boundaries → isolated read-only candidate**

and should not yet wire production gateway consumption if any ambiguity
appears during focused tests.
