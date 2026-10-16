# ROBY XI.2 --- HCC Ordinary Productive Multi-Abstraction Reachability Audit

**Baseline:** 13,468 PASS + Ruff clean\
**Mode:** read-only architectural audit; no production code or tests
modified.\
**Sources:** current code + Master Capability Registry + Cognitive
Inventory + CAP-07 Deep Surgical Map + HCC contract/implementation
documents.

------------------------------------------------------------------------

## 1. Executive verdict

# DECISION B --- EXISTING OWNER EXTENSION REQUIRED

The audit does **not** justify a new cognitive primitive.

The missing diversity is caused by a deliberately narrow normalization
boundary inside the existing CAP-07 owner:

`core/governed_reasoning/productive_abstraction_admission.py`

Current productive semantic grounding already carries more structured
relational information than reaches Relational Abstraction.

However, `normalize_grounding()` maps every admitted grounding family to
the same abstraction pair:

`required_for` → `blocked_when_unavailable`

Therefore ordinary productive runtime can accumulate many examples, but
they all become evidence for the **same relational abstraction family**.

HCC needs multiple distinct canonical abstractions. The bottleneck is
upstream normalization, not HCC itself.

------------------------------------------------------------------------

## 2. Productive path confirmed

The current ordinary productive chain is:

conversation / temporary relational rule intake →
`GovernedContextualRuleInterpretationProducer` →
`GovernedBoundedSemanticRoleRelationGrounder` → certified semantic
grounding →
`GovernedProductiveAbstractionAdmission.normalize_grounding()` →
`RelationalAbstractionExample` → `GovernedRelationalAbstractionInducer`
→ canonical productive abstraction episode → HCC candidate binding /
consultative concept consumption.

The path is real and governed.

The limitation is specifically between **semantic grounding** and
**relational abstraction example normalization**.

------------------------------------------------------------------------

## 3. Semantic Grounding already contains relational diversity

`ContextualSemanticRelation` currently includes:

-   `dependency`
-   `availability`
-   `alternative`
-   `capability`
-   `required_for`

The grounded candidate also preserves:

-   typed semantic roles;
-   typed semantic slots;
-   source spans;
-   family ID;
-   provenance;
-   scope;
-   deterministic source fingerprint.

Two certified grounding families are visible in the current bounded
grounder:

-   `exclusive_dependency_capability_loss_v1`
-   `relational_prerequisite_capability_block_v1`

The first family exposes slots such as:

-   dependent → dependency → exclusive
-   resource → availability → unavailable
-   dependent → alternative → absent
-   dependent → capability → unavailable

The second family exposes:

-   prerequisite → required_for → dependent
-   prerequisite → availability → unavailable
-   dependent → capability → unavailable

Therefore the semantic layer is **not semantically empty or
single-relation internally**.

------------------------------------------------------------------------

## 4. The exact collapse point

`GovernedProductiveAbstractionAdmission.normalize_grounding()` currently
defines:

`_SUPPORTED_RELATION = "required_for"`

`_SUPPORTED_OUTCOME = "blocked_when_unavailable"`

It accepts both certified semantic-grounding families, but then
constructs every `RelationalAbstractionExample` using exactly those two
constants.

Consequently:

-   family A becomes `required_for / blocked_when_unavailable`;
-   family B becomes `required_for / blocked_when_unavailable`;
-   different internal semantic slots are not preserved as distinct
    abstraction families.

This is the exact reason HCC cannot naturally receive multiple
semantically distinct productive abstractions from ordinary runtime.

------------------------------------------------------------------------

## 5. This collapse is deliberate, not accidental corruption

The restriction is consistent with the earlier HCE learning bridge.

`GovernedRelationalAbstractionLearningBridge._supported_statement()`
supports the same bounded family:

`required_for` + `blocked_when_unavailable`.

That historical constraint allowed HCE to prove:

abstraction → explicit approval → governed learning → Memory → later
structural reuse

without opening arbitrary generalized learning.

Therefore the current normalization should not be described as a bug.

It is a **former safety boundary that has now become too narrow for HCC
input diversity**.

------------------------------------------------------------------------

## 6. Why HCC must not solve this problem

`GovernedHierarchicalConceptComposer` correctly consumes canonical
abstraction episodes.

It must not reinterpret semantic slots itself.

If HCC tried to convert semantic grounding into new relations, it would
duplicate:

-   semantic grounding;
-   abstraction normalization;
-   abstraction admission.

That would create a second abstraction path and violate one-authority
discipline.

Therefore HCC remains unchanged.

------------------------------------------------------------------------

## 7. Why Semantic Grounding should not be expanded first

Semantic Grounding already produces differentiated, typed slots.

The audit does not demonstrate a missing semantic primitive at this
stage.

Adding more grammar families before preserving the distinctions already
present would be premature expansion.

The first surgical move belongs downstream:

# Productive Abstraction Admission normalization

Reuse what Semantic Grounding already knows.

------------------------------------------------------------------------

## 8. Correct owner for the extension

# `GovernedProductiveAbstractionAdmission`

Specifically its normalization contract.

The extension should preserve:

-   existing semantic grounder;
-   existing `RelationalAbstractionExample`;
-   existing inducer;
-   existing session-local accumulation;
-   existing productive abstraction episode;
-   existing HCC composer.

No new authority is required.

------------------------------------------------------------------------

## 9. What the extension must NOT do

It must not simply emit one abstraction example for every semantic slot.

That would confuse:

**a fact/slot inside one grounded rule**

with:

**a repeated invariant across multiple examples**.

The current `GovernedRelationalAbstractionInducer` requires multiple
examples sharing one relation and outcome.

Therefore each future abstraction family needs a clear normalization
rule that says:

> which grounded semantic pattern counts as one repeatable relational
> observation?

Only then may two or more observations induce a canonical abstraction.

------------------------------------------------------------------------

## 10. Safe expansion strategy

The safest strategy is incremental.

Keep the existing family unchanged:

### Family R1

`required_for` → `blocked_when_unavailable`

Then introduce **one additional abstraction-normalization family at a
time**, derived from already-certified semantic slots.

Candidate families for design review include concepts equivalent to:

### Family R2 --- dependency constraint

A grounded exclusive dependency relation repeatedly associated with
capability loss/degradation.

### Family R3 --- alternative absence constraint

A grounded absence-of-alternative relation repeatedly associated with
loss/blocking.

These names/semantics are not yet implementation authorization.

The exact `relation` and `outcome` strings must be fixed by Contract &
RED evidence before production code.

------------------------------------------------------------------------

## 11. Important epistemic rule

Do not derive a new abstraction family merely because a semantic slot
has a different enum value.

For example:

`availability = unavailable`

is a grounded local condition.

It is not automatically a reusable abstraction such as:

`unavailability_causes_failure`.

Causality/generalization must not be fabricated.

The adapter may only normalize a family whose higher-order semantics are
already explicit in the certified grounded rule structure.

------------------------------------------------------------------------

## 12. Productive diversity requirement for HCC

HCC should be considered naturally reachable only when ordinary runtime
can produce, within one compatible scope:

-   abstraction episode A with canonical invariant R1/O1;
-   abstraction episode B with canonical invariant R2/O2;
-   R1/O1 != R2/O2 in semantically meaningful terms;
-   both derived from certified grounded evidence;
-   no manual test-only construction;
-   no duplicate/relabelled equivalent abstraction.

Only then should the runtime attempt an HCC composition candidate.

------------------------------------------------------------------------

## 13. Current HCC productive status after this audit

### Downstream path

**CLOSED / PRODUCTIVE**

already-governed HCC candidate → canonical productive concept episode →
gateway → reasoning contributor.

### Upstream automatic concept generation

**NOT YET CERTIFIED**

because productive abstraction normalization collapses admitted evidence
into one abstraction family.

Therefore current HCC should be described as:

> productively consumable, but ordinary multi-abstraction source
> diversity remains bounded upstream.

------------------------------------------------------------------------

## 14. Tests supporting the audit

The focused audit perimeter covering:

-   bounded semantic grounding;
-   VELAR semantic grounding;
-   productive abstraction admission;
-   productive abstraction gateway;
-   HCC composition;
-   HCC productive concept gateway;
-   governed relational abstraction;

remains green.

No production changes were required to expose the bottleneck.

------------------------------------------------------------------------

## 15. Surgical Change Record

  ------------------------------------------------------------------------------
  Field                               Decision
  ----------------------------------- ------------------------------------------
  Requested behavior                  Allow ordinary runtime to produce multiple
                                      semantically distinct canonical
                                      abstractions for HCC

  Current owner                       `GovernedProductiveAbstractionAdmission`

  Current state                       Productive but single normalized
                                      abstraction family

  Upstream source                     Existing certified semantic grounding

  Existing inducer                    Reuse unchanged

  HCC                                 Reuse unchanged

  Persistence                         NONE

  Learning                            NONE in this extension

  Structural Transfer                 NONE

  Exact residual                      `normalize_grounding()` collapses all
                                      supported groundings to one
                                      relation/outcome family

  Change class                        Existing capability deepening

  New authority                       NOT JUSTIFIED

  Semantic-grounder expansion         NOT YET JUSTIFIED
  ------------------------------------------------------------------------------

------------------------------------------------------------------------

## 16. Required next contract

The next safe step is:

# CAP-07 Multi-Family Productive Abstraction Normalization --- Contract & RED Evidence

That contract must define:

1.  exact second normalization family;
2.  exact certified grounding pattern that admits it;
3.  exact `relation` and `outcome` semantics;
4.  how it differs from R1;
5.  how repeated evidence induces it using the existing inducer;
6.  fail-closed cases;
7.  no causality fabrication;
8.  no automatic Learning;
9.  no Structural Transfer;
10. HCC eligibility only after two genuinely distinct canonical
    abstraction episodes exist.

------------------------------------------------------------------------

## 17. RED evidence required

At minimum the RED suite should prove:

-   today two different certified grounding families still normalize to
    the same R1/O1 pair;
-   no second productive abstraction family exists;
-   HCC must reject/effectively avoid fake diversity based only on
    duplicate R1 abstractions;
-   a proposed R2 must originate from an explicit certified semantic
    pattern;
-   unsupported slots cannot become abstraction families;
-   repeated R2 evidence is required before an R2 abstraction episode
    exists;
-   R1 behavior remains unchanged;
-   no Learning/Memory/Transfer/persistence is added.

------------------------------------------------------------------------

## 18. Decision against alternative paths

### A --- ALREADY CAPABLE / WIRING RESIDUAL

**Rejected.**

The relevant paths are already wired. The source information is
collapsed before abstraction diversity exists.

### B --- EXISTING OWNER EXTENSION REQUIRED

# **SELECTED**

The existing productive abstraction admission owner is the correct
location.

### C --- NEW COGNITIVE PRIMITIVE JUSTIFIED

**Rejected.**

No new cognition is required yet. Existing semantic structure + existing
inducer are sufficient foundations.

### D --- DO NOT EXPAND

**Rejected as global decision, retained as safety rule.**

Expansion is justified only if the next contract can define a
semantically legitimate second abstraction family without fabricating
causality/generalization.

------------------------------------------------------------------------

## 19. Final conclusion

The audit reveals a useful architectural fact:

> ROBY already sees more relational structure than its productive
> abstraction layer currently preserves.

The bottleneck is not intelligence in Semantic Grounding and not
Hierarchical Concept Composition.

It is a deliberately narrow adapter that was originally designed to
support one safe HCE learning family.

The correct next evolution is therefore not another cognitive module.

It is a surgical deepening of the existing CAP-07 normalization
boundary:

**preserve a second legitimate abstraction family from already-certified
semantic evidence, prove it with RED, keep the existing inducer, and
only then allow ordinary HCC composition from genuinely diverse
abstractions.**

This is exactly an **integration-before-expansion** case.
