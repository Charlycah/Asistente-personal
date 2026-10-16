# ROBY XI.2 — D:\Roby GREEN — SURGICAL RECONCILIATION & REPAIR

Date: 2026-10-05
Status: LOCAL FOCUSED GREEN / OWNER FULL CERTIFICATION REQUIRED

## Trigger

Owner certification of the first surgical GREEN stopped during collection because
an earlier architectural contract imported the pre-existing canonical name
`DevelopmentHistorySourceAdapter`.

## Reconciliation

Historical evidence confirmed two earlier contracts for the same governed source:

- `DevelopmentHistorySourceAdapter` / `HistoricalSourceKind` for bounded read-only
  development-history evidence;
- explicit owner consultation through `development_history.consult`.

The repair therefore preserves one source authority. The newer
`DevelopmentHistoryRootDiscoveryAdapter` name is only a compatibility surface to
that same class; it is not a second adapter or authority.

## Contract conflict resolved

The newer RED excluded ZIP archives from discovery. The historical contract
requires ZIP archives to remain visible as opaque historical metadata while
forbidding direct reads. The reconciled rule is:

`ZIP: DISCOVERABLE_OPAQUE_METADATA / NOT_READABLE / NOT_INGESTIBLE`.

Direct-readable candidates are ordered before opaque metadata so bounded discovery
is not displaced by archives.

## Boundaries preserved

- `ROBY_DEVELOPMENT_HISTORY_ROOT` remains the only deployment root configuration.
- No hardcoded `D:\Roby` product path.
- Read-only source; no history or code mutation.
- Historical material remains `current_truth=False`.
- No Memory, Knowledge, Reasoning, diagnostics, proposal generation, Planning or
  Execution authority is added to the source.
- Explicit consultation is human-scoped and `human_approval` initiated.
- Historical findings remain hypotheses requiring current-project verification
  before any governed improvement proposal.

## Focused certification

52 PASS / 0 FAIL across:

- current D:\Roby source contract;
- recovered explicit-owner history consultation contract;
- Document Inbox regression;
- CAP-17 governed local-library catalogue regression.

No lines over 88 characters in the repaired implementation modules.

## STOP

Full Owner certification is required before this GREEN can be closed.

## V2 — historical contract shape reconciliation

Owner full-suite certification exposed four remaining failures in the historical
source contract. The failures were limited to compatible data-shape surfaces:
`candidate.kind`, `candidate.snapshot_segment`, and `observation.candidate`.

The canonical `DevelopmentHistorySourceAdapter` remains the single source
authority. V2 adds only derived compatibility surfaces: `kind` maps the existing
`source_kind`, `snapshot_segment` derives from the governed relative path, and
an observation retains the exact revalidated candidate. No new discovery,
reading, ingestion, reasoning, mutation, or autonomous authority was added.

Local focused reconciliation: 64 passed / 0 failed across both D:\\Roby
contracts, Document Inbox, D:\\Documentos ingestion, and CAP-17 catalogue.
The execution environment used for packaging has no Ruff executable; Owner
certification remains authoritative for repository-wide Ruff and pytest.
