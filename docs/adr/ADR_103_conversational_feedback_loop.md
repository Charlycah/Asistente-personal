# ADR 103 — Conversational Feedback Loop

## Status
Accepted

## Context
M100 provides an auditable conversational presence, but ROBY still needs a governed way to interpret what happens after that presence: acceptance, correction, confusion, rejection, deepening, disengagement, or no observable signal.

## Decision
Introduce `core.living_conversation.feedback` as a post-presence assessment layer. It receives an immutable M100 presence plus explicit, implicit, or system feedback signals and returns an immutable assessment with a dominant signal, effective confidence, recommended adjustments, recommended intensity, follow-up posture, rationale, and deterministic identity.

The layer does not mutate its input and does not write to memory, learning, personality, realization, presence, or policy state. Its output is advisory and auditable.

## Invariants
- Ownership must match the governed presence owner.
- Only ready M100 presences are actionable.
- Implicit confidence is capped by policy.
- Low-confidence feedback is insufficient or review-required.
- `no_signal` cannot be combined with other signals.
- Non-actionable assessments expose only the `none` adjustment.
- Recommended intensity remains in `[0, 1]`.
- All records are immutable and deterministically identified.

## Consequences
M101 closes the first conversational loop without creating hidden adaptation. Future milestones may consume its assessments through explicit governance, but M101 itself never learns automatically.
