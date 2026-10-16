# Post-M409.1 — Curiosity Knowledge Candidate → Existing M369 Learning Evaluation Foundation v1

## Status

IMPLEMENTED / CERTIFICATION PENDING USER GATES.

## Purpose

Adapt an explicitly learning-relevant curiosity knowledge candidate into the
existing read-only M369 evaluation chain without creating a writer or a new
learning authority.

v1 intentionally supports explicit preference-learning evaluation. Ordinary
facts remain `NOT_LEARNING_RELEVANT`. Habit and pattern evaluation require
accumulated temporal/structured evidence and are not inferred from one human
answer.

## Existing M369 reuse

The bridge uses the existing `LearningFoundation` (M369.1),
`PreferenceLearning` (M369.2), and `SafeLearningPolicies` (M369.6).
It never changes their thresholds or dispositions.

A single preference observation remains `INSUFFICIENT_EVIDENCE`. Consistent
accumulated evidence may reach `REVIEW_REQUIRED`. Existing safe-learning policy
continues to reject contradictions or sensitive learning without consent and to
expire stale evidence.

## Governance

Learning kind and confidence are explicit inputs; v1 does not infer them from
free text. Prior preference evidence must already be structured M369 evidence.

No learning is accepted, persisted or applied. No memory or knowledge is
written. `ExperientialLearningManager` is not called. Habit detection, pattern
recognition and adaptive reasoning are not synthesized from a single curiosity
answer. No Gateway, provider, network, background process or action execution is
introduced.

M410, networking and Residential remain out of scope.
