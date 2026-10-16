# ADR-101 — Conversational Realization Layer

## Status
Accepted

## Context
M93–M98 can detect, govern, time, draft, continue and intellectually assemble a conversational contribution. The remaining gap is a stable boundary that turns an approved structured contribution into a final channel-neutral utterance without granting delivery authority.

## Decision
Introduce `core.living_conversation.realization` as M99. It consumes one M98 `IntellectualContribution`, validates owner continuity and upstream status, maps semantic contribution kinds to conversational acts, selects a bounded register, normalizes sentence boundaries, and produces immutable ordered segments plus a final text projection.

M99 supports concise, natural and deliberate registers, optional owner address, optional title inclusion, question integrity, character and segment limits, source preservation, abstention and review propagation.

M99 does not call an LLM, generate new knowledge, choose a device or channel, synthesize voice, deliver text, schedule work, invoke tools, mutate memory or learn from reactions.

## Invariants
- A realization cannot exist without one immutable M98 contribution.
- The realization owner must match the governed conversation owner.
- Only ready M98 contributions can produce user-facing segments.
- Review-required and abstained outcomes remain non-content outcomes.
- Sources are preserved exactly from M98.
- Question acts require a closing question by default.
- Segment and character limits fail closed through abstention.
- Every result is immutable, deterministic for identical inputs and auditable.

## Consequences
ROBY gains a final language-assembly boundary while preserving future freedom to add channel selection, text delivery, voice synthesis, mobile presentation and multimodal output as separate governed milestones.
