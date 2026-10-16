# ROBY XI.2 — HCC GREEN-5 Productive Concept Episode & Consultative Gateway

**Entry baseline:** 13,462 PASS + Ruff clean.

## Implemented

- `CanonicalProductiveConceptEpisode` under `governed_reasoning`;
- exact owner/session/turn/scope lineage;
- deterministic episode identity from the already-governed HCC candidate;
- explicit gateway binding for a reviewable/contested HCC candidate;
- exact-turn concept retrieval and reference IDs;
- `CanonicalProductiveReasoningSource.concept_context_lines()`;
- `ReasoningRuntimeContributor` consultative concept-context consumption.

## Governance preserved

The productive concept episode is:

- read-only;
- session-local;
- non-persistent;
- no Memory write;
- no Learning creation;
- no Personal Knowledge mutation;
- no World Model mutation;
- no Structural Transfer;
- no rule registration;
- no action execution;
- no new authority.

## Important productive-reachability boundary

GREEN-5 deliberately does **not** fabricate hierarchical concepts from repeated
abstraction episodes.

The current ordinary productive semantic-grounding path is still bounded to the
existing certified relational family. Therefore this block binds and consumes an
**already-governed HCC candidate**, rather than pretending that ordinary conversation
currently supplies multiple semantically distinct abstraction families.

This distinction is intentional:

- HCC candidate → productive concept episode → consultative reasoning is now wired.
- Automatic ordinary-turn generation of sufficiently diverse HCC inputs is **not yet
  certified**.

That remaining upstream diversity/reachability question must be reconciled before any
claim that HCC is autonomously produced from arbitrary conversation.

## Focused validation

6 new GREEN-5 tests PASS.

Expanded architectural perimeter:

**84 PASS = 6 GREEN-5 + 10 HCC GREEN-1→4 + 68 pre-HCC controls.**

Full promotion requires local:

`ruff check .`
`pytest -q`

Expected complete suite if no regressions:

**13,468 PASS + Ruff clean.**
