# ROBY XI.2 — Cross-Domain Concept Synthesis — Governed Productive Reachability

**Entry baseline:** 13,514 PASS + Ruff clean (user-certified).

## Architectural decision

CAP-19 is closed as an existing-owner extension under `governed_reasoning`.
`knowledge_runtime` remains the authority for knowledge sourcing/provenance and
`CrossDomainCoordinator` remains operational blackboard coordination; neither is
turned into a new reasoning engine.

## Productive contract

The block introduces an explicit, transient `domain_reference` admission around an
already-governed `CanonicalProductiveConceptEpisode`. It never rewrites or aliases
the episode's `scope_reference`.

Two concepts may become a cross-domain synthesis candidate only when:

- owner and session lineage match;
- explicit domain references are genuinely distinct;
- both HCC concepts contain sufficient governed structure;
- component relation/outcome structure corresponds;
- HCC link topology corresponds.

The candidate preserves both domain references, both original scopes, both concept
episode IDs and a deterministic source fingerprint.

## Reachability

`OfficialGovernedReasoningRuntimeGateway` stores only session-local transient
cross-domain concept provenance and exposes a same-turn synthesis candidate.
`CanonicalProductiveReasoningSource` contributes its exact references and
consultative context. `ReasoningRuntimeContributor` consumes that context through
the existing reasoning contribution boundary.

## Governance

A synthesis candidate:

- is read-only and session-local;
- does not persist;
- does not establish truth or causality;
- does not authorize inference;
- does not write Memory, Learning or World Model;
- does not execute Structural Transfer;
- does not register rules;
- does not execute actions or grant authority.

Cross-domain structural similarity therefore remains explicitly distinct from
truth, equivalence, causality and transfer.

## Focused validation

New contracts plus HCC productive gateway, productive hierarchical analogy,
ordinary multi-hypothesis, explanatory inquiry/re-entry and the global production
import-cycle audit: **31 PASS**.

`py_compile` passed for modified Python files and no modified Python file has lines
over 88 characters.

Official promotion remains gated by local `ruff check .` and full `pytest -q`.
With seven new tests, expected full baseline is **13,521 PASS + Ruff clean**.
