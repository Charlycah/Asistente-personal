# ROBY XI.2 — CAP-08 Rich Hierarchical Structural Analogy Block

**Entry baseline:** 13,482 PASS + Ruff clean.

## Reconciliation decision

CAP-08 already owns bounded structural transfer under `governed_reasoning`:

- `GovernedStructuralKnowledgeTransferMatcher` compares certified semantic
  groundings and target-problem projections;
- `GovernedTransferInstantiator` can instantiate a matched recalled rule;
- `GovernedTransferAdmissionGuard` delegates valid packages to the existing
  canonical temporary-rule admission boundary.

The existing path is mature and must not be replaced by a second Analogy Engine.

The residual after HCC Productivo Ordinario is narrower: CAP-08 had no primitive
that compares two `CanonicalProductiveConceptEpisode` objects as multi-component
hierarchical structures. The existing structural matcher accepts semantic
groundings/projections, not HCC concepts.

## Implemented bounded extension

`core/governed_reasoning/hierarchical_structural_analogy.py` adds a read-only
hierarchical structural comparison primitive under the same
`governed_reasoning` authority.

It compares:

- exact scope;
- distinct concept episodes;
- multi-component `(relation, outcome)` structure;
- HCC component correspondence;
- HCC link topology and relation type.

It returns an analogy candidate only when the two governed HCC structures are
compatible.

## Critical boundary with existing structural transfer

This block deliberately does **not** feed an HCC analogy candidate into
`GovernedTransferInstantiator` or `GovernedTransferAdmissionGuard`.

The old transfer path is executable only because it carries recalled durable-rule
compilation, target projection, role bindings and exact provenance required by
the canonical rule instantiator. An HCC concept episode does not carry that
executable rule lineage.

Therefore converting HCC analogy directly into a temporary rule would fabricate
semantics and weaken the existing transfer admission contract.

The new result explicitly states:

- `executes_transfer = False`;
- `authorizes_inference = False`;
- `registers_rule = False`;
- `establishes_truth = False`.

A later block may study a governed bridge from hierarchical analogy to
explanatory reasoning or to structural transfer, but only if exact role/rule
lineage can be demonstrated without invention.

## Anti-duplication

No new general analogy engine, reasoning authority, memory, learning system,
retrieval system or inference engine was introduced.

The new primitive is a CAP-08 extension whose source type is the HCC canonical
concept episode. Existing RC-1 transfer behavior remains unchanged.

## Validation

Eight new architecture tests cover:

1. cross-episode multi-component HCC structural analogy;
2. component-semantic mismatch rejection;
3. matching HCC link topology;
4. link-topology mismatch rejection;
5. same-episode rejection;
6. scope isolation;
7. strict non-transfer/non-learning/non-action boundaries;
8. deterministic result identity.

Expanded affected perimeter: **85 PASS**.

`py_compile` passed for all modified Python files.

Official promotion remains gated by local:

`ruff check .`
`pytest -q`

Expected full count if no unrelated test changes exist: **13,490 PASS**.
