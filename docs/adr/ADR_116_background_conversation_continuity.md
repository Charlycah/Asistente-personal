# ADR 116 — Background Conversation Continuity

## Status
Accepted

## Context
M111 governs the logical mobile conversation runtime, M112 governs mobile presence, and M113 decides notification interruption. ROBY still needs a governed way to preserve a resumable logical checkpoint when the mobile experience moves to background or dormancy.

## Decision
Introduce M114 as a pure decision layer that evaluates M111–M113, produces immutable background-continuity decisions, and carries only an opaque checkpoint reference. It does not execute operating-system background work, deliver notifications, persist raw conversation content, or resume a conversation by itself.

## Invariants
- Upstream ownership must agree.
- Stale signals require review.
- Terminated conversations expire continuity.
- Suspended conversations are not resumable.
- Only maintaining, checkpointed, or awaiting-user states may be resumable.
- Decision identifiers are deterministic and auditable.
