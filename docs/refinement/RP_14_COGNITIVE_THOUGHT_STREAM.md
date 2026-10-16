# RP.14 — Cognitive Thought Stream

RP.14 converts agenda deliberation and governed reflection into a compact,
immutable stream of executive thought summaries.

## Authority

The authoritative implementation is `app/cognitive_thought_stream.py` and its
state is owned by `ContinuousInternalCognitiveLoop`.

## Guarantees

- no private chain-of-thought is stored;
- summaries are bounded and provenance-aware;
- the stream cannot execute tools or change permissions;
- previous RP contracts remain compatible.

## Integration

The output is published as `ContinuousCognitiveState.thought_stream` between
reflection and the hypothesis workspace.
