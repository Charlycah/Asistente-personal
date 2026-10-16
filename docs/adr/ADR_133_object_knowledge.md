# ADR-133 — Object Knowledge

## Status
Accepted.

## Context
M130 consolidates scene-level meaning but deliberately does not represent the entities declared within that scene. ROBY needs a provider-neutral, governed object-knowledge boundary before future perception, product, text, place, attention, or unified-companion capabilities can consume object semantics.

## Decision
Introduce `core.object_knowledge` downstream from M130. It accepts immutable declarative `ObjectEvidence`, validates owner and observation lineage, filters weak or disallowed evidence, resolves duplicates deterministically, detects close semantic conflicts, and produces an immutable `ObjectKnowledgeProfile`.

Object knowledge is semantic consolidation only. M131 does not inspect pixels, detect or track objects, extract text, identify products or places, perform biometrics, call providers, or mutate platform state.

## Consequences
- Object semantics remain independent from perception providers.
- Evidence provenance and ambiguity remain explicit.
- Future visual attention, product search, place understanding, and unified context can consume one stable contract.
- Detection and execution capabilities remain separate milestones.
