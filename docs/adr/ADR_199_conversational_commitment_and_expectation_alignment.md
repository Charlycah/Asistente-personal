# ADR 199 — Conversational Commitment and Expectation Alignment

## Decision

ROBY will add a deterministic, advisory commitment-and-expectation capability immediately after M198 conversational grounding.

M199 converts shared-understanding state into bounded guidance about what may be responsibly committed in the current turn. It distinguishes aligned expectations, explicit commitment requests, absolute guarantees, and commitments blocked by unresolved grounding.

## Constraints

- M199 consumes M198 grounding state but does not own or mutate it.
- Clarification boundaries take priority over commitment requests.
- Absolute guarantees are calibrated rather than repeated as certainty.
- Commitments are limited to work realizable and verifiable in the active turn.
- M199 cannot schedule future work, execute tools, select providers, mutate memory, or alter plans.
- Official contributor order is M196, M197, M198, M199, then existing cognitive stages.
- M199 remains optional, deterministic, traceable, and failure-contained.

## Consequences

The runtime gains explicit expectation alignment without granting conversational guidance operational authority. Downstream stages receive concise instructions that prevent unsupported promises while preserving normal progress.
