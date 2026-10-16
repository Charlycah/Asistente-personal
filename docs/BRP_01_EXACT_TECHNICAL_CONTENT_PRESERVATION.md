# BRP.01 — Exact Technical Content Preservation

## Objective

Refine ROBY's visible companion expression without allowing personality
normalization to alter technical content that must remain exact.

## Behavioral change

- Argentine voseo continues to be applied to visible natural-language prose.
- Inline code delimited by backticks is preserved byte-for-byte.
- Fenced code blocks delimited by triple backticks are preserved byte-for-byte.
- Personality-adjustment telemetry now counts every actual replacement.
- Redundant no-op replacements were removed from the expression policy.

## Architectural boundary

This change adds no runtime, capability, service, decision layer, memory path,
or permission path. It is a deterministic refinement inside the existing
`CompanionExpressionPolicy`.

## Certification

- Focused suite: 7 passed.
- Full suite: 6229 passed.
- Regressions observed: 0.
- Ruff could not be reproduced in the packaging environment because the Ruff
  module is not installed there.
