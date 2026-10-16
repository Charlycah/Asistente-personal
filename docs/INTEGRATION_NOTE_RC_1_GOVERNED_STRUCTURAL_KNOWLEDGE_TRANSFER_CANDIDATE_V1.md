# RC-1 — Governed Structural Knowledge Transfer Candidate v1

## Purpose

RC-1 introduces a read-only governed structural matching contract for recognizing
when previously grounded knowledge has the same bounded relational structure as
a newly grounded target, even when concrete domain entities do not share words.

The result is a transfer candidate only. It is not truth, inference authority,
a registered rule, a learned rule, a memory mutation, or an action.

## Authority

Structural compatibility is governed by
`GovernedStructuralKnowledgeTransferMatcher` inside `core.governed_reasoning`.
It reuses `GovernedContextualSemanticGroundingCandidate`,
`ContextualSemanticRole`, and `ContextualSemanticRelation`.

No generalization engine, analogy engine, second memory system, second inference
engine, or retrieval authority is introduced.

## Structural signature

The v1 signature compares:

- certified semantic family;
- canonical role ordering;
- role/relation topology;
- bounded literal values;
- explicit role-bound object references.

Concrete source texts and entity names are deliberately excluded from the
structural signature.

A successful result exposes explicit role correspondences between source and
target texts so the proposed transfer remains explainable.

## Bounded outcomes

- `NO_TRANSFER`: no structurally compatible known grounding exists.
- `TRANSFER_CANDIDATE`: exactly one compatible structure exists.
- `AMBIGUOUS`: more than one compatible structure exists; no source is selected.

A grounding cannot transfer to itself, and cross-scope sources are ineligible.

## Epistemic limits

RC-1 is session-local and read-only. It does not persist results, create or
modify Memory, create or modify Learning, mutate the world model, establish
truth, authorize inference, register rules, execute actions, call providers, or
perform retrieval.

Memory/retrieval may later provide bounded candidate groundings, but retrieval
must not decide structural validity.

## Explicit non-goals

RC-1 v1 does not automatically apply matched knowledge. It does not create
analogies through an LLM, rewrite rules, learn generalized rules, perform
cross-session transfer, or select among ambiguous matches.

## Validation

Tests require cross-domain matches with different entity vocabulary, rejection
when words overlap but relational structure differs, ambiguity handling,
scope isolation, deterministic role mapping, immutability, and preservation of
all non-authority limits.

Final repository certification still requires `ruff check .` and full
`pytest -q`.
