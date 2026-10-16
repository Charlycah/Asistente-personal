# ADR-157 — Living Conversation Conversation Candidate

## Status
Accepted

## Context
M154 declares whether a prepared presence opportunity is eligible, partially eligible, or not eligible to advance. The architecture requires a separate canonical artifact that consolidates the eligible source for later timing and authorization stages without starting or scheduling a conversation.

## Decision
Add M155 as a pure conversation-candidate construction layer downstream from M154.

M155:

- consumes immutable M154 eligibility-decision results;
- selects the best valid decision deterministically;
- builds `CANDIDATE`, `CANDIDATE_PARTIAL`, or `WITHHELD` outcomes;
- preserves the exact M154 decision and M150 opportunity objects;
- applies owner, freshness, confidence, partial-context, deduplication, and result-limit governance;
- produces deterministic immutable candidate identifiers;
- never authorizes, starts, activates, or schedules a conversation.

## Boundaries
M155 does not select timing, generate prompts, realize responses, infer identity/activity/intent, adapt behavior, call providers, automate actions, or mutate the platform.

## Consequences
The Living Conversation presence pipeline gains a canonical candidate artifact while preserving the separation between eligibility, candidate construction, timing, final authorization, realization, and execution.
