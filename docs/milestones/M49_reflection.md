# M49 — ROBY Reflection (Phase IV.9)

## Purpose

M49 introduces ROBY's first metacognitive layer. ROBY can now review its own
reasoning, planning, knowledge usage and learning signals before closing a
cognitive turn.

## Architectural principle

ROBY does not only act, plan or learn. ROBY must also ask whether the process was
coherent, useful and aligned with its purpose as a persistent household presence
for Carlos and Cristina.

## Components

- `ReflectionContext`: explicit context to review a cognitive process.
- `ReflectionInsight`: one observation produced during reflection.
- `ReflectionResult`: auditable judgement, summary and recommendation.
- `ReflectionEngine`: deterministic first-pass reflection engine.
- `ReflectionManager`: stable facade with history and prompt integration.

## Integration

M49 integrates optionally with `CognitivePipeline` after learning and before the
final prompt is built. It can use:

- Identity
- Mental State
- Attention
- Working Memory
- Reasoning
- Planning
- Learning
- Knowledge Gateway

The integration is non-invasive. If `ReflectionManager` is not injected, the
pipeline behaves as before.

## Milestone

Today ROBY learned to review its own decisions.
