# ADR-122 — Driving Conversation Adaptation

## Status
Accepted.

## Context
M117 establishes Driving Companion eligibility, M118 describes driving context, and M119 selects the permitted interaction envelope. A separate boundary is required to translate that envelope into conversational constraints without generating language or executing a modality.

## Decision
Introduce `core.driving_conversation_adaptation` as a pure, deterministic domain. It consumes an immutable M119 decision plus declarative content characteristics and emits an immutable adaptation plan.

The plan governs style, word and sentence budgets, user-floor preservation, question permission, confirmation need, chunking, and remainder deferral. It does not contain generated text and does not execute any action.

## Invariants
- Ownership matches the complete M117–M119 lineage.
- M119 remains authoritative for interaction permissions and mode.
- Non-ready upstream states propagate conservatively.
- No plan may enable a capability prohibited by M119.
- Questions are never introduced when absent from the declared content.
- Minimal and emergency modes remain bounded and non-discursive.
- Plans are immutable, deterministic, auditable, and repository-backed.

## Consequences
M120 provides a stable contract for future driving realization and safety coordination while preserving independent evolution of Maps, Visual Understanding, Ambient Context, and Unified Companion.
