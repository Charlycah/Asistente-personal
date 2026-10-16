# M85 — Episodic Memory

## Objective

Open Phase IX with a governed episodic substrate that lets ROBY preserve bounded experiences as ordered, traceable and recallable temporal records without converting them automatically into facts, knowledge or learned policy.

## M84 diagnosis

M84 provides the correct upstream governance boundary:

`Evidence → Claims → Context → Inference → Conflict → Decision → Explanation`

Its immutable identities and Decision Records are sufficient to anchor an episode. The pre-existing memory modules serve different responsibilities:

- `memory.py` and `memory_pipeline.py`: generic capture abstraction;
- `cognitive_memory_*`: persistence and relevance-based conversational recall;
- `working_memory.py`: temporary active workspace;
- `learning.py`: extracted and strengthened lessons;
- `reflection.py`: evaluation of cognitive results;
- `household_memory.py` and `relationship_memory.py`: domain-specific records.

Therefore M85 introduces a new Phase IX package rather than extending or renaming those modules.

## Delivered

- `core.adaptive_cognition` public package.
- immutable `Episode`, `EpisodeEvent` and `EpisodeReference` models;
- explicit status, event-kind and sensitivity enums;
- stable SHA-256 event and episode fingerprints;
- append-only contiguous episode revisions;
- repository protocol and deterministic in-memory repository;
- governed recall query and result contracts;
- filtering by owner, domain, status, sensitivity, tags, time and importance;
- deterministic relevance, importance, confidence and recency ranking;
- configurable episodic capture policy;
- direct capture of M84 governed reasoning results;
- optional Cognitive Pipeline integration and prompt guidance;
- ADR-087 and 19 focused tests.

## Invariants

- An episode records experience; it is not evidence of truth by itself.
- Events are immutable and temporally ordered inside their episode.
- Historical revisions are never mutated or overwritten.
- Revisions are contiguous and explicitly supersede their predecessor.
- Closed episodes cannot accept additional events.
- Completed episodes require an explicit outcome.
- Review-required M84 results remain review-required when captured.
- Sensitive episodes are excluded from ordinary recall.
- Owner and Scope Guard domains constrain retrieval.
- Recall cannot learn, update knowledge, execute tools or authorize actions.
- M84 identifiers remain traceable in captured reasoning episodes.
- Pipeline integration is optional and backward compatible.

## Architectural flow

`Governed experience → Episode events → Immutable episode revisions → Governed recall`

Future milestones may consume recalled episodes:

`M85 Episodes → M86 Mental Models → M87 Meta-Reasoning → M88 Reflection → M89 Knowledge Evolution`

No downstream interpretation is implemented in M85.
