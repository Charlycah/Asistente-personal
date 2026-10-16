# ROBY XI.2 --- Hierarchical Concept Composition Pre-Implementation Reconciliation

**Baseline:** 13,452 PASS + Ruff clean\
**Sources reconciled:** Master Capability Registry + Cognitive Inventory
Reconciliation + CAP-07 Deep Surgical Map + current production code\
**Mode:** pre-implementation architecture decision; no code changes.

------------------------------------------------------------------------

## 1. Executive decision

# DECISION: NEW BOUNDED PRIMITIVE JUSTIFIED

A new bounded primitive is justified, but only as an **extension inside
the existing `governed_reasoning` authority**.

It must not become a new cognitive authority, storage system, ontology
engine, knowledge repository, or learning path.

The justified gap is:

> ROBY can now productively obtain one governed relational abstraction
> episode, but it still cannot canonically compose multiple governed
> relational abstractions into a single higher-order conceptual
> structure with hierarchy, component relations, local boundaries,
> counterevidence and deterministic provenance.

This is a representational gap, not a reachability gap.

------------------------------------------------------------------------

## 2. What already exists and must not be recreated

### Productive relational abstraction

Current productive path:

semantic grounding → productive abstraction admission → existing
`GovernedRelationalAbstractionInducer` → canonical productive
abstraction episode → consultative reasoning consumption.

This is now productively reachable and must remain the upstream source.

### Structural transfer

`GovernedStructuralKnowledgeTransferMatcher` already owns bounded
structural matching and role correspondence across domains.

Hierarchical Concept Composition must not perform transfer/analogy.

### Personal Knowledge

`PersonalKnowledgeBaseManager` owns persisted knowledge items and
explicit relations between items.

Its `KnowledgeRelation` model is a storage/knowledge relation, not an
inferred concept representation.

Concept composition must not use Personal Knowledge as its internal
concept graph or silently persist candidates there.

### Persistent World Model

`PersistentWorldModelView` represents governed facts and world
snapshots.

It is a world-state view, not a concept-formation engine.

Concept composition must not duplicate facts or create a second world
model.

### Learning

Existing Learning/Memory pathways already own durable learning.

A concept candidate must remain transient until a future explicit
learning contract is separately justified.

### Epistemic evaluation

Existing sufficiency/assessment contracts already own epistemic
judgments.

Concept composition may carry evidence/status, but must not invent a
second epistemic authority.

------------------------------------------------------------------------

## 3. Why current Relational Abstraction is insufficient

`GovernedRelationalAbstractionCandidate` currently represents one
invariant:

-   one `scope_reference`;
-   one `invariant_relation`;
-   one `invariant_outcome`;
-   supporting example IDs;
-   counterexample IDs;
-   confidence;
-   rationale;
-   source fingerprint.

It cannot represent a compound structure such as:

Concept C → abstraction A1 → abstraction A2 → relation between A1 and A2
→ parent concept P → child concept C1 → boundary condition B →
counterevidence attached only to A2.

Trying to overload the current candidate with this responsibility would
blur a deliberately bounded primitive and risk regressions in the
already-closed HCE abstraction contract.

Therefore the correct move is not to mutate the old candidate into a
universal concept object.

------------------------------------------------------------------------

## 4. Why Personal Knowledge relations do not close the gap

`PersonalKnowledgeBase` already supports `KnowledgeItem` and
`KnowledgeRelation`.

That structure is useful for persisted knowledge organization, but it
differs fundamentally from the desired concept candidate:

-   it is repository-oriented;
-   it links stored knowledge items;
-   it is not built from canonical abstraction episodes;
-   it does not represent component-level epistemic boundaries;
-   it is not a session-local reasoning product;
-   it does not preserve `governed_reasoning` as inferential authority.

Therefore:

> Knowledge relations may later reference an approved concept, but they
> are not the concept-composition primitive itself.

------------------------------------------------------------------------

## 5. Why World Model does not close the gap

`PersistentWorldFact` represents:

-   domain;
-   fact key/value;
-   source authority;
-   source reference;
-   epistemic level;
-   evidence.

`PersistentWorldSnapshot` is a read-only composite view of facts.

This supports representation of the known world, not abstraction
hierarchy.

A concept like "resource dependency" is not the same kind of object as
"device X currently depends on resource Y".

Therefore World Model is a possible evidence consumer/source in future,
but not the owner of concept composition.

------------------------------------------------------------------------

## 6. Why Structural Transfer does not close the gap

Structural transfer already represents correspondences between a known
source structure and a target structure.

Its responsibility is:

**map structure across domains**

not:

**compose several abstractions into one concept**.

If we use transfer to create the concept itself, CAP-08 would become a
concept owner and violate the one-authority boundary.

Thus the dependency remains:

relational abstractions → hierarchical concept composition → later
structural mapping/analogy.

Not the reverse.

------------------------------------------------------------------------

## 7. Canonical authority

# `governed_reasoning`

This is strongly justified because:

-   semantic grounding already belongs there;
-   relational abstraction already belongs there;
-   productive abstraction admission is now wired there;
-   structural transfer already belongs there;
-   the missing operation is inferential composition of reasoning
    products.

No new authority is justified.

------------------------------------------------------------------------

## 8. New primitive scope

The new primitive should do exactly one thing:

> compose multiple canonical governed relational abstraction episodes
> into a bounded, read-only hierarchical concept candidate.

It should not:

-   discover raw semantic relations;
-   reinterpret free text;
-   persist;
-   learn;
-   transfer;
-   act;
-   modify the world model;
-   modify personal knowledge;
-   create inference rules;
-   establish truth.

------------------------------------------------------------------------

## 9. Minimal candidate semantics

A justified V1 candidate needs only enough structure to prove the new
capability.

Suggested responsibilities:

-   `concept_id` / deterministic candidate identity;
-   `scope_reference`;
-   constituent abstraction episode IDs/fingerprints;
-   ordered component abstractions;
-   explicit component relationships;
-   optional parent reference;
-   optional child references;
-   component-level supporting evidence;
-   component-level counterevidence/boundary markers;
-   status/rationale;
-   source fingerprint;
-   canonical authority;
-   governance flags.

Do not add an ontology language.

Do not add arbitrary property bags unless a RED case requires them.

------------------------------------------------------------------------

## 10. Hierarchy semantics must remain bounded

V1 should support only a small, explicit hierarchy contract.

Recommended initial relation vocabulary:

-   `PARENT_OF`
-   `CHILD_OF`
-   `CONTAINS_COMPONENT`
-   `RELATED_COMPONENT`

Only if current evidence can justify those relations deterministically.

Do not implement:

-   open-ended taxonomies;
-   arbitrary graph reasoning;
-   recursive ontology inference;
-   automatic class/instance inference;
-   universal `IS_A` semantics.

Those can be studied later.

------------------------------------------------------------------------

## 11. Source contract

V1 source must be:

`CanonicalProductiveAbstractionEpisode`

or an equivalent canonical abstraction product from the existing CAP-07
path.

No raw conversation text.

No arbitrary `KnowledgeItem`.

No raw World Model fact.

No LLM-generated "concept description".

This ensures that concept composition starts only after abstraction has
already passed the governed admission path.

------------------------------------------------------------------------

## 12. Composition admission

A concept candidate may be attempted only when:

1.  at least two canonical abstraction episodes exist;
2.  they share a compatible scope or an explicitly governed scope
    relation;
3.  each has deterministic provenance;
4.  no episode is duplicated;
5.  all component abstractions are reviewable/eligible under existing
    abstraction semantics;
6.  the relationship between components is explicitly justified by
    evidence, not lexical similarity.

If those conditions are not met:

**ABSTAIN / INSUFFICIENT / NOT_COMPOSABLE**

rather than fabricating a concept.

------------------------------------------------------------------------

## 13. Counterevidence and local boundaries

This is one of the strongest reasons a new primitive is justified.

Current relational abstraction treats counterevidence at the invariant
level.

A compound concept needs local boundaries.

Example:

Concept C consists of A1 and A2.

Evidence may contest A2 while leaving A1 intact.

The concept candidate must preserve:

-   A1 supported;
-   A2 contested;
-   overall candidate partial/contested.

It must not collapse all evidence into one scalar confidence.

This should be explicit in the RED design.

------------------------------------------------------------------------

## 14. Productive consumption

The first consumer should again be consultative `governed_reasoning`.

The concept candidate can enrich reasoning context with something like:

> a governed higher-order conceptual structure is available, composed
> from these canonical abstractions, with these boundaries.

It must not automatically:

-   invoke Structural Transfer;
-   invoke Learning;
-   persist to Knowledge;
-   write Memory;
-   update World Model.

------------------------------------------------------------------------

## 15. Persistence decision

# NONE IN V1

This is mandatory.

If hierarchical concepts later prove useful enough to persist,
persistence must be a separate design:

concept candidate → epistemic evaluation → explicit learning/admission
policy → existing Learning authority → existing Memory/Knowledge
authority.

No `ConceptRepository` in V1.

------------------------------------------------------------------------

## 16. RED evidence required before production implementation

The RED suite should prove the following residuals:

1.  current relational abstraction cannot represent multiple constituent
    abstractions;
2.  current candidate cannot express parent/child composition;
3.  current candidate cannot attach counterevidence to one component
    without affecting all others;
4.  two canonical abstraction episodes can be accepted as inputs without
    raw-text reinterpretation;
5.  incompatible scopes fail closed;
6.  duplicate episodes do not inflate concept structure;
7.  input ordering does not change canonical concept identity;
8.  lexical similarity alone does not establish hierarchy;
9.  no Memory write;
10. no Learning creation;
11. no World Model mutation;
12. no Personal Knowledge persistence;
13. no Structural Transfer call;
14. authority remains `governed_reasoning`;
15. concept candidate can be consumed read-only by reasoning.

------------------------------------------------------------------------

## 17. Existing owner decision

Do not modify these existing owners except for explicit integration
points:

-   `relational_abstraction.py` --- upstream primitive remains bounded;
-   `structural_knowledge_transfer.py` --- downstream transfer remains
    separate;
-   `personal_knowledge_base.py` --- no concept storage;
-   `persistent_world_model.py` --- no concept storage;
-   Learning/Memory --- untouched in first wave.

Recommended new file boundary:

`core/governed_reasoning/hierarchical_concept_composition.py`

This is a **new primitive under an existing authority**, not a new
subsystem.

------------------------------------------------------------------------

## 18. Maturity classification after reconciliation

### Semantic grounding

CLOSED / PRODUCTIVE / BOUNDED.

### Relational abstraction

CLOSED / PRODUCTIVE / BOUNDED.

### Productive abstraction admission

CLOSED / PRODUCTIVE / READ-ONLY.

### Hierarchical concept composition

MISSING / JUSTIFIED NEW BOUNDED PRIMITIVE.

### Rich structural analogy

PARTIAL / WAITING ON CONCEPT COMPOSITION.

### Concept learning

NOT AUTHORIZED IN THIS PHASE.

------------------------------------------------------------------------

## 19. Anti-duplication decision table

  ------------------------------------------------------------------------------
  Existing        Reuse                          Modify now  Duplicate forbidden
  capability                                                
  --------------- -------------------- -------------------- --------------------
  Semantic        Yes                                    No                  Yes
  grounding                                                 

  Relational      Yes                                    No                  Yes
  abstraction                                               

  Productive      Yes                      Integration only                  Yes
  abstraction                                         later 
  admission                                                 

  Structural      Later consumer                         No                  Yes
  transfer                                                  

  Epistemic       Reuse                                  No                  Yes
  assessment                                                

  Personal        Future persistence                     No                  Yes
  Knowledge       consumer only                             

  World Model     Evidence/reference                     No                  Yes
                  only                                      

  Learning        Future explicit                        No                  Yes
                  bridge only                               

  Memory          Future governed                        No                  Yes
                  write only                                
  ------------------------------------------------------------------------------

------------------------------------------------------------------------

## 20. Surgical implementation sequence

### HCC-RED

Create only RED tests and contract documentation.

### HCC-GREEN-1

Add immutable candidate/status contracts with governance invariants.

### HCC-GREEN-2

Add deterministic composition of multiple canonical abstraction
episodes.

### HCC-GREEN-3

Add hierarchy/component relationship validation and local
boundary/counterevidence handling.

### HCC-GREEN-4

Add read-only productive concept episode, still isolated.

### HCC-GREEN-5

Wire consultative consumption beneath the existing reasoning gateway.

### STOP

Do not add transfer or persistence in the same block.

------------------------------------------------------------------------

## 21. Final verdict

# NEW BOUNDED PRIMITIVE JUSTIFIED

The codebase does not already contain an equivalent higher-order concept
composer.

The gap is not covered by:

-   relational abstraction;
-   Personal Knowledge relations;
-   Persistent World Model;
-   Structural Transfer;
-   Learning;
-   Memory.

The smallest architecturally valid next capability is therefore:

# Governed Hierarchical Concept Composition

under:

`governed_reasoning`

with:

-   canonical abstraction episodes as source;
-   transient/read-only candidate output;
-   no persistence;
-   no learning;
-   no transfer;
-   no second authority.

The next safe step is:

# Hierarchical Concept Composition --- Contract & RED Evidence

Only after that RED evidence should production code be written.
