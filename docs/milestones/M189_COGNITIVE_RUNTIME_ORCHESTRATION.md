# M189 — Cognitive Runtime Orchestration

## Purpose

M189 starts ROBY Operational Cognitive Integration. It introduces one operational
boundary that coordinates existing cognitive capabilities during a real governed
conversation turn. It does not recreate reasoning, planning, reflection, memory,
or executive systems.

## Runtime order

The official preparation path is now:

1. governed provider and knowledge preparation;
2. inference request construction;
3. memory runtime enrichment;
4. cognitive runtime orchestration;
5. tool runtime enrichment;
6. governed provider execution.

## Contracts

`CognitiveRuntimeContributor` is the narrow port used by future integration
milestones. A contributor can apply context, skip the turn, or fail in a contained
way. It cannot execute providers, tools, network access, or platform mutations.

`CognitiveRuntimeOrchestrator` preserves contributor order, enriches only the LLM
request prompt and metadata, and exposes deterministic lineage through
`CognitiveRuntimeOrchestrationResult`.

## Privacy and governance

- contributor exception messages are not exposed;
- reference identifiers remain in lineage and are not copied into the prompt;
- no private conversation content is persisted by M189;
- no autonomous action authority is introduced;
- no provider call is performed by the orchestration layer.

## Next integrations

M190–M194 will implement concrete contributors for living conversation,
reasoning, planning, reflection, and executive cognition using this boundary.
