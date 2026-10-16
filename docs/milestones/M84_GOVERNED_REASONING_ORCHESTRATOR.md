# M84 — Governed Reasoning Orchestrator

## Objective

Close Phase VIII by integrating M77–M83 into one deterministic, governed and auditable reasoning flow while preserving backward compatibility and the separation between reasoning and action.

## Delivered

- `GovernedReasoningStatus`: completed, abstained, blocked and review required.
- immutable `GovernedReasoningPolicy`.
- immutable `GovernedReasoningResult` with stable SHA-256 identity.
- `GovernedReasoningOrchestrator`.
- `GovernedReasoningManager` for Cognitive Pipeline integration.
- mandatory M79 → M80 → M81 → M82 → M83 execution order.
- deterministic public conclusion synthesis from applied rule-result claims.
- governed abstention and block messages.
- limited result snapshots for pipeline consumers.
- optional `CognitivePipeline` dependency and result field.
- system-prompt guidance preserving evidence/claim/inference separation.
- formal closure of Phase VIII.

## Invariants

- Context assembly always precedes inference.
- Inference always precedes conflict and uncertainty analysis.
- Every run creates a Decision Record and Explainable Answer.
- A blocked or insufficient query is recorded rather than treated as a technical failure.
- Rule results remain inferential claims and are never promoted automatically.
- No tool, external action or permission is executed by M84.
- The most restrictive governance result prevails.
- Pipeline integration is optional and backward compatible.
- Public snapshots omit unrestricted reasoning content.

## Phase VIII closure

M77–M84 now provide the complete governed reasoning chain:

`Sources → Evidence → Claims → Context → Inference → Conflict & Uncertainty → Decision Record → Explainable Answer → Orchestration`

Phase VIII is complete. Future phases may consume M84 results, but action execution must continue through the existing planning, permission, Tool Gateway and Governed Autonomy boundaries.
