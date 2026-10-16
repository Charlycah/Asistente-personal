# PM1 / M162 — Runtime Readiness Gate

## Goal

Provide the first controlled step of FASE X — PUESTA EN MARCHA by determining whether ROBY is ready to start without starting anything.

## Input

- One M161 `UnifiedCompanionIntegrationResult`.
- Immutable runtime component checks.
- Explicit required/optional classification.

## Output statuses

- `ready`
- `degraded`
- `blocked`
- `configuration_required`
- `provider_unavailable`
- `not_applicable`

## Component families

- configuration
- memory
- provider
- service
- permission
- storage
- network
- capability
- other

## Core rules

- Required configuration failures produce `configuration_required`.
- Required provider failures produce `provider_unavailable`.
- No available provider produces `provider_unavailable` when policy requires one.
- Required non-provider failures produce `blocked`.
- Optional failures and degraded components produce `degraded`.
- A non-ready M161 lineage blocks startup readiness.
- M162 never starts services or authorizes execution.

## Safety boundary

All operational flags remain false:

- activation
- service start
- provider call
- network access
- conversation start
- platform mutation

## Verification

Focused tests cover status transitions, provider visibility, configuration handling, M161 lineage, conservative confidence, immutability, deterministic identity, repository behavior, validation, and the no-execution boundary.
