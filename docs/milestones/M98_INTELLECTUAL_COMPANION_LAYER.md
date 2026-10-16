# M98 — Intellectual Companion Layer

## Objective
Assemble validated M93–M96 outputs into a bounded, sourced and domain-aware intellectual contribution suitable for a future delivery layer.

## Scope
- Intellectual domains: literature, music, science, history, philosophy, culture, personal projects and general.
- Contribution kinds: response, question, connection, context/perspective and continuation.
- Immutable requests, contributions, policy and repository contracts.
- Depth scoring based on opportunity quality, concepts, thesis and sources.
- Domain-specific titles and bounded concept enrichment.
- Abstention for weak, ungrounded, oversized or non-generated material.
- Explicit review path for protected contributions.

## Exclusions
M98 does not:
- call an LLM;
- search or retrieve new evidence;
- speak or send messages;
- schedule interventions;
- execute tools;
- update memory, relationship or continuity state;
- override M93 governance, M95 timing or M96 generation outcomes.

## Contracts
### `IntellectualCompanionRequest`
Requires consistent governance, timing and reflection records and optionally adds a domain, thesis and bounded concepts.

### `IntellectualContribution`
Records status, kind, domain framing, thesis, key points, question, sources, rationale, depth score and deterministic identity.

### `IntellectualCompanionLayer`
Composes a contribution or explicitly abstains/requires review.

## Acceptance criteria
- Upstream record consistency is enforced.
- Ready contributions preserve all source references.
- Spontaneous unsourced contributions are rejected by default.
- Low-depth material is not padded into conversation.
- Review and abstention records contain no deliverable content.
- Domain and form mappings are deterministic.
- Existing M1–M97 behavior remains unchanged.
- Ruff passes and the complete test suite passes.
