# ADR-145 — Presence Context Subscription

## Status
Accepted — 2026-07-11

## Context
M142 exposes immutable, canonical presence-context publications without invoking consumers or performing delivery. ROBY needs a governed way for downstream domains to declare interest in those artifacts while preserving provider neutrality and preventing subscription registration from becoming message transport or behavior execution.

## Decision
Introduce M143 as a declarative subscription boundary downstream from M142.

M143:
- accepts only governed M142 publication results;
- preserves the selected M142 publication exactly;
- validates ownership, freshness, confidence, result limits, deduplication, and ambient lineage;
- matches canonical topic and accepted schema versions;
- supports complete-only or partial-inclusive filters;
- represents active and paused subscription lifecycle states;
- stores immutable subscription records behind a repository protocol;
- never delivers context, invokes callbacks, processes consumer logic, performs inference, decides responses, adapts behavior, calls providers, automates actions, or mutates the platform.

## Consequences
Consumers can depend on a stable subscription contract without coupling to transport or execution mechanisms. Delivery, dispatch, callback invocation, consumer processing, and behavioral integration remain separate future responsibilities.
