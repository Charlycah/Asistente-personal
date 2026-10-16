# Post-M409.1 — Governed Independence Level 1/2 Authorization Boundary Foundation v1

Status: IMPLEMENTED — pending official Ruff + complete pytest certification.

## Purpose
Represent the governance boundary between a non-executive evidence-acquisition plan and permission to continue toward an existing initiative/execution gate. The boundary does not execute.

## Decisions
- `MAY_INITIATE`: eligible to continue to the next existing governed gate; not execution authorization.
- `MUST_ASK`: explicit human approval is required.
- `MUST_ABSTAIN`: initiative must stop.
- `REVIEW_REQUIRED`: metadata/ambiguity/partial coverage prevents an automatic decision.

## Reused authorities
- `planning_foundation` remains the planning authority and keeps `planning_execution_authorized=False`.
- M62 `CapabilityRegistryManager` / `CapabilityDescriptor` remain the capability description authority.
- `PersonalInitiativeEngine` remains the existing Level 1 conversational initiative gate and keeps execution disabled.
- No `AutonomyAuthority`, selector, executor, gateway, worker, or scheduler is introduced.

## Minimal descriptor extension
`CapabilityDescriptor` gains fail-closed declarations with `UNDECLARED` defaults:
- `initiation_policy`: undeclared / never / human approval / governed autonomous eligibility.
- `effect_class`: undeclared / read-only / state-changing.
- `interaction_scope`: undeclared / internal / human / device / external.

`evidence_outputs` remains independent: providing evidence does not grant initiation permission.

## Level 1
Human interaction is routed only as eligibility and reuses an existing `InitiativeProposal`. The boundary does not generate a Curiosity question and does not emit conversation.

## Level 2
Only an explicitly declared, read-only, non-network, low-risk, enabled candidate can become `MAY_INITIATE`; ambiguity, partial planning, undeclared policy, state changes, network/external scope, or high risk fail closed. Even `MAY_INITIATE` has `execution_authorized=False`.

## Validation
15 architecture/semantic tests are included. Focused overlay validation passed 54/54 tests across M62, runtime registry, M368.1 Planning Foundation, Evidence Acquisition Planning/Productive Consumption, and this boundary. Official certification remains `ruff check .` and complete `pytest -q` on the certified baseline.
