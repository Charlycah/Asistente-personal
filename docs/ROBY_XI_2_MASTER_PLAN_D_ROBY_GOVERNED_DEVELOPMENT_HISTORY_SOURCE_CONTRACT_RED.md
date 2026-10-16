# ROBY XI.2 — D:\Roby GOVERNED DEVELOPMENT HISTORY SOURCE — CONTRACT RED

## Status

CONTRACT RED / LOCALLY CONFIRMED.

Starting executable truth remains the Owner-certified post-D:\Documentos state:
13,359 PASS / 0 FAIL / Ruff clean.

The immediately preceding corpus/source-model reconciliation authorized RED only
for the narrow residual:

`BOUNDED_GOVERNED_DEVELOPMENT_HISTORY_DISCOVERY_SELECTION_AND_READ`.

No productive implementation is added by this block.

## Governing boundaries

CURRENT EXECUTABLE TRUTH + LATEST OWNER GATE > STALE HISTORICAL STATUS LABEL.

ONE BRAIN / ONE AUTHORITY PER CAPABILITY.

HISTORICAL_SOURCE != CURRENT_TRUTH.

HISTORICAL_SOURCE != DIAGNOSTIC_PROJECT_EVIDENCE.

HISTORICAL_READ != KNOWLEDGE / MEMORY / LEARNING WRITE.

HISTORICAL_READ != PROPOSAL_AUTHORIZATION != CODE_MUTATION.

## Existing-authority reconciliation

The certified Personal Documents source provides a reusable filesystem-security
pattern: configured root, deterministic bounded discovery, relative provenance,
explicit selection, revalidation, containment and symlink fail-closed behavior.

Its domain authority is not reused. In particular, D:\Roby historical material
must not flow through `DocumentInboxManager` merely because the existing
Personal Documents adapter already has an ingestion path.

`app.self_improvement_proposal_generation` remains unchanged and authoritative
for the bounded current-project proposal-evidence seam. Its
`DiagnosticProjectEvidence` continues to require explicit current project file
and validation-test evidence whose SHA-256 content is verified against the
current `project_root` before proposal generation.

The RED therefore defines an inert historical observation boundary only.

## Contractual module seam

The absent semantic is represented contractually as:

`app.development_history_source`.

Expected public contract:

- `DevelopmentHistorySourceAdapter`;
- `HistoricalSourceKind`;
- `build_development_history_source_from_environment`.

This naming identifies a subordinate source adapter, not a manager, brain,
repository, Knowledge authority, Memory authority or self-improvement owner.

The dedicated configuration key is:

`ROBY_DEVELOPMENT_HISTORY_ROOT`.

Absent or blank configuration must yield no source adapter. D:\Roby itself must
never be hardcoded in product code.

## RED contractual behaviors

### RED-1 — source boundary exists

The narrow source adapter, source-kind classification and environment builder
must exist.

### RED-2 — explicit governed root

The builder must require `ROBY_DEVELOPMENT_HISTORY_ROOT`. It must not silently
fall back to the Owner's real D:\Roby path.

### RED-3 — bounded deterministic historical discovery

Discovery must use stable relative-path ordering, a positive candidate limit,
explicit truncation and historical source references.

### RED-4 — exact direct-readable allowlist

Direct historical reading is limited to:

`.py`, `.pyi`, `.md`, `.txt`, `.json`, `.toml`, `.yaml`, `.yml`, `.ini`, `.cfg`,
`.csv`, `.html`, `.htm`.

Binary/database/document formats outside this contract are not direct-readable
candidates.

### RED-5 — sensitive/noise exclusions

The source must exclude runtime/private/cache/environment/generated surfaces,
including `.roby`, `.git`, `.pytest_cache`, `.ruff_cache`, `__pycache__`, virtual
environments, `site-packages`, `.env`, credential, secret and token material.

An allowlisted suffix never overrides an excluded path/name class.

### RED-6 — historical provenance

A candidate must preserve deterministic identity, relative path, top historical
snapshot/container segment when present, suffix, size, modification timestamp
and a `development-history:` source reference.

It must not use `local-library:` or `personal-document:` identity.

### RED-7 — explicit revalidated bounded read

Only a candidate returned by the last bounded discovery may be selected. The
selected file must be revalidated before reading. A changed candidate fails
closed.

A successful direct read returns an inert historical observation whose trust
class is explicitly historical and whose `current_truth` value is false.

### RED-8 — containment, symlink and read limits

Root escape, external symlink traversal and configured byte/character limit
violations fail closed.

### RED-9 — ZIP is opaque

A `.zip` may be catalogued only as an `opaque_archive` candidate. It cannot be
read, extracted, traversed or searched internally by this increment.

### RED-10 — no durable state

Discovery and historical reading must not modify the authorized source tree or
create project, Knowledge, Memory, Learning or document-lifecycle state.

### RED-11 — historical types are not current-project evidence

Historical candidates must remain type/semantic-distinct from
`DiagnosticProjectFileEvidence` and `DiagnosticProjectEvidence`. Historical
candidate identity is not a current-project SHA-256 evidence claim.

## Guardrails

### Guardrail 12 — current project evidence remains hash-bound

Existing `DiagnosticProjectEvidence` and `DiagnosticProjectFileEvidence`
continue to construct explicit current-project evidence with SHA-256 content
identity and validation-test scope.

### Guardrail 13 — no hardcoded Owner root

Existing `app/` and `core/` product code contains no hardcoded D:\Roby root.

### Guardrail 14 — no automatic cognitive integration

Existing runtime environment/root wiring, governed Reasoning and self-improvement
proposal generation do not reference the new history configuration or adapter.

The RED does not authorize changing that fact.

## Local RED result

Directed command:

`pytest -q tests/architecture/`
`test_master_plan_d_roby_governed_development_history_source_contract_red.py`

Result:

- 11 expected RED failures;
- 3 guardrails passed;
- 0 unexpected failures.

Every intended RED failure is:

`ModuleNotFoundError: No module named 'app.development_history_source'`.

This is the desired contractual RED: the bounded semantic is absent rather than
present with incorrect behavior.

The RED test compiles successfully with `py_compile` and contains zero lines over
88 characters.

## Product and authority delta

Product code changed: NONE.

Existing product files changed: NONE.

New authority: NONE.

New persistence: NONE.

New runtime wiring: NONE.

New cognitive integration: NONE.

The only additions are this CONTRACT RED document and its architecture test.

## Explicit STOP boundaries

This RED does not authorize:

- runtime/conversation wiring;
- semantic historical search;
- automatic comparison with current code;
- ZIP extraction;
- background indexing or watchers;
- automatic ingestion;
- Document Inbox ingestion;
- Reasoning admission;
- Knowledge or Memory persistence;
- Learning admission;
- proposal generation from historical material;
- self-modification;
- Planning, Authorization or Execution;
- B2, B3 or B4.

## Certification state

`CONTRACT_RED: LOCALLY_CONFIRMED`.

`EXPECTED_RED_FAILURES: 11 / 11`.

`GUARDRAILS: 3 / 3 PASS`.

`UNEXPECTED_FAILURES: 0`.

`PRODUCT_CHANGE: NONE`.

`NEW_AUTHORITY: NONE`.

`B2 / B3 / B4: STOP`.

Owner global validation is required before this RED becomes Owner-certified.

## Owner validation gate

Run from the delivered project root:

`python scripts/clean_project_caches.py`

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`

Expected global state is the prior green suite plus exactly the 11 contractual
RED failures from the absent `app.development_history_source` module, with Ruff
clean and no unrelated failures.

STOP before SURGICAL GREEN until Owner supplies that validation.
