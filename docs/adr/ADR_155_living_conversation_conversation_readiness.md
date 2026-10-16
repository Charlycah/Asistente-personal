# ADR-155 — Living Conversation Conversation Readiness

## Status
Accepted

## Context
M152 produces one governed opportunity selection but intentionally does not express whether that selection is sufficiently prepared for later conversation-decision stages.

## Decision
Introduce M153 as a pure readiness layer downstream from M152. It maps full selections to ready, permitted partial selections to partially ready, and deferred selections to not ready. It preserves exact source lineage and exposes no behavioral authorization.

## Consequences
Readiness becomes explicit and independently governed. Later decision and timing milestones can consume M153 without coupling to selection internals. M153 cannot initiate conversation, choose timing, generate content, call providers, automate, or mutate the platform.
