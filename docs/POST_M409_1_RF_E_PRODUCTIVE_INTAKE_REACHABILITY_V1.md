# RF-E — Productive Intake Reachability — Implementation v1

## Status

Implementation candidate. Final closure requires `ruff check .` and full `pytest -q`.

## Purpose

Expose the already certified RF-E/3A.8 productive temporary-rule intake to every
substantive official end-to-end conversational turn without changing the primary
conversation-entry route.

The reachability path is:

1. `OfficialEndToEndConversationRuntimeGateway` classifies the turn normally;
2. the raw `GovernedConversationPipelineRequest.text` is observed once by the canonical
   governed-reasoning productive intake;
3. the original context/dialogue/reasoning/action route remains unchanged;
4. if the route also enters adaptive cognition/reasoning, the later reasoning call skips
   a second intake observation for that same turn.

## Authority and routing

The entry classifier remains the authority for conversational routing. It is not taught
RF-E grammar or semantic patterns.

`governed_reasoning` remains the only authority for temporary-rule interpretation,
grounding, compilation, case grounding, claim projection, instantiation, admission, and
inference. The end-to-end runtime only exposes the raw turn to that existing capability.

## Exactly-once and raw-turn invariants

The official end-to-end path observes productive intake at most once per turn. The intake
receives `request.text`, not the continuity-enriched prompt, so journal/context material
cannot be mistaken for current-turn rule evidence.

Partial or legacy test compositions that do not expose the productive-intake observer
remain supported and report `productive_intake_observed=False`.

## Observability

`EndToEndConversationRuntimeResult` and its snapshot expose only:

- `productive_intake_observed`;
- `productive_intake_status`.

They do not expose pending specs, projected claims, bindings, or registry internals.

## Governance

This increment adds no persistence, Memory/Learning mutation, provider/retrieval use,
entity repository, second registry, action execution, or authority gain. GAP A grammar
compatibility remains deferred and unchanged.
