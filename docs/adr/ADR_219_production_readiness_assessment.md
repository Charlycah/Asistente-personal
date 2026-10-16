# ADR 219 — Production Readiness Assessment

## Status

Accepted.

## Context

M218 certifies operational reliability from bounded M217 evidence, but certification alone is not the same as a production-readiness decision. ROBY needs a deterministic gate that consolidates the reliability certificate, its criteria, execution controls, failure controls, and complete lineage before the final M220 architecture acceptance.

## Decision

Introduce `ProductionReadinessAssessor` as the sole M219 authority. It consumes an M218 certificate for the same owner and session and emits an immutable assessment with five explicit criteria: reliability certification, reliability-criterion completion, operational lineage, bounded execution controls, and failure controls.

The official outcomes are `ready`, `conditional`, and `not_ready`. Strict policy requires full M218 certification. A configurable relaxed policy may preserve a conditional outcome for a narrowly incomplete but non-rejected certificate.

M219 publishes its result to the unified cognitive blackboard immediately after M218. It does not deploy, approve a release, mutate infrastructure, execute stress workloads, or certify the final ROBY v1 architecture.

## Consequences

Production-readiness decisions become reproducible, traceable, identity-bound, and isolated from deployment authority. M220 can consume a single governed assessment while retaining complete M211–M219 lineage.
