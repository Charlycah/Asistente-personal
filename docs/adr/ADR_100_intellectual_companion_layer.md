# ADR-100 — Intellectual Companion Layer

## Status
Accepted for M98.

## Context
M93–M97 established governance, opportunity detection, timing, bounded reflection generation and longitudinal continuity. The next boundary must assemble those outputs into a coherent intellectual contribution without becoming a delivery channel or an unconstrained generator.

## Decision
Introduce `core.living_conversation.intellectual` as a deterministic assembly layer. It accepts only mutually consistent M93, M95 and M96 records, classifies the contribution, applies domain-specific framing, evaluates intellectual depth, preserves provenance and produces an immutable contribution record.

Supported domains are literature, music, science, history, philosophy, culture, personal projects and general reflection. Supported contribution kinds are response, question, connection, perspective/context and continuation.

M98 does not call an LLM, retrieve new knowledge, deliver messages, schedule work, mutate memory or bypass upstream decisions.

## Invariants
- A contribution cannot exist without matching governance, timing and reflection records.
- Only generated M96 reflections with an open M95 timing window can become ready contributions.
- Spontaneous contributions require traceable sources by default.
- Insufficient depth produces abstention, not filler.
- Review requirements remain review requirements.
- Non-ready contributions contain no user-facing content.
- Every result is immutable, identifiable and auditable.

## Consequences
The project gains a stable intellectual assembly boundary while preserving future freedom to add grounded knowledge retrieval, language realization and delivery as separate governed milestones.
