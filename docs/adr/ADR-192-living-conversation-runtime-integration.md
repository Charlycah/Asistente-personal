# ADR-192 — Living Conversation Runtime Integration

## Decision

Represent governed living-conversation output as an M189 cognitive contributor.
The contributor projects an existing M105 integration into the current
user-initiated prompt and never delivers a message itself.

## Rationale

The M93–M105 chain already owns conversational opportunity, timing, presence,
rhythm, curiosity, realization, and integration decisions. Reimplementing any
of those decisions in the operational runtime would duplicate cognition and
break lineage. A contributor preserves those decisions while keeping provider,
tool, memory, and delivery authority outside the living-conversation layer.

## Consequences

- Eligible decisions can shape cadence and next move in a real turn.
- Inactive or review-required decisions remain visible but non-invasive.
- Exact M93–M105 references remain available to orchestration and tracing.
- Proactive activation remains outside M190.
