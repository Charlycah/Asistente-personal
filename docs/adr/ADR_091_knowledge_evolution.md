# ADR-091 — Knowledge Evolution

## Status

Accepted for M89.

## Context

M85–M88 provide governed experience, mental representations, meta-reasoning and
longitudinal reflection. ROBY still lacks a safe boundary for proposing changes
to durable knowledge without confusing reflection with truth or silently
mutating the Personal Knowledge Base.

## Decision

Introduce `core.adaptive_cognition.knowledge_evolution` as a proposal-and-decision
layer. A reflection may support a proposal to create, reinforce, supersede or
retire knowledge. Proposals and decisions are immutable, content-addressed and
fully traceable to reflections, mental models and existing knowledge items.

M89 does not auto-approve and does not apply approved proposals. Approval and
materialization remain separate governed operations. High-risk proposals are
blocked when approval is attempted and require a later explicit review path.

## Consequences

- Reflection is not promoted directly to fact.
- Existing PKB contracts remain unchanged.
- Knowledge mutations are reviewable and reversible by design.
- M90 can consume approved proposals without obtaining authority to apply them.
