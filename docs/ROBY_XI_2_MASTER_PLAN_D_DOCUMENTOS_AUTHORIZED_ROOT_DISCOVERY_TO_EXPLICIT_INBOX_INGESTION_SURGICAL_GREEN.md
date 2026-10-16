# ROBY XI.2 — MASTER PLAN

## D:\Documentos Authorized Root Discovery to Explicit Inbox Ingestion

### SURGICAL GREEN

#### Starting certification

- CONTRACT RED: Owner-certified.
- Expected RED failures: 9 / 9.
- Other tests at RED: 13,350 PASS.
- Ruff at RED: clean.
- Selected residual:
  `AUTHORIZED_PERSONAL_DOCUMENT_ROOT_DISCOVERY_TO_EXPLICIT_INBOX_INGESTION`.
- B2 / B3 / B4: STOP.

#### Productive change

Added one application-side adapter:

`app.personal_document_source`

No existing productive file was modified.

The adapter composes the existing:

- `DocumentReadingService`;
- `DocumentInboxManager`.

It does not construct or replace either authority.

#### Source models

The adapter exposes transient immutable evidence:

- `PersonalDocumentSourceCandidate`;
- `PersonalDocumentDiscovery`.

These are filesystem-source evidence only.

They are not:

- `DocumentRecord`;
- repository entities;
- Knowledge entities;
- Memory;
- Learning;
- CAP-17 library entries.

#### Authorized root

`PersonalDocumentRootDiscoveryAdapter` requires one explicit root.

The environment builder reads only:

`ROBY_PERSONAL_DOCUMENTS_ROOT`

When the variable is absent, it returns `None`.

`D:\Documentos` is not hardcoded.

The configured root is resolved and must be a directory.

#### Discovery

Discovery is recursive, deterministic, bounded and read-only.

The contracted suffixes are:

- `.txt`;
- `.md`;
- `.csv`;
- `.json`;
- `.html`;
- `.htm`;
- `.docx`;
- `.pdf`;
- `.epub`.

`.py` and `.log` remain excluded.

Candidates are sorted by relative path.

The result reports `truncated=True` when more valid candidates exist than the
configured bound.

#### Provenance

Each candidate preserves:

- deterministic `candidate_id`;
- relative path;
- Personal Documents source reference;
- suffix;
- size;
- modification timestamp.

The source reference uses the Personal Documents namespace.

It does not use CAP-17 `local-library:` identity.

#### Containment and symlinks

Discovery ignores symlinks.

A selected source is resolved again before reading and must remain inside the
authorized root.

External symlinks and root escape fail closed.

#### Discovery is not ingestion

`discover()` does not call the Document Inbox.

It creates no `DocumentRecord`.

Invariant:

`DISCOVERED_SOURCE_CANDIDATE != INGESTED_DOCUMENT_RECORD`

#### Explicit selected ingestion

`ingest_selected(candidate_id)` accepts only a candidate from the last bounded
discovery result.

That discovery index is process-local and transient.

It is not durable state or a second repository.

The selected candidate is revalidated against its prior source evidence.

If the source disappeared or changed identity, ingestion fails closed.

A valid selection follows:

`candidate -> revalidation -> DocumentReadingService.read_text() ->
DocumentInboxManager.ingest_text() -> DocumentRecord`

The durable identity remains the existing `DocumentRecord.document_id`.

#### Existing owners preserved

No changes were made to:

- `core.document_inbox`;
- `DocumentRepository`;
- `DocumentRecord`;
- `DocumentReadingService`;
- CAP-17;
- Reasoning;
- Knowledge;
- Memory;
- Learning.

No second Document Inbox is constructed.

#### Runtime boundary

The contracted environment builder lives with the source adapter.

No automatic runtime construction was added.

This preserves the CONTRACT RED guardrail that source-root configuration alone does
not create background ingestion or a second Inbox.

A later productive caller may explicitly compose the builder with the existing
canonical Inbox and reader if a separately demonstrated reachability residual
requires it.

#### No automatic cognition

The GREEN adds no:

- watcher;
- startup scan;
- automatic ingestion;
- autonomous selection;
- conversational filesystem search;
- semantic source retrieval;
- automatic Reasoning;
- automatic Knowledge creation;
- Memory;
- Learning.

#### Directed verification

The twelve CONTRACT RED tests are GREEN:

`12 PASSED`

This proves:

- adapter and builder existence;
- explicit environment provisioning;
- deterministic bounded discovery;
- Personal Documents provenance;
- discovery without ingestion;
- existing reader and Inbox reuse;
- selected-source revalidation;
- external-symlink exclusion;
- exact source suffix family;
- no hardcoded personal root;
- existing Inbox authority;
- no automatic runtime source wiring.

All modified Python compiles.

No changed or added text file contains a line over 88 characters.

#### Scope

The GREEN closes only the contracted source seam.

It does not claim ordinary conversational reachability for source discovery or
ingestion.

That question requires a later reconciliation after Owner global certification.

#### Status

`AUTHORIZED_PERSONAL_DOCUMENT_ROOT_DISCOVERY_TO_EXPLICIT_INBOX_INGESTION:
LOCAL_GREEN`

`DOCUMENT_LIFECYCLE_AUTHORITY: EXISTING_DOCUMENT_INBOX_MANAGER`

`DOCUMENT_READER: EXISTING_DOCUMENT_READING_SERVICE`

`DISCOVERY: TRANSIENT / READ_ONLY`

`INGESTION: EXPLICIT_ONLY`

`CAP17_LIBRARY_AUTHORITY: UNCHANGED`

`PARALLEL_DOCUMENT_AUTHORITY: NONE`

`DIRECTED_CONTRACT: 12 PASS`

`GLOBAL_CERTIFICATION: PENDING_OWNER`

`B2: STOP`

`B3: STOP`

`B4: STOP`
