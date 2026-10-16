# ROBY XI.2 — D:\Roby GOVERNED DEVELOPMENT HISTORY SOURCE — SURGICAL GREEN

## Status

SURGICAL GREEN / LOCAL CONTRACT CLOSURE / OWNER CERTIFICATION PENDING.

Starting gate: CONTRACT RED OWNER-CERTIFIED with 11 expected failures,
13,362 other tests passing, and Ruff clean.

## Closed residual

`BOUNDED_GOVERNED_DEVELOPMENT_HISTORY_DISCOVERY_SELECTION_AND_READ`

The GREEN adds one narrow application/infrastructure source adapter. It does not
create a cognitive authority, repository, manager, planner, agent, brain, or
persistence owner.

## Product delta

Added only:

`app/development_history_source.py`

No existing productive file was modified.

## Governed source model

The adapter implements only:

configured historical root
→ bounded deterministic read-only discovery
→ explicit historical candidate selection
→ selected-source revalidation
→ bounded UTF-8 historical read
→ inert historical observation
→ STOP

The root is supplied only through `ROBY_DEVELOPMENT_HISTORY_ROOT`. `D:\Roby` is
not hardcoded in product code.

## Candidate semantics

Historical candidates are immutable transient metadata. They preserve:

- deterministic candidate identity;
- root-relative POSIX path;
- `development-history:` source provenance;
- top-level snapshot segment;
- suffix;
- size;
- modification timestamp;
- source kind.

They are not `DiagnosticProjectEvidence` or `DiagnosticProjectFileEvidence` and
do not expose `content_sha256` as current-project evidence identity.

## Direct-readable allowlist

Exactly these suffixes are directly readable:

`.py`, `.pyi`, `.md`, `.txt`, `.json`, `.toml`, `.yaml`, `.yml`, `.ini`,
`.cfg`, `.csv`, `.html`, `.htm`.

`.zip` is discoverable only as `opaque_archive` metadata and cannot be read or
extracted by this capability.

## Exclusion boundary

Discovery fails closed for symlinks, root escape, unsupported formats, and
sensitive/noise surfaces including `.roby`, `.git`, `.pytest_cache`,
`.ruff_cache`, `__pycache__`, `.venv`, `venv`, `site-packages`, environment
files, and credential/secret/token/password-named files.

No archive traversal or extraction is implemented.

## Read boundary

A selected candidate must come from the latest bounded discovery and is
revalidated before reading. Candidate metadata must remain unchanged.

Direct reads are bounded independently by positive byte and character limits.
The implementation reads only valid UTF-8 text and fails closed when limits are
exceeded.

Discovery and reading create no durable project state.

## Frozen trust boundary

`HISTORICAL_SOURCE != CURRENT_TRUTH`

`HISTORICAL_SOURCE != DIAGNOSTIC_PROJECT_EVIDENCE`

`HISTORICAL_PATH_MATCH != CURRENT_PROJECT_FILE_IDENTITY`

`HISTORICAL_READ != DOCUMENT_INBOX_INGESTION`

`HISTORICAL_READ != REASONING_ADMISSION`

`HISTORICAL_READ != KNOWLEDGE_OR_MEMORY_WRITE`

`HISTORICAL_READ != LEARNING`

`HISTORICAL_READ != PROPOSAL_AUTHORIZATION`

`HISTORICAL_READ != CODE_MUTATION`

Existing self-diagnostic and self-improvement evidence authorities remain
unchanged. Current project evidence must still be reacquired and hash-bound
through the existing `DiagnosticProjectEvidence` contract.

## Runtime boundary

No automatic runtime construction or registration was added. No changes were
made to runtime environment wiring, runtime root construction, governed
Reasoning, or self-improvement proposal generation.

Productive conversational or cognitive reachability is not claimed by this
GREEN and would require a separately demonstrated residual.

## Local verification

Contract file:

`tests/architecture/`

`test_master_plan_d_roby_governed_development_history_source_contract_red.py`

Result:

`14 passed`

This closes all 11 Owner-certified RED failures while preserving all 3
contract guardrails.

Focused regression around current project evidence, Personal Documents source
governance, governed read-only evidence, and self-improvement proposal
generation:

`38 passed`

`python -m py_compile app/development_history_source.py`: PASS.

Line discipline:

- new product module: 217 lines, 0 lines > 88;
- RED contract test: 300 lines, 0 lines > 88;
- this GREEN document: 0 lines > 88 after final verification.

Ruff is not available in the assistant execution environment, so no local Ruff
claim is made. The Owner gate remains authoritative.

## Scope closure

`LOCAL_GREEN: CONFIRMED`

`OWNER_GREEN: PENDING`

`NEW_COGNITIVE_AUTHORITY: NONE`

`NEW_PERSISTENCE: NONE`

`AUTOMATIC_RUNTIME_WIRING: NONE`

`ARCHIVE_EXTRACTION: NONE`

`CURRENT_PROJECT_EVIDENCE_AUTHORITY: UNCHANGED`

`SELF_IMPROVEMENT_PROPOSAL_AUTHORITY: UNCHANGED`

`B2: STOP`

`B3: STOP`

`B4: STOP`

Owner certification requires the normal complete gate:

`python scripts/clean_project_caches.py`

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`
