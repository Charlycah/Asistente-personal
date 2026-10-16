# M92 — Adaptive Cognition Integration

## Objective

Close Phase IX by integrating M85–M91 under one governed, auditable and
backward-compatible boundary.

## Architecture

```text
M84 Governed Reasoning Result
            |
            v
M92 Adaptive Cognition Manager
    |-- M85 episode capture
    |-- M86 model capability/reference
    |-- M87 meta-reasoning assessment
    |-- M88 advisory reflection
    |-- M89 explicit knowledge evolution
    |-- M90 explicit executive planning
    `-- M91 explicit executive coordination
```

## Public contracts

- `AdaptiveCognitionStage`
- `AdaptiveCognitionStageStatus`
- `AdaptiveCognitionStageRecord`
- `AdaptiveCognitionCycle`
- `AdaptiveCognitionCycleRepository`
- `InMemoryAdaptiveCognitionCycleRepository`
- `AdaptiveCognitionPolicy`
- `AdaptiveCognitionManager`

## Integration behavior

`CognitivePipeline` accepts an optional `adaptive_cognition` manager. When it is
present, the manager owns the safe post-M84 flow and returns an
`adaptive_cognition_cycle` in `CognitivePipelineResult`. When absent, the M85,
M87 and M88 integrations retain their previous behavior.

## Governance boundary

M92 does not automatically:

- update mental models;
- create or approve knowledge-evolution proposals;
- create executive plans;
- create executive coordinations;
- create tasks, schedule work or invoke tools;
- bypass Scope Guard, permissions or Governed Autonomy.

## Acceptance criteria

- All seven Phase IX faculties appear in readiness and cycle records.
- Safe automatic stages are traceable to their generated artifacts.
- Missing components are represented explicitly.
- Review requirements propagate.
- Duplicate cycles are rejected.
- Existing pipeline configurations remain compatible.
- Ruff passes and the complete test suite has no regressions.
