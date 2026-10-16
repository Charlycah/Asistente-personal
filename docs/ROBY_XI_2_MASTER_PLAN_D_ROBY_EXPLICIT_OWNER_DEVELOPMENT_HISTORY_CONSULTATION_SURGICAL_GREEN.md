# ROBY XI.2 — D:\Roby Owner history consultation — Surgical GREEN

## Status

SURGICAL GREEN implemented locally after Owner-certified CONTRACT RED.

The productive residual closed by this increment is:

`EXPLICIT_OWNER_DEVELOPMENT_HISTORY_CONSULTATION_ADMISSION_AND_PRESENTATION`

The already Owner-certified `DevelopmentHistorySourceAdapter` remains unchanged.

## Baseline and corrected contract

The baseline is the complete CONTRACT RED package.

The Owner-supplied corrected contract test replaces the earlier copy of:

`tests/architecture/`
`test_master_plan_d_roby_explicit_owner_history_consultation_contract_red.py`

That correction is documentary/test hygiene only: it preserves the eleven RED
behaviours and three guardrails while keeping imports Ruff-compatible.

## Product delta

Exactly one productive module is added:

`app/development_history_consultation_runtime.py`

No existing productive file is modified.

The module provides only:

- `DevelopmentHistoryConsultationInterceptionPort`;
- `development_history_consult_descriptor()`;
- `build_development_history_consultation_runtime_from_environment()`.

No second source, registry, gateway, manager, planner, Reasoning authority,
Memory authority, Knowledge authority, Learning authority, or proposal authority
is introduced.

## Canonical composition

The implemented route is:

Owner explicit intent
→ `OfficialRuntimeCapabilityRegistry`
→ subordinate consultation interception port
→ existing `DevelopmentHistorySourceAdapter`
→ safe presentation
→ STOP.

The capability name is exactly:

`development_history.consult`

The descriptor is read-only, human-scoped, and human-approved.

## Admission

The port admits only explicit development-history intent, including the governed
`D:\Roby` reference. Generic requests about history, ROBY, development, or files
are not sufficient.

Discovery uses only the existing source candidate metadata. It does not search
inside candidate contents.

## Selection and ephemeral state

When selection is required, pending state is scoped by `session_id` and expires
after five minutes.

Selection accepts only:

- a displayed ordinal; or
- the exact displayed relative path.

An internal candidate identifier supplied by the user is not a valid selection.

Cancellation removes the pending selection.

## Presentation privacy

Disambiguation presents only safe relative metadata:

- ordinal;
- relative path;
- direct-text or opaque kind;
- byte size.

It does not present the configured absolute root, `source_reference`, or internal
candidate identity.

## Archive boundary

ZIP candidates remain opaque metadata.

They can be displayed as historical artifacts but cannot be read or extracted
through this consultation route.

## Trust boundary

The GREEN preserves:

`HISTORICAL_PRESENTATION != CURRENT_TRUTH`

`HISTORICAL_PRESENTATION != DIAGNOSTIC_PROJECT_EVIDENCE`

`HISTORICAL_PRESENTATION != REASONING_ADMISSION`

`HISTORICAL_PRESENTATION != MEMORY_WRITE`

`HISTORICAL_PRESENTATION != KNOWLEDGE_WRITE`

`HISTORICAL_PRESENTATION != LEARNING_ADMISSION`

`HISTORICAL_PRESENTATION != PROPOSAL_AUTHORIZATION`

`HISTORICAL_PRESENTATION != CODE_MUTATION`

Level-2 read-only evidence execution is not introduced into this direct
Owner-driven route.

## Builder semantics

The builder delegates source construction to the existing governed source
builder.

If `ROBY_DEVELOPMENT_HISTORY_ROOT` is absent, no consultation capability is
registered.

Invalid source configuration fails closed and does not register the capability.

No fallback path to `D:\Roby` is hardcoded.

## Local certification

The corrected consultation contract passes:

`14 passed`

The consultation contract together with the governed development-history source
contract passes:

`28 passed`

`py_compile` passes for the new module and corrected contract test.

Line-length check:

- consultation module: 227 lines, 0 lines longer than 88;
- corrected contract test: 260 lines, 0 lines longer than 88;
- this GREEN document: 0 lines longer than 88.

Ruff is not installed in the local execution environment used to build this
package. Ruff therefore remains an Owner certification requirement and is not
claimed locally.

## STOP

This GREEN does not authorize:

- automatic Reasoning admission;
- Memory, Knowledge, or Learning persistence;
- historical-to-current-evidence promotion;
- direct proposal generation from historical material;
- code mutation or self-modification;
- ZIP extraction;
- semantic content indexing of the historical corpus;
- autonomous historical consultation;
- B2, B3, or B4 expansion.

## Result

`SURGICAL_GREEN: LOCALLY_CONFIRMED`

`CORRECTED_CONTRACT_TEST: INTEGRATED`

`CONTRACT_TESTS: 14 PASS`

`FOCUSED_SOURCE_AND_CONSULTATION_TESTS: 28 PASS`

`PRODUCTIVE_FILES_ADDED: 1`

`EXISTING_PRODUCTIVE_FILES_CHANGED: 0`

`NEW_COGNITIVE_AUTHORITY: NONE`

`OWNER_GREEN: PENDING`

The next gate is Owner global certification with cache cleanup, quality baseline,
Ruff, and full pytest. STOP before any further reachability or cognitive horizon.
