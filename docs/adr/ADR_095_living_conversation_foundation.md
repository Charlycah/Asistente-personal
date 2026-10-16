# ADR-095 — Living Conversation Foundation

## Status

Accepted for M93.

## Context

ROBY already has presence, relationship memory, controlled initiative, social
regulation and adaptive cognition. Those faculties can describe continuity and
suggest actions, but Phase X requires a distinct boundary that answers a more
fundamental question: whether speaking now would add enough value to justify
interrupting human attention.

Directly extending M53 Initiative would mix candidate generation with the
higher-level ethics of presence, context, privacy and silence. Automatically
emitting text would also be premature because composition, timing and delivery
need separate governed milestones.

## Decision

Introduce `core.living_conversation` and a `LivingConversationManager` that
accepts an explicit context and opportunity, applies a conservative policy, and
records one immutable decision.

The possible dispositions are:

1. `intervene` — the opportunity justifies a proportionate conversational act;
2. `defer` — it may have value later, but M93 does not schedule it;
3. `remain_silent` — restraint is the correct present action;
4. `review_required` — sensitivity or governance blocks automatic initiative.

M93 references prior subsystem artifacts by identifiers. It does not mutate or
reinterpret their records.

## Invariants

- Human autonomy and attention boundaries prevail.
- Do-not-disturb always produces silence.
- User absence produces deferral without scheduling.
- Guest privacy blocks personalized references.
- Sensitive unsolicited intervention is forbidden.
- Low confidence cannot produce unsolicited intervention.
- Silence and restraint are first-class decisions, not missing output.
- M93 never generates content, invokes an LLM or tool, writes memory or acts.

## Consequences

Phase X begins with a stable, testable and auditable constitutional boundary.
Later milestones may add opportunity generation, conversational composition,
timing and delivery, but each must consume M93 decisions rather than bypassing
them.
