# ADR 214 — High-Load Cognitive Scheduling

## Status
Accepted

## Context
M213 provides a deterministic recovery state, while M205 provides the governed cognitive work order. Under elevated demand ROBY needs an explicit operational policy for admission pressure without silently changing priorities, violating recovery restrictions, or introducing concurrent execution before M216.

## Decision
Introduce `HighLoadCognitiveScheduler` as the M214 authority for bounded cognitive admission control. It combines the M205 schedule with the effective M213 recovery plan, classifies demand into `nominal`, `elevated`, `high`, or `saturated`, and assigns each scheduled action an `admit`, `defer`, or `shed` disposition.

M214 publishes the effective load band to the Unified Cognitive Blackboard and preserves complete source lineage. Recovery states `stabilizing` and `held` restrict admission to one action. Saturated work beyond capacity is shed; less severe excess work is deferred.

## Boundaries
M214 does not execute work, spawn workers, introduce parallelism, mutate providers, invoke tools, or alter platform capacity. Concurrent cognitive execution remains reserved for M216.

## Consequences
ROBY gains deterministic behavior under load, explicit overload semantics, recovery-aware admission limits, and auditable scheduling decisions without expanding execution authority.
