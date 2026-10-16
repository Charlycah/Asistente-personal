# ROBY XI.2 — MASTER PLAN

## D:\Documentos Authorized Root Discovery to Explicit Inbox Ingestion

### CONTRACT RED

#### Starting authority

- Baseline: Owner-certified 13,347 PASS / Ruff clean.
- PRE-RED residual:
  `AUTHORIZED_PERSONAL_DOCUMENT_ROOT_DISCOVERY_TO_EXPLICIT_INBOX_INGESTION`.
- Product code change: NONE.
- New domain authority: NONE.
- B2 / B3 / B4: STOP.

#### Existing owners preserved

Document lifecycle remains owned by:

`core.document_inbox.DocumentInboxManager`

Durable persistence remains owned by:

`core.document_inbox.DocumentRepository`

Durable identity remains:

`core.document_inbox.DocumentRecord.document_id`

Filesystem content extraction remains owned by:

`app.document_reading.DocumentReadingService`

Governed Reasoning admission remains the existing explicit Personal Document
admission path.

The RED does not authorize replacements for any of those owners.

#### Missing seam contracted

The missing application-side seam is represented contractually as:

`app.personal_document_source.PersonalDocumentRootDiscoveryAdapter`

with environment construction through:

`build_personal_document_source_from_environment(...)`

These names describe a subordinate adapter role.

They do not authorize a second Document Inbox, repository, Knowledge Base or
Reasoning authority.

#### Configuration contract

The source root is configured only through:

`ROBY_PERSONAL_DOCUMENTS_ROOT`

No product code may hardcode:

`D:\Documentos`

The environment builder returns no source adapter when the variable is absent.

When configured, the adapter exposes the resolved authorized root.

#### Discovery contract

Discovery is transient and read-only.

It must:

- remain inside the configured root;
- recurse deterministically;
- sort candidates by relative path;
- include only contracted Personal Documents formats;
- enforce a positive candidate bound;
- report truncation when more candidates exist;
- preserve deterministic candidate identity and source provenance;
- preserve relative path, suffix, size and modification timestamp;
- not use CAP-17 `local-library:` identity.

The first contracted suffix family is:

- `.txt`;
- `.md`;
- `.csv`;
- `.json`;
- `.html`;
- `.htm`;
- `.docx`;
- `.pdf`;
- `.epub`.

`.py` and `.log` remain outside this source contract.

#### Discovery is not ingestion

Calling `discover()` must not call Document Inbox ingestion and must not persist a
`DocumentRecord`.

Invariant:

`DISCOVERED_SOURCE_CANDIDATE != INGESTED_DOCUMENT_RECORD`

#### Explicit selected ingestion

Only an explicit candidate identity may reach ingestion.

The required sequence is:

`candidate id -> source revalidation -> DocumentReadingService.read_text() ->
DocumentInboxManager.ingest_text() -> DocumentRecord`

The adapter must receive the existing reader and Inbox collaborators.

It must not construct another `DocumentInboxManager`.

The resulting durable identity is the existing `DocumentRecord.document_id`.

#### Revalidation

A candidate selected after discovery must be revalidated before reading.

If the file disappeared, escaped the authorized root, became an external symlink or
otherwise ceased to satisfy the source contract, ingestion fails closed.

No path reconstruction outside the authorized root is allowed.

#### Symlink contract

External symlinks are not candidates by default.

They cannot become an ingestion path.

The test permits a platform skip only when symlink creation is unavailable.

#### CAP-17 boundary

CAP-17 security semantics are reused as contract invariants.

CAP-17 library authority and library entity types are not reused as Personal
Documents identity.

No Personal Documents candidate may use `local-library:` provenance.

#### Protected cognition

This RED does not authorize:

- automatic Reasoning;
- automatic Knowledge creation;
- automatic Memory;
- automatic Learning;
- background ingestion;
- startup ingestion;
- autonomous selection;
- conversational filesystem search;
- semantic retrieval over the source root.

#### RED test

Added:

`tests/architecture/`
`test_master_plan_d_documentos_authorized_root_discovery_to_`
`explicit_inbox_ingestion_contract_red.py`

The contract contains twelve tests.

Expected RED failures:

1. source adapter and environment builder do not exist;
2. environment source-root provisioning is missing;
3. bounded filtered deterministic discovery is missing;
4. candidate relative-path provenance is missing;
5. discovery-without-ingestion seam is missing;
6. explicit reader-to-existing-Inbox handoff is missing;
7. selected-source revalidation is missing;
8. external-symlink exclusion in this source seam is missing;
9. exact Personal Documents suffix discovery is missing.

Expected guardrail passes:

10. no hardcoded `D:\Documentos` or CAP-17 library identity in protected owners;
11. existing `DocumentInboxManager` remains lifecycle authority;
12. runtime has no automatic Personal Documents source or second Inbox wiring.

#### Directed local RED result

`9 FAILED / 3 PASSED`

All nine failures are expected and originate from the absent
`app.personal_document_source` seam.

No unexpected product failure was observed in the directed contract.

The three authority and boundary guardrails remain GREEN.

#### RED interpretation

The current failure is not evidence that Document Inbox, Document Reading or
Reasoning are missing.

It is evidence only that the authorized Personal Documents source adapter is absent.

Therefore GREEN must not solve the RED by:

- changing Document Inbox ownership;
- copying CAP-17 catalogue types;
- adding another repository;
- bypassing `DocumentReadingService`;
- ingesting during discovery;
- adding downstream cognition;
- hardcoding the user's source root.

#### Expected GREEN surface

The narrow GREEN may add one application-side source adapter and the minimum runtime
builder/wiring required to provision it with the existing canonical collaborators.

The GREEN should not require changes to:

- `DocumentRecord`;
- `DocumentRepository`;
- Reasoning;
- Knowledge;
- Memory;
- Learning;
- CAP-17 catalogue authority.

Any such requirement must trigger reconciliation rather than silent scope growth.

#### Status

`CONTRACT_RED: LOCALLY_CONFIRMED`

`EXPECTED_RED_FAILURES: 9 / 9`

`EXPECTED_GUARDRAIL_PASSES: 3 / 3`

`UNEXPECTED_FAILURES: 0`

`PRODUCT_CHANGE: NONE`

`NEW_AUTHORITY: NONE`

`NEXT_ACTION:
D:\Documentos AUTHORIZED ROOT DISCOVERY TO EXPLICIT INBOX INGESTION —
SURGICAL GREEN`

STOP before GREEN until Owner RED certification.

`B2: STOP`

`B3: STOP`

`B4: STOP`
