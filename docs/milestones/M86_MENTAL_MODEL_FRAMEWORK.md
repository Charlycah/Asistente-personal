# M86 — Mental Model Framework

## Objective

Give ROBY a governed framework for stable, revisable internal representations of people, projects, tasks, systems, environments, concepts and self, without treating those representations as facts or learned policy.

## Baseline diagnosis

M85 preserves bounded experience. Existing `mental_state.py` describes transient operational state; `working_memory.py` holds temporary context; domain memories store specialized records; `knowledge_gateway.py` retrieves knowledge. None provides a generic, revisioned representation of a subject.

## Delivered

- immutable `MentalModel` and `ModelAssertion` contracts;
- model and assertion lifecycle enums;
- stable SHA-256 identities and fingerprints;
- contiguous immutable model revisions and history;
- repository protocol and deterministic in-memory implementation;
- explicit `ModelUpdateProposal` boundary;
- proposal creation from M85 episodes with direct provenance;
- confidence-based review policy;
- conflict preservation as disputed assertions;
- owner, kind, domain, status and text query;
- optional Cognitive Pipeline prompt integration;
- ADR-088 and 20 focused tests.

## Invariants

- A mental model is a revisable representation, not evidence of truth.
- Episodes propose changes; they never mutate models directly.
- Low-confidence changes require explicit approval.
- Contradictory assertions are preserved, not silently replaced.
- Revisions are immutable, contiguous and auditable.
- Owner and Scope Guard domains constrain retrieval.
- M86 does not promote assertions to knowledge, learn policy or execute actions.
- Pipeline integration is optional and backward compatible.

## Flow

`M85 Episode → Model update proposal → Policy/review → Immutable model revision`

Future consumption:

`M86 Mental Models → M87 Meta-Reasoning → M88 Reflection → M89 Knowledge Evolution`
