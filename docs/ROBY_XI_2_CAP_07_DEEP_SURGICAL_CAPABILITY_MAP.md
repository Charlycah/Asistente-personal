# ROBY XI.2 --- Deep Surgical Capability Map

## CAP-07 --- Relational Abstraction / Concept Foundation

**Baseline:** 13,439 PASS + Ruff clean\
**Mode:** read-only architecture audit; no production modification\
**Purpose:** establish the exact ownership, API, reachability,
persistence boundary, tests, dependencies, and residual before
Hierarchical Concept Composition.

------------------------------------------------------------------------

## 1. Executive finding

CAP-07 is **not one capability at one maturity level**. It contains
three distinct layers:

1.  **Contextual semantic grounding** --- productively wired and reused
    by application/runtime paths.
2.  **Governed relational abstraction induction** --- implemented,
    deterministic, contract-tested, but in this focused scan its inducer
    is referenced only by its defining module and architecture tests; no
    direct `app/` or other `core/` productive caller was found.
3.  **Abstraction → governed learning bridge** --- implemented and
    tested in an end-to-end architecture scenario, but the bridge itself
    likewise has no direct productive caller outside tests in this scan.

Therefore the safe classification is:

> **Semantic grounding: SUBSTANTIAL / PRODUCTIVELY WIRED.**\
> **Relational abstraction: FOUNDATION / ARCHITECTURALLY PROVEN,
> productive runtime reachability not yet demonstrated by this map.**\
> **Abstraction learning/reuse: CLOSED-LOOP ARCHITECTURE EVIDENCE, but
> not equivalent to proof that ordinary runtime autonomously reaches
> abstraction induction.**

This distinction is critical before adding hierarchical concepts.

------------------------------------------------------------------------

## 2. Canonical authority

**Owner:** `governed_reasoning`

The semantic grounding candidate and relational abstraction candidate
both enforce:

`canonical_authority = "governed_reasoning"`

The abstraction candidate additionally enforces:

-   read-only;
-   session-local;
-   no persistence;
-   no Memory creation/modification;
-   no Learning creation/modification;
-   no truth establishment;
-   no inference authorization;
-   no rule registration;
-   no execution;
-   no authority grant.

**Decision:** Hierarchical Concept Composition, if implemented, should
extend this reasoning authority rather than create `ConceptBrain`,
`ConceptManager`, `OntologyAuthority`, or another cognitive owner.

------------------------------------------------------------------------

## 3. Primary implementation ownership

### 3.1 Semantic grounding

`core/governed_reasoning/contextual_semantic_grounding.py`

Principal public types:

-   `ContextualSemanticGroundingStatus`
-   `ContextualSemanticRole`
-   `ContextualSemanticRelation`
-   `ContextualSemanticRoleMention`
-   `ContextualSemanticSlot`
-   `GovernedContextualSemanticGroundingCandidate`
-   `GovernedBoundedSemanticRoleRelationGrounder`

Primary operation:

`GovernedBoundedSemanticRoleRelationGrounder.ground(...)`

This is a bounded semantic grammar, not a general ontology.

### 3.2 Relational abstraction

`core/governed_reasoning/relational_abstraction.py`

Principal public types:

-   `RelationalAbstractionStatus`
-   `RelationalAbstractionExample`
-   `GovernedRelationalAbstractionCandidate`
-   `GovernedRelationalAbstractionInducer`

Primary operation:

`GovernedRelationalAbstractionInducer.induce(...)`

Current candidate represents one bounded invariant through:

-   `scope_reference`
-   `invariant_relation`
-   `invariant_outcome`
-   supporting example IDs
-   counterexample IDs
-   confidence
-   rationale codes
-   source fingerprint.

### 3.3 Learning bridge

`app/governed_relational_abstraction_learning_bridge.py`

Principal type:

-   `GovernedRelationalAbstractionLearningBridge`

Primary operation:

`evaluate(abstraction)`

The bridge reuses existing:

-   `LearningFoundation`
-   `PreferenceLearning`
-   `SafeLearningPolicies`

It does not create a new Learning authority.

------------------------------------------------------------------------

## 4. Public/import surface

A focused inspection of `core/governed_reasoning/__init__.py` shows that
the semantic-grounding types are exported there.

The relational abstraction and abstraction-learning bridge types are
**not exported through that package `__init__` in the inspected
baseline**; tests import them from their concrete modules.

This is useful evidence that relational abstraction is architecturally
more isolated than semantic grounding.

**Surgical implication:** do not expand the package public API merely to
make a new feature convenient. First decide the intended productive
integration route.

------------------------------------------------------------------------

## 5. Productive caller map

### Semantic grounding --- confirmed productive references

The semantic grounder is referenced by production/application code
including:

-   `app/productive_temporary_rule_intake.py`
-   `app/approved_learning_memory_materialization.py`
-   `core/governed_reasoning/recalled_knowledge_structural_projection.py`

It is also protected by a substantial Post-M409 architecture-test
family.

This establishes real reuse beyond isolated tests.

### Relational abstraction inducer --- focused reference result

`GovernedRelationalAbstractionInducer` was found in:

-   its defining module;
-   `tests/architecture/test_hce_governed_relational_abstraction_wave.py`;
-   `tests/architecture/test_hce_abstraction_approved_learning_later_novel_reuse.py`.

No direct application/runtime caller was found in this scan.

### Abstraction learning bridge --- focused reference result

`GovernedRelationalAbstractionLearningBridge` was found in:

-   its defining module;
-   `tests/architecture/test_hce_abstraction_approved_learning_later_novel_reuse.py`.

No direct application/runtime caller was found in this scan.

------------------------------------------------------------------------

## 6. What the existing closed-loop architecture test proves

`test_hce_abstraction_approved_learning_later_novel_reuse.py` explicitly
composes a chain containing:

relational abstraction induction\
→ abstraction learning evaluation\
→ explicit human approval evidence\
→ structural eligibility/materialization proposal\
→ `OfficialMemoryGateway`\
→ later recall\
→ structural projection/transfer on a novel domain.

This is strong architectural evidence that the products are compatible
and can participate in the governed learning/reuse loop.

However, the test itself manually invokes
`GovernedRelationalAbstractionInducer()` and
`GovernedRelationalAbstractionLearningBridge()`.

Therefore it does **not by itself prove** that ordinary productive
runtime traffic reaches those two operations automatically.

This map deliberately distinguishes:

**closed-loop composability** from **runtime reachability**.

------------------------------------------------------------------------

## 7. Relational abstraction contract

The inducer is deterministic and fail-closed.

Minimum support:

`MINIMUM_SUPPORT = 2`

Current outcomes:

-   `INSUFFICIENT_EVIDENCE`
-   `NO_ABSTRACTION`
-   `REVIEW_REQUIRED`
-   `CONTESTED`
-   `ABSTAIN`

Important guards include:

-   unique example IDs;
-   common scope;
-   multiple supporting examples;
-   one shared relation;
-   one shared outcome;
-   explicit counterexamples;
-   contested status when a counterexample shares the relation but
    contradicts the outcome;
-   stable ordering before fingerprint/result construction.

A reviewable/contested candidate must expose a complete invariant and at
least two supporting examples.

A non-abstraction may not expose a partial invariant.

------------------------------------------------------------------------

## 8. Current representational ceiling

The existing abstraction is essentially:

> **within scope S, relation R repeatedly corresponds to outcome O.**

It does not canonically represent a composed concept with:

-   concept identity;
-   multiple constituent abstractions;
-   parent/child relations;
-   multiple internal relations;
-   necessary versus optional properties;
-   concept boundaries;
-   component-level counterevidence;
-   exceptions;
-   hierarchy depth;
-   concept-to-concept links.

This is the precise representational gap behind Hierarchical Concept
Composition.

------------------------------------------------------------------------

## 9. Learning boundary

The abstraction candidate itself cannot learn or persist.

The learning bridge accepts only an uncontested `REVIEW_REQUIRED`
abstraction and then reuses the existing M369 governed learning path.

More importantly, the inspected bridge supports only a specific
structural family:

`required_for` + `blocked_when_unavailable`

which is converted into the existing bounded rule statement.

Therefore:

> **the existence of the bridge is not permission for arbitrary concept
> learning.**

Any first hierarchical-concept implementation should remain
transient/read-only.

------------------------------------------------------------------------

## 10. Persistence/writer map

### Relational abstraction candidate

**Writers:** NONE.

### Learning bridge

Produces/evaluates governed learning artifacts but does not itself
bypass the established learning policy.

### Durable materialization

The end-to-end architecture test ultimately uses:

`OfficialMemoryGateway`

for durable memory write after explicit approval and
eligibility/materialization stages.

**Hard rule:** a future concept candidate must never write directly to
Memory, Knowledge persistence, or a new concept store.

------------------------------------------------------------------------

## 11. Structural-transfer dependency

CAP-07 is adjacent to, but must not absorb, CAP-08 Structural Transfer.

Existing structural-transfer families include:

-   recalled knowledge structural projection;
-   target problem structural projection;
-   structural knowledge transfer;
-   transfer admission guard;
-   transfer instantiation.

A hierarchical concept implementation must not recreate:

-   structural matching;
-   role correspondence;
-   target projection;
-   transfer admission.

The first concept wave should **compose representation**, not perform
rich analogy/transfer simultaneously.

------------------------------------------------------------------------

## 12. Contract-test surface

Direct relational-abstraction architecture tests identified:

-   `tests/architecture/test_hce_governed_relational_abstraction_wave.py`
-   `tests/architecture/test_hce_abstraction_approved_learning_later_novel_reuse.py`

Adjacent semantic/structural tests include Post-M409 suites for:

-   bounded semantic role/relation grounding;
-   contextual case grounding;
-   grammar compatibility;
-   structural eligibility;
-   recalled knowledge structural projection;
-   structural knowledge transfer candidate.

**Rule:** before modifying CAP-07, enumerate the exact adjacent
CAP-08/CAP-09 tests affected by imports or shared contracts, not only
tests containing `relational_abstraction` in the filename.

------------------------------------------------------------------------

## 13. Dependency direction

Current safe dependency direction is approximately:

explicit/bounded evidence\
→ contextual semantic grounding\
→ relational evidence/examples\
→ relational abstraction candidate\
→ optional governed learning evaluation\
→ explicit approval/policy\
→ official memory materialization\
→ recall\
→ structural projection/transfer.

A future hierarchy should fit conceptually as:

relational abstraction candidates\
→ **hierarchical concept composition candidate**\
→ epistemic/review boundary\
→ cognitive consumption.

Not:

free text\
→ concept truth\
→ concept memory.

------------------------------------------------------------------------

## 14. Exact residual

The residual is **not**:

"ROBY lacks concepts."

The residual is:

> **ROBY has a bounded primitive that induces one shared
> relation/outcome invariant from multiple explicit examples, but there
> is no canonical governed product that composes multiple legitimate
> abstractions into one higher-order concept structure with hierarchy,
> component relationships, boundaries, counterevidence and provenance.**

A second residual discovered by this surgical map is:

> **direct productive runtime reachability of
> `GovernedRelationalAbstractionInducer` and
> `GovernedRelationalAbstractionLearningBridge` has not been
> demonstrated by the focused reference scan, despite strong
> architecture-test evidence of their composability.**

This second residual must be resolved before deciding where a
hierarchical concept producer should be wired.

------------------------------------------------------------------------

## 15. Forbidden duplication list

Do not create:

-   `ConceptBrain`
-   `ConceptMemory`
-   `ConceptLearning`
-   `GeneralizationEngine`
-   `AnalogyEngine`
-   a second semantic grounder
-   a second abstraction inducer
-   a second structural matcher
-   a new persistence path
-   a second epistemic-status system merely for concepts.

------------------------------------------------------------------------

## 16. Surgical Change Record --- prefilled

  -----------------------------------------------------------------------
  Field                               Decision
  ----------------------------------- -----------------------------------
  Requested behavior                  Compose multiple governed
                                      abstractions into a higher-order
                                      hierarchical concept candidate.

  Registry capability                 CAP-07

  Current state                       FOUNDATION; semantic grounding
                                      productive, abstraction induction
                                      architecture-proven but productive
                                      reachability requires confirmation

  Canonical authority                 `governed_reasoning`

  Existing foundations                semantic grounding + relational
                                      abstraction + epistemic guards +
                                      structural transfer + governed
                                      learning bridge

  Productive entry                    **UNRESOLVED for abstraction
                                      inducer; must audit composition
                                      root/caller route before
                                      implementation**

  Productive consumer                 First consumer must be chosen
                                      explicitly; do not invent both
                                      producer and multiple consumers in
                                      one wave

  Writers                             NONE in first wave

  Persistence owner                   NONE in first wave

  Contract tests                      HCE relational abstraction +
                                      approved-learning/later-reuse +
                                      adjacent semantic/structural suites

  Residual                            No canonical multi-abstraction
                                      hierarchical concept product

  RED evidence                        Must prove multi-relation
                                      composition/hierarchy cannot be
                                      represented by current candidate

  Minimum change                      Extend `governed_reasoning` with
                                      one bounded composition
                                      primitive/product, only after
                                      reachability decision

  Forbidden duplication               semantic grounding, relational
                                      abstraction, structural transfer,
                                      Learning, Memory, epistemic
                                      authority

  Promotion                           focused RED/GREEN → adjacent
                                      architecture suites → Ruff → full
                                      pytest

  Rollback                            new concept files + explicit
                                      integration wiring only; existing
                                      abstraction/transfer contracts
                                      should remain unchanged unless
                                      separately justified
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 17. Required RED evidence before production code

At minimum:

1.  **Multi-abstraction composition** --- current
    `GovernedRelationalAbstractionCandidate` cannot represent two or
    more constituent invariants as one concept.
2.  **Hierarchy** --- parent/child structure cannot be represented
    canonically.
3.  **Boundary evidence** --- component-specific counterevidence cannot
    be represented without collapsing the whole abstraction.
4.  **Scope mismatch** --- incompatible abstractions fail closed.
5.  **Determinism** --- input ordering cannot change canonical concept
    identity.
6.  **No lexical shortcut** --- shared words alone do not establish
    conceptual composition.
7.  **No persistence** --- concept candidate writes nothing.
8.  **Authority preservation** --- remains `governed_reasoning`.
9.  **No transfer duplication** --- concept formation does not perform
    CAP-08 transfer.
10. **No learning shortcut** --- concept candidate cannot directly enter
    durable Memory.

------------------------------------------------------------------------

## 18. Next audit before implementation

Because runtime reachability is unresolved, the next surgical step
should be:

# **CAP-07 Productive Reachability & Composition-Root Trace**

It should answer exactly:

-   Where could relational abstraction legitimately be invoked in
    ordinary runtime?
-   Is there already a hidden/indirect factory or adapter not captured
    by direct symbol references?
-   Which canonical episode/source should produce
    `RelationalAbstractionExample` objects?
-   Which existing runtime object should consume the abstraction
    candidate?
-   Is the current abstraction intentionally
    architecture-only/selective, or is productive wiring incomplete?
-   Should hierarchy be wired at the same selective boundary or at a
    later consumer?

Only after that trace should RED tests for Hierarchical Concept
Composition be written.

------------------------------------------------------------------------

## 19. Surgical verdict

**CAP-07 AUDIT: PASS WITH REACHABILITY RESIDUAL**

The conceptual gap is real.

The authority is clear.

The persistence boundary is clear.

The anti-duplication boundaries are clear.

But productive reachability of the abstraction inducer itself is not yet
sufficiently demonstrated to authorize wiring a higher-order concept
primitive.

Therefore:

> **DO NOT IMPLEMENT HIERARCHICAL CONCEPT COMPOSITION YET.**

First complete the **CAP-07 Productive Reachability & Composition-Root
Trace**.

That is the smallest safe next move.


---

## CAP-07 GREEN-5 → GREEN-7 update

The former productive-reachability residual is now closed by the official reasoning
gateway path:

certified semantic grounding
→ productive abstraction admission
→ existing relational abstraction inducer
→ canonical read-only abstraction episode
→ `CanonicalProductiveReasoningSource`
→ `ReasoningRuntimeContributor` consultative context.

The path remains transient and does not create Memory, Learning, Structural Transfer,
rule registration, action execution, or a second authority.

The remaining CAP-07 residual is therefore representational rather than reachability:
ROBY still lacks canonical hierarchical composition of multiple governed abstractions.


---

## Hierarchical Concept Composition GREEN-1 → GREEN-4 update

The representational residual identified by this map now has an isolated bounded
implementation under `governed_reasoning`:

canonical abstraction episodes
→ deterministic component normalization
→ bounded hierarchy/component links
→ component-local counterevidence
→ read-only hierarchical concept candidate.

The implementation remains session-local and does not persist, learn, mutate the World
Model or Personal Knowledge, invoke Structural Transfer, register rules, execute actions,
or create a new authority.

**Remaining residual:** no canonical productive concept episode or gateway consumption is
wired yet.


---

## HCC GREEN-5 update — productive concept episode and consultative consumption

The downstream HCC reachability path is now wired:

already-governed HCC candidate
→ canonical productive concept episode
→ official reasoning gateway references
→ `CanonicalProductiveReasoningSource`
→ `ReasoningRuntimeContributor` consultative context.

This closes the **candidate-to-consumer** residual without persistence, Learning,
Memory, Structural Transfer, World Model/Personal Knowledge mutation, rule
registration, action execution, or a new authority.

A narrower upstream residual remains: the ordinary productive grounding path currently
certifies a bounded relational family and does not yet prove that multiple semantically
distinct abstraction families can arise naturally in one HCC scope. HCC must not compose
repeated equivalent abstractions merely to simulate conceptual diversity.


---

## CAP-07 Multi-Family Productive Abstraction GREEN-1 → GREEN-4 update

The former single-family normalization bottleneck has been deepened without adding a
new authority or inducer.

- Historical R1 remains `required_for → blocked_when_unavailable`.
- Certified VELAR grounding now forms bounded R2:
  `required_for → blocked_when_prerequisite_unavailable`.
- Evidence is accumulated per normalization family while one total scope bound remains.
- R1 and R2 counterevidence/support do not contaminate each other.
- Learning, Memory and Structural Transfer remain outside this extension.

This closes the normalization-diversity residual needed for ordinary HCC input.


---

## HCC Productivo Ordinario — Multi-Abstraction closure

Ordinary productive runtime now retains bounded distinct abstraction pairs per exact
owner/session/scope. When a current canonical abstraction has one genuinely distinct
compatible abstraction in the same scope, the existing
`GovernedHierarchicalConceptComposer` composes them and the existing gateway binds
the resulting candidate as a `CanonicalProductiveConceptEpisode` for same-turn
consultative reasoning consumption.

This closes the previously documented upstream ordinary multi-abstraction → HCC
reachability residual without adding a new authority, persistence, Learning, Memory
or Structural Transfer path.
