# M193 — Reflection Runtime Integration

## Purpose

M193 connects the adaptive reflection capability created in M88 to the governed
operational conversation runtime. It does not create a new reflection engine.
It projects an existing `ReflectionRecord` into the current turn through the
M189 cognitive runtime orchestration boundary.

## Official order

1. Living conversation context.
2. Governed reasoning.
3. Executive planning.
4. Adaptive reflection.
5. Additional cognitive contributors.
6. Tool runtime and local provider execution.

## Publication policy

- `stable` and `improving` records may contribute summary, observations, and
  consultative recommendations.
- `insufficient` contributes only a caution against inferring stable patterns.
- `mixed`, `degrading`, or any record with a high-importance observation is
  withheld from the provider prompt because it requires review.
- Missing reflection is represented as a skipped cognitive stage.

## Governance boundary

Reflection may review how the response should be framed. It may not rewrite
reasoning decisions, activate or execute plans, call tools, mutate memory,
change knowledge, or grant execution authority to the model.

All record, assessment, observation, episode, and mental-model identifiers are
retained as cognitive lineage and are not exposed in provider prompts.
