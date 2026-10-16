# ROBY XI.2 — HCC Productivo Ordinario

## Multi-Abstraction → Composition → Productive Concept Episode

**Entry baseline:** 13,477 PASS + Ruff clean.

## Objective

Close ordinary productive reachability from genuinely distinct relational
abstraction families to the already-governed HCC composer and canonical productive
concept episode, without adding a cognitive authority.

## Implemented path

Ordinary productive turn
→ certified semantic grounding
→ `GovernedProductiveAbstractionAdmission`
→ canonical R1/R2 abstraction episode
→ session/scope-local distinct-family collection
→ `GovernedHierarchicalConceptComposer`
→ `GovernedHierarchicalConceptCandidate`
→ existing `bind_productive_concept_candidate`
→ `CanonicalProductiveConceptEpisode`
→ existing `CanonicalProductiveReasoningSource`
→ consultative concept context.

## Architectural ownership

No new authority is introduced.

- semantic grounding remains owned by the existing governed grounder;
- abstraction admission remains owned by `GovernedProductiveAbstractionAdmission`;
- composition remains owned by `GovernedHierarchicalConceptComposer`;
- productive binding remains owned by `OfficialGovernedReasoningRuntimeGateway`;
- reasoning consumption remains owned by the existing reasoning runtime source/contributor.

The gateway only performs bounded orchestration of already-governed outputs.

## Anti-fabrication rule

Ordinary HCC composition requires two different abstraction semantic pairs:

`(invariant_relation, invariant_outcome)`.

Repeated episodes of the same pair replace the latest family-local episode but do
not count as conceptual diversity.

The current ordinary composer uses exactly the current abstraction plus one
deterministically selected distinct abstraction from the same owner/session/scope.

## Isolation

The transient collection key is:

`owner + session + scope`

and family identity is represented by the normalized invariant
`relation + outcome` pair.

No cross-session or cross-scope composition is admitted.

## Governance boundaries

Unchanged:

- read-only;
- session-local;
- no persistence;
- no Memory;
- no Learning;
- no World Model mutation;
- no Personal Knowledge mutation;
- no Structural Transfer;
- no rule registration;
- no action execution;
- no new authority.

## Focused validation

Five new end-to-end architecture tests prove:

1. ordinary R1 + R2 reaches a productive HCC concept episode;
2. repeated same-family evidence cannot fabricate diversity;
3. session/scope isolation;
4. same-turn concept reaches consultative reasoning source references/context;
5. governance boundaries remain closed.

Expanded affected perimeter: **87 PASS**.

`py_compile` passed for modified production and block-test files.

Ruff could not be executed in the assistant environment; official promotion remains
the user's local gate:

`ruff check .`
`pytest -q`

If the complete suite has no unrelated changes, expected test count is
**13,482 PASS**.
