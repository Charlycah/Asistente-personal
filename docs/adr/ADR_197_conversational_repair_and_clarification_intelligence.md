# ADR 197 — Conversational Repair and Clarification Intelligence

## Decision

ROBY will add a deterministic, advisory dialogue-repair capability immediately
after Adaptive Conversation Intelligence. It will identify conversational
conditions that make direct execution unsafe or incoherent and recommend one of
four bounded actions: proceed, ask a targeted clarification, confirm a
correction, or acknowledge a topic shift.

## Rationale

M196 models how intent evolves, but adaptation alone does not determine when a
turn lacks a stable referent or sufficient task detail. M197 converts selected
conversation-state transitions and local linguistic signals into explicit
repair guidance, reducing unsupported assumptions while preserving conversational
flow.

## Consequences

- M197 may consume the current M196 state but does not own or mutate it;
- repair assessments are session-scoped, deterministic, and non-authoritative;
- clarification guidance is minimal and targeted rather than open-ended;
- no tool, provider, memory, plan, or autonomous-action authority is added;
- assessment references are hashes of bounded classifications and metadata, not
  raw user content;
- official contributor order is M196, then M197, then existing cognitive stages;
- M197 remains optional and failure-contained.
