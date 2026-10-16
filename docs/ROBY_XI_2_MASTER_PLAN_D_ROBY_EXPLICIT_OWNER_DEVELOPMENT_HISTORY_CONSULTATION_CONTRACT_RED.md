# ROBY XI.2 — D:\Roby explicit Owner development history consultation
## CONTRACT RED

Status: CONTRACT RED / local controlled RED confirmed.

## 1. Baseline

This block starts from the complete PRE-RED reconciliation baseline for explicit
Owner development-history consultation.

The productive development-history source is already Owner-certified and is not
reopened here. The source remains read-only, bounded, historical, and not current
truth.

Starting Owner truth remains:

- pytest: 13,373 PASS / 0 FAIL;
- Ruff: clean;
- governed development-history source: CLOSED / OWNER-CERTIFIED.

## 2. Governing decision

The missing residual is reachability only:

`EXPLICIT_OWNER_DEVELOPMENT_HISTORY_CONSULTATION_ADMISSION_AND_PRESENTATION`

No new source, manager, reasoning authority, memory authority, knowledge
authority, self-improvement authority, or execution gateway is authorized.

The canonical route fixed by this contract is:

`explicit Owner intent`
`-> OfficialRuntimeCapabilityRegistry`
`-> subordinate conversation interception port`
`-> DevelopmentHistorySourceAdapter`
`-> safe presentation`
`-> STOP`

The Level-2 evidence gateway is not required for this direct Owner route.

## 3. Expected absent seam

The RED intentionally expects one missing application seam:

`app.development_history_consultation_runtime`

Its future contract surface is limited to:

- `DevelopmentHistoryConsultationInterceptionPort`;
- `development_history_consult_descriptor()`;
- `build_development_history_consultation_runtime_from_environment(...)`.

These names describe a subordinate runtime adapter. They do not establish a new
cognitive authority.

## 4. Capability descriptor contract

The capability name is exactly:

`development_history.consult`

The descriptor must declare:

- read permission;
- read-only effect;
- human interaction scope;
- human-approval initiation;
- no autonomous initiation.

The descriptor does not authorize Reasoning, Learning, Memory, Knowledge,
proposal generation, or mutation.

## 5. Explicit admission contract

Admission must be narrow and explicit.

Positive requests may explicitly name the development history or `D:\Roby`.
Generic mentions such as `historia`, `ROBY`, `archivos`, `código`, or
`desarrollo` alone are insufficient.

The port must return `None` for unrelated or insufficiently explicit requests so
the canonical conversation pipeline can continue normally.

## 6. Discovery and matching contract

The port reuses `DevelopmentHistorySourceAdapter.discover()`.

Initial consultation matching is metadata-only and deterministic. Matching is
against safe candidate path/name metadata. It must not read candidate content in
order to find matches.

The port must not create a second filesystem crawler, index, repository, or
search authority.

The source's existing candidate bound remains authoritative. The consultation
port must not silently increase it.

## 7. Presentation privacy

Candidate presentation may expose only bounded safe metadata needed for human
selection, including:

- ordinal;
- relative path;
- source kind;
- optionally suffix or size.

It must not expose:

- the configured absolute root;
- internal `source_reference`;
- full candidate identity;
- credentials or excluded paths.

## 8. Explicit selection and ephemeral state

Disambiguation state is transient and scoped by `session_id`.

The contract permits a short TTL of five minutes. Expired state must not admit a
selection.

A selection may resolve only to candidates that were presented for that session.
Accepted selection forms are:

- a visible ordinal;
- an exact presented relative path.

An arbitrary candidate ID supplied by the caller is not an admissible selection
surface.

Cancellation must clear pending state.

No pending consultation state may be written to Memory, Knowledge, a database,
or project files.

## 9. Selected read contract

A selected direct source is read only through
`DevelopmentHistorySourceAdapter.read_selected()`.

That existing source method remains responsible for revalidation, containment,
symlink rejection, byte limits, character limits, UTF-8 validation, and changed
source rejection.

The consultation port must not implement a second file reader.

## 10. Archive contract

ZIP candidates remain `opaque_archive` metadata only.

They may be shown as historical artifacts, but selecting one must not extract,
traverse, decode, or otherwise read archive contents.

## 11. Runtime registration contract

The environment builder reuses `ROBY_DEVELOPMENT_HISTORY_ROOT` through the
existing source builder.

When that root is absent, no consultation capability is registered.

When the source is validly provisioned, the builder registers exactly
`development_history.consult` in the existing
`OfficialRuntimeCapabilityRegistry` with the subordinate interception port.

No second registry or gateway is authorized.

## 12. Trust barrier

The following invariants remain mandatory:

`HISTORICAL_PRESENTATION != CURRENT_TRUTH`

`HISTORICAL_PRESENTATION != DIAGNOSTIC_PROJECT_EVIDENCE`

`HISTORICAL_PRESENTATION != REASONING_ADMISSION`

`HISTORICAL_PRESENTATION != MEMORY_WRITE`

`HISTORICAL_PRESENTATION != KNOWLEDGE_WRITE`

`HISTORICAL_PRESENTATION != LEARNING_ADMISSION`

`HISTORICAL_PRESENTATION != PROPOSAL_AUTHORIZATION`

`HISTORICAL_PRESENTATION != CODE_MUTATION`

A future comparison with the current project must reacquire current evidence
through the existing current-project evidence authority.

## 13. Contract tests

The RED adds one architecture contract file with fourteen tests.

Eleven tests specify absent productive behavior:

1. consultation port, builder, and descriptor exist;
2. descriptor is human/read-only and not autonomous;
3. only explicit development-history intent is admitted;
4. discovery matching uses metadata and does not search content;
5. disambiguation exposes only safe relative metadata;
6. follow-up selection is session-scoped and ordinal-capable;
7. only a presented relative path or ordinal may select;
8. pending selection expires and supports cancellation;
9. ZIP is opaque metadata and cannot be read;
10. builder registers only with explicit governed root configuration;
11. the official registry can execute the explicit Owner consultation.

Three guardrails already pass:

1. historical source observations remain non-current truth;
2. the source remains free of cognitive/mutation integration;
3. direct Owner routing does not require Level-2 execution.

## 14. Local RED result

Directed command:

`python -m pytest -q tests/architecture/`
`test_master_plan_d_roby_explicit_owner_history_consultation_contract_red.py`

Observed local result:

`11 failed, 3 passed`

Every intended RED fails because:

`ModuleNotFoundError: No module named`
`'app.development_history_consultation_runtime'`

No guardrail failure is present.

This is the expected controlled RED shape.

## 15. STOP boundaries

This contract does not authorize GREEN yet.

It also does not authorize:

- automatic historical consultation;
- startup/background scans;
- content indexing or semantic historical search;
- Level-2 planning fabrication for direct Owner requests;
- automatic Reasoning admission;
- Memory, Knowledge, or Learning persistence;
- historical-to-`DiagnosticProjectEvidence` conversion;
- historical-to-proposal handoff;
- archive extraction;
- code mutation;
- B2/B3/B4 expansion.

## 16. Certification state

`CONTRACT_RED: LOCALLY_CONFIRMED`

`EXPECTED_RED_FAILURES: 11 / 11`

`GUARDRAILS: 3 / 3 PASS`

`UNEXPECTED_FAILURES: 0`

`PRODUCT_CHANGE: NONE`

`NEW_AUTHORITY: NONE`

`B2/B3/B4: STOP`

Owner certification must run the normal global gate before any SURGICAL GREEN:

`python scripts/clean_project_caches.py`

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`

Expected global shape is the previous 13,373 passing tests plus these three new
passing guardrails and eleven controlled RED failures.

Therefore the expected Owner RED summary is:

`11 failed, 13376 passed`

STOP before GREEN.
