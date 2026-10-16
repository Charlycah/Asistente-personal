# ROBY XI.2 — MASTER PLAN

## D:\Documentos Governed Authorized Source — PRE-RED Reconciliation

### Classification

- Block: PRE-RED RECONCILIATION / DOCUMENTARY
- Starting baseline: OWNER-CERTIFIED / GLOBAL GREEN
- Starting suite: 13,347 passed / 0 failed
- Starting Ruff: clean
- Selected horizon: `D_DOCUMENTOS_GOVERNED_AUTHORIZED_SOURCE`
- Product change: NONE
- Test change: NONE
- New domain authority: NONE
- B2 / B3 / B4: STOP

### Authority already settled

Historical Gate 3 work already settled the primary domain ownership.

Canonical Personal Documents lifecycle authority:

`core.document_inbox.DocumentInboxManager`

Canonical persistence port:

`core.document_inbox.DocumentRepository`

Canonical durable document entity:

`core.document_inbox.DocumentRecord`

The official runtime already provisions one durable Document Inbox through
`build_document_inbox_from_environment()` and shares that instance with existing
consumers.

Therefore no new document lifecycle manager, repository authority, Knowledge
authority or Reasoning authority is justified.

### Database path is not a source root

Current Document Inbox configuration includes:

- `ROBY_DOCUMENT_INBOX_ENABLED`;
- `ROBY_DOCUMENT_INBOX_DB_PATH`.

The DB path persists already-ingested `DocumentRecord` values.

It is not a filesystem collection root.

Invariant:

`DOCUMENT_INBOX_DB_PATH != DOCUMENT_SOURCE_ROOT`

No current configuration provisions `D:\Documentos` as an authorized Personal
Documents source root.

### Existing explicit ingestion

`DocumentInboxManager.ingest_path()` accepts one caller-supplied file.

It requires an existing file, reads TXT/MD/CSV/JSON directly, then delegates
lifecycle semantics to `ingest_text()`.

The Inbox continues to own deduplication, classification, Scope Guard, status and
durable persistence.

`ingest_path()` does not authorize a root, discover a collection, preserve governed
relative-path provenance, reject collection escape or govern source symlinks.

Therefore it is ingestion, not authorized-source discovery.

### Existing reader

`app.document_reading.DocumentReadingService` already performs bounded explicit
document reading.

Its readable family includes TXT, MD, CSV, JSON, LOG, PY, HTML/HTM, DOCX, PDF and
EPUB.

It remains a reader/extractor, not a source authority or repository.

A governed source seam may call `read_text()` for one explicitly selected source and
then hand extracted content to the existing Document Inbox.

The dependency remains application-side.

`core.document_inbox` must not import `app.document_reading`.

### Existing Reasoning admission

`PersonalDocumentReasoningAdmissionAdapterV1` already admits only explicitly
selected `DocumentRecord.document_id` values from the Document Inbox into the
existing governed Reasoning gateway.

Therefore:

`FILESYSTEM_DISCOVERY != REASONING_ADMISSION`

`SOURCE_SELECTION != AUTOMATIC_REASONING`

No new Reasoning seam is required here.

### CAP-17 comparison

CAP-17 already demonstrates the required governed-root security semantics:

- one explicitly authorized root;
- bounded read-only discovery;
- relative-path containment;
- external symlinks not followed by default;
- deterministic entry identity and provenance;
- root-escape rejection;
- bounded catalogue size;
- explicit selection before reading.

Those invariants are reusable.

The CAP-17 implementation itself is domain-specific. It produces
`GovernedLibraryEntry`, `GovernedLibraryCatalogue`,
`GovernedLibrarySearchResult` and `local-library:` source references.

Directly using that catalogue for Personal Documents would merge Biblioteca
identity and provenance into a different domain.

Decision:

`CAP17_SECURITY_SEMANTICS: REUSABLE`

`CAP17_LIBRARY_AUTHORITY: NOT_REUSABLE_AS_DOCUMENT_AUTHORITY`

`CAP17_LIBRARY_ENTITY_TYPES: NOT_REUSABLE_AS_DOCUMENT_IDENTITY`

### No second durable document catalogue

The missing seam must not become another durable document catalogue.

The durable source of truth for ingested Personal Documents remains the existing
Document Inbox repository.

Filesystem discovery may expose transient candidates under one authorized root.

Those candidates are not `DocumentRecord` values and do not own document lifecycle.

Invariant:

`DISCOVERED_SOURCE_CANDIDATE != INGESTED_DOCUMENT_RECORD`

### Selected seam

The smallest missing seam is:

`AUTHORIZED_PERSONAL_DOCUMENT_ROOT_DISCOVERY_TO_EXPLICIT_INBOX_INGESTION`

Its responsibilities are limited to:

1. provision one explicit Personal Documents root from governed configuration;
2. enumerate only contracted source candidates inside that root;
3. preserve relative path and deterministic source provenance;
4. reject root escape;
5. not follow external symlinks by default;
6. bound discovery;
7. revalidate one explicitly selected candidate before ingestion;
8. read that candidate through the existing reading authority;
9. hand extracted text to the existing `DocumentInboxManager`;
10. return the resulting existing `DocumentRecord`.

This seam is not a new cognitive or document-lifecycle authority.

### Owner boundaries

Document lifecycle remains owned by `DocumentInboxManager`.

Filesystem reading remains owned by `DocumentReadingService`.

Reasoning remains owned by the existing governed Reasoning path plus the existing
explicit Personal Document admission adapter.

Only authorized-root discovery is currently unowned for Personal Documents.

A narrow application/infrastructure adapter may own that mechanical boundary while
remaining subordinate to Document Inbox.

It must not behave as another Inbox, Knowledge Base or Reasoning system.

### Governed configuration

The user-authorized deployment root is:

`D:\Documentos`

It must never be hardcoded in product code.

The first contract should provision it through a dedicated environment setting:

`ROBY_PERSONAL_DOCUMENTS_ROOT`

This is distinct from:

- `ROBY_DOCUMENT_INBOX_DB_PATH`;
- `ROBY_LOCAL_LIBRARY_ROOT`;
- visual collection configuration;
- local music configuration.

Tests must use temporary roots and must not depend on the user's actual directory.

### Initial source formats

The first source-root contract should use the Personal Documents subset:

- `.txt`;
- `.md`;
- `.csv`;
- `.json`;
- `.html`;
- `.htm`;
- `.docx`;
- `.pdf`;
- `.epub`.

Although the generic reader can also read `.log` and `.py`, those are not promoted
into this first Personal Documents source contract.

This prevents `D:\Documentos` from silently becoming a general development-source
scanner.

### Source provenance

Discovery needs provenance before a `DocumentRecord` exists.

It should preserve at least:

- authorized-root identity;
- relative path;
- deterministic candidate identity;
- suffix;
- size;
- modification timestamp.

Personal Documents provenance must not use CAP-17's `local-library:` namespace.

Absolute personal paths must not become canonical durable document identity.

After ingestion, `DocumentRecord.document_id` remains the canonical durable
identifier.

### Explicit selection only

Discovery must never ingest by itself.

Allowed progression:

`authorized root -> transient discovery -> explicit candidate selection ->
selected-source validation -> bounded reading -> DocumentInboxManager ingestion`

Not authorized:

- background watcher;
- startup ingestion;
- recursive automatic ingestion;
- autonomous selection;
- automatic Knowledge creation;
- automatic Reasoning;
- automatic Memory;
- automatic Learning.

### Ingestion handoff

For one explicitly selected source candidate, the future seam should:

1. revalidate the candidate against the authorized root;
2. read it through `DocumentReadingService.read_text()`;
3. call `DocumentInboxManager.ingest_text()`;
4. supply bounded source metadata;
5. return the canonical `DocumentRecord`.

Current `source_name` may carry a visible source name but must not become canonical
filesystem provenance identity.

No `DocumentRecord` schema expansion is authorized unless CONTRACT RED proves it is
necessary.

### Read-only source boundary

The governed source seam is read-only with respect to `D:\Documentos`.

It must not rename, move, edit, delete, overwrite or create source files.

Document Inbox persistence remains separate and may write only its own existing
repository representation.

### Symlink and escape boundary

The CAP-17 security semantics become contractual requirements:

`SELECTED_SOURCE_RESOLVED_PATH MUST REMAIN WITHIN AUTHORIZED_ROOT`

Default:

`FOLLOW_SYMLINKS: FALSE`

External symlinks must not become candidates or ingestion paths.

Absolute and relative escape attempts fail closed.

### Determinism and boundedness

Discovery must be deterministic and bounded.

The first contract should require stable relative-path ordering, deterministic
candidate identity for unchanged source metadata, a positive candidate limit and
explicit truncation evidence.

This remains transient source discovery, not a second durable repository.

### Runtime reachability

The official runtime already constructs the canonical `DocumentInboxManager`.

A future GREEN must reuse that exact instance.

The source adapter must not construct another Inbox.

Provisioning occurs only when the Personal Documents root is explicitly configured.

Without that configuration, current Document Inbox behavior remains unchanged.

### Capability and conversation boundary

This PRE-RED does not authorize broad conversational filesystem search.

The first productive seam proves governed discovery and explicit ingestion only.

Any later conversational surface must reuse this same source seam and the same
Document Inbox.

### D:\Roby remains separate

`D:\Roby` remains outside this block.

The Personal Documents source seam must not become a generic filesystem framework
for development history.

`.py` is therefore excluded from the first Personal Documents source contract.

### Protected authorities

This increment must not alter ownership of Document Inbox, Document Repository,
Personal Knowledge, Task Intelligence, CAP-17 Biblioteca, Knowledge, Reasoning,
Memory, Learning, Planning, Unified Experience, visual collection or local music.

### Candidate adapter role

A narrow role such as:

`PersonalDocumentRootDiscoveryAdapter`

is architecturally acceptable.

It is an adapter, not a new domain manager or durable catalogue authority.

Its state is limited to configured root, discovery bound and transient source
candidate construction.

It should receive existing collaborators instead of constructing replacements:

- the existing `DocumentInboxManager`;
- the existing `DocumentReadingService`.

Exact class and module naming remain CONTRACT RED details.

### Demonstrated residual

The exact missing phenomenon is:

`AUTHORIZED_PERSONAL_DOCUMENT_ROOT_DISCOVERY_TO_EXPLICIT_INBOX_INGESTION`

Today ROBY can ingest a caller-supplied individual text path and can read an explicit
document path.

It cannot yet govern `D:\Documentos` as one authorized Personal Documents source
collection with bounded discovery, containment, source-selection provenance and
explicit handoff into the canonical Document Inbox.

### CONTRACT RED scope

Evidence is sufficient for a narrow RED.

The RED should prove at least:

1. source root comes only from explicit configuration;
2. no hardcoded `D:\Documentos` exists in product code;
3. discovery never escapes the authorized root;
4. external symlinks are not followed by default;
5. only contracted Personal Documents suffixes are candidates;
6. candidate identity and provenance are deterministic;
7. relative path is preserved;
8. discovery is bounded and reports truncation;
9. discovery alone never ingests;
10. only explicit selected-candidate ingestion reaches Document Inbox;
11. selected source is revalidated before reading;
12. existing `DocumentReadingService` performs content reading;
13. existing canonical `DocumentInboxManager` performs ingestion;
14. the adapter constructs no second Inbox;
15. resulting durable identity is existing `DocumentRecord.document_id`;
16. no automatic Reasoning, Memory, Learning or Knowledge creation occurs;
17. CAP-17 library namespace/types are not Personal Documents identity;
18. absent source-root configuration preserves current behavior.

### RED authorization

`RED_AUTHORIZED: YES`

Authorized residual:

`AUTHORIZED_PERSONAL_DOCUMENT_ROOT_DISCOVERY_TO_EXPLICIT_INBOX_INGESTION`

The RED remains source-governance and explicit-ingestion only.

No conversational search, semantic retrieval, background scanning, automatic
ingestion or downstream cognition is authorized.

### Next action

`MASTER PLAN — D:\Documentos AUTHORIZED ROOT DISCOVERY TO EXPLICIT INBOX
INGESTION — CONTRACT RED`

STOP before product implementation.

### Closure

`D_DOCUMENTOS_GOVERNED_AUTHORIZED_SOURCE: NARROWED`

`DOCUMENT_LIFECYCLE_AUTHORITY: EXISTING_DOCUMENT_INBOX_MANAGER`

`DOCUMENT_PERSISTENCE_AUTHORITY: EXISTING_DOCUMENT_REPOSITORY`

`DOCUMENT_READER: EXISTING_DOCUMENT_READING_SERVICE`

`CAP17_SECURITY_SEMANTICS: REUSE_AS_CONTRACT`

`CAP17_LIBRARY_AUTHORITY: NOT_REUSED`

`DISCOVERY: TRANSIENT / READ_ONLY`

`INGESTION: EXPLICIT_ONLY`

`DURABLE_DOCUMENT_IDENTITY: EXISTING_DOCUMENT_RECORD`

`SELECTED_RESIDUAL:
AUTHORIZED_PERSONAL_DOCUMENT_ROOT_DISCOVERY_TO_EXPLICIT_INBOX_INGESTION`

`RED_AUTHORIZED: YES`

`PRODUCT_CHANGE: NONE`

`TEST_CHANGE: NONE`

`B2: STOP`

`B3: STOP`

`B4: STOP`
