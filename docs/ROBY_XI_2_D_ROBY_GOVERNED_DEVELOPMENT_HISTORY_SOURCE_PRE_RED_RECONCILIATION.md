# ROBY XI.2 — D:\Roby Governed Development History Source

## PRE-RED Reconciliation

### Classification

- Block: PRE-RED RECONCILIATION / DOCUMENTARY
- Starting baseline: OWNER-CERTIFIED / 13,401 PASS / Ruff clean
- Selected residual: `AUTHORIZED_READ_ONLY_DEVELOPMENT_HISTORY_SOURCE_AND_TRUST_PROJECTION`
- Product change: NONE
- Test change: NONE
- New cognitive/domain authority: NONE
- CONTRACT RED: STOP pending Owner certification

### Owner intent

`D:\Roby` is an authorized read-only development-history corpus. ROBY may inspect
explicitly selected historical material, explain what it found, compare it with the
current project, and suggest a possible improvement with rationale, scope, risks and
validation needs under human review.

It must never modify the history or treat historical material as permission to modify
code, architecture, configuration, Memory or Learning.

### Existing authorities to reuse

The current repository already owns the downstream chain:

- `DocumentReadingService`: explicit file text extraction;
- `DocumentInboxManager`: canonical ingested-document lifecycle;
- `PersonalDocumentReasoningAdmissionAdapterV1`: explicit DocumentRecord admission to
  the existing governed Reasoning gateway;
- self-diagnostics: observation, hypothesis and reproducible-proof gates;
- `generate_diagnostic_proposal_request`: current-project hash-bound proposal evidence;
- canonical Governed Proposal model/inbox and human review.

No new Reasoning, Inbox, self-improvement authority, Proposal authority, Memory or
Learning authority is justified.

### Reuse boundary with Personal Documents and CAP-17

`PersonalDocumentRootDiscoveryAdapter` proves the closest application-side mechanical
pattern: configured root, bounded deterministic discovery, relative provenance,
symlink rejection, containment, revalidation and explicit ingestion.

CAP-17 independently proves governed-root security semantics.

Their security/mechanical semantics are reusable. Their domain identities are not.

`DEVELOPMENT_HISTORY != PERSONAL_DOCUMENTS`

`DEVELOPMENT_HISTORY != LOCAL_LIBRARY`

The new seam must not emit `local-library:` provenance or silently identify history as
ordinary Personal Documents.

### Smallest seam

The only missing productive seam is:

`AUTHORIZED_DEVELOPMENT_HISTORY_ROOT -> BOUNDED_READ_ONLY_DISCOVERY ->`
`DEVELOPMENT_HISTORY_PROVENANCE/TRUST -> EXPLICIT_SELECTION ->`
`EXISTING_READER/INBOX/REASONING`

A narrow application-side adapter may own this mechanical source boundary. It is not a
new cognitive authority and owns no durable document lifecycle.

### Governed configuration

The deployment root authorized by the Owner is `D:\Roby`.

Product code must never hardcode that path. The proposed dedicated configuration key
for the first contract is:

`ROBY_DEVELOPMENT_HISTORY_ROOT`

Absence of that setting must provision no development-history source.

Tests must use temporary roots and must never depend on the Owner's real directory.

### Discovery contract

The first RED should require:

1. one explicit configured root;
2. read-only operation;
3. deterministic bounded discovery;
4. stable candidate identity;
5. relative-path provenance;
6. root-containment enforcement;
7. external-symlink rejection;
8. revalidation at explicit selection time;
9. no discovery-time ingestion;
10. no startup/background scan;
11. no automatic Reasoning, Memory, Learning, diagnostics or Proposal generation.

### Development-history identity and trust

Each discovered candidate must carry an unambiguous source namespace such as
`development-history:` and an explicit trust classification equivalent to:

`HISTORICAL_DEVELOPMENT_MATERIAL`

That classification is semantic metadata, not a confidence upgrade.

Permanent invariants:

`HISTORICAL_DEVELOPMENT_MATERIAL != CURRENT_EXECUTABLE_PROJECT_EVIDENCE`

`HISTORICAL_FINDING != CURRENT_DEFECT`

`HISTORICAL_SUGGESTION != CHANGE_AUTHORIZATION`

The source seam must not manufacture `DiagnosticProjectFileEvidence`, reproduced proof
or any equivalent current-project certification from historical material.

### Formats

The development-history corpus may contain more than ordinary Personal Documents.
The initial contract should distinguish two classes rather than ingest everything:

- readable historical text/document candidates, using formats already supported by
  `DocumentReadingService` where safe and explicit;
- referential artifacts that may be identified/provenanced but are not automatically
  text-ingested merely because they exist under the root.

No recursive archive/ZIP execution or extraction authority is authorized by this
PRE-RED. Executables, virtual environments, caches and arbitrary binary artifacts are
not candidates for automatic ingestion.

The exact initial readable suffix set belongs in CONTRACT RED and must be bounded to
formats already supported by the existing reader. It must not create a new parser.

### Explicit selection and downstream handoff

Discovery produces transient source candidates only.

`DISCOVERED_HISTORY_CANDIDATE != DOCUMENT_RECORD`

Only an explicitly selected and revalidated readable candidate may be handed through
the existing reader into the canonical Document Inbox. Only explicit document IDs may
then reach governed Reasoning through the existing admission path.

No automatic cognition follows discovery or ingestion.

### Improvement-suggestion boundary

Historical material may tell ROBY where to investigate. It cannot prove that the
current system is defective.

A valid advisory chain is:

`historical finding -> current-state verification -> explanation -> possible improvement`

If the observation is promoted into the existing self-improvement Proposal path, the
current gates remain mandatory:

`current executable/project evidence -> reproduced proof -> hash-verified current files/tests ->`
`Governed Proposal -> human review`

The historical source cannot satisfy or bypass those gates.

### Mutation boundary

The development-history source has no write operation.

It must not:

- edit, rename, delete or create files in `D:\Roby`;
- patch current project code;
- alter architecture/governance/configuration;
- write Memory or Learning automatically;
- trigger self-diagnostics automatically;
- create or approve a Proposal automatically;
- authorize Planning, Execution or autonomous application.

### Duplicate-risk exclusions

Do not create `DevelopmentHistoryManager`, `SelfHistoryBrain`,
`SelfImprovementManager`, another Document Inbox, another Reasoning gateway, another
Proposal inbox, an autonomous patcher or a background history watcher.

### Exact RED target

Subject to Owner certification of this PRE-RED, the next block may be:

`D:\Roby GOVERNED DEVELOPMENT HISTORY SOURCE — CONTRACT RED`

The RED must be source/trust-side only. It should prove the missing adapter/configuration
contract and reuse existing reader/inbox/reasoning authorities. It must STOP before any
new downstream self-diagnostic or Proposal behavior.

### PRE-RED decision

`D_ROBY_PRE_RED_RECONCILIATION: COMPLETE`

`CANONICAL_MISSING_SEAM: DEVELOPMENT_HISTORY_SOURCE_AND_TRUST_PROJECTION`

`CONFIGURATION: ROBY_DEVELOPMENT_HISTORY_ROOT`

`SOURCE_ACCESS: READ_ONLY / EXPLICIT / BOUNDED`

`HISTORICAL_TRUST: NON_CURRENT_PROJECT_EVIDENCE`

`DOWNSTREAM_AUTHORITIES: EXISTING / REUSE`

`AUTOMATIC_MEMORY_LEARNING_DIAGNOSTICS_PROPOSAL: FORBIDDEN`

`CODE_OR_HISTORY_MUTATION: FORBIDDEN`

`CONTRACT_RED_READINESS: YES`

`CONTRACT_RED_AUTHORIZATION: NO — STOP FOR OWNER CERTIFICATION`
