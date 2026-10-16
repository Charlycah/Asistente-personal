# ROBY XI.2 — MASTER PLAN

## D:\Roby Governed Development History Source — PRE-RED Reconciliation

### Classification

- Block: PRE-RED RECONCILIATION / DOCUMENTARY.
- Starting baseline: Owner-certified 13,359 PASS / Ruff clean.
- Selected horizon: `D_ROBY_GOVERNED_DEVELOPMENT_HISTORY_SOURCE`.
- Product change: NONE.
- Test change: NONE.
- New authority: NONE.
- CONTRACT RED: NOT AUTHORIZED.
- B2 / B3 / B4: STOP.

### Purpose

This block determines whether the historical ROBY development material located at
`D:\Roby` can become a governed read-only evidence source without confusing it with
the current executable project or with evidence capable of authorizing change.

The source root is deployment information. It must never be hardcoded in product
code.

### Current truth precedence

The project already defines the governing precedence:

`CURRENT EXECUTABLE TRUTH + LATEST OWNER GATE > STALE HISTORICAL STATUS LABEL`

Historical material therefore cannot override current executable evidence, the
latest Owner certification, Current Truth, the Capability Registry or the Cognitive
Inventory.

Required invariant:

`HISTORICAL_DEVELOPMENT_MATERIAL != CURRENT_EXECUTABLE_PROJECT_EVIDENCE`

### Existing self-diagnostic authority

CAP-14 already owns self-diagnostics and governed improvement proposals.

The productive proposal producer is:

`app.self_improvement_proposal_generation.generate_diagnostic_proposal_request()`

It accepts only:

`reproduced proof -> hash-bound current project evidence -> inert proposal`

The current evidence contract requires explicit relative project paths, SHA-256
content digests, existing files under the supplied `project_root`, bounded affected
files and existing validation tests.

It rejects root escape, digest mismatch and protected governance scope.

No historical source may weaken those checks.

### Historical consultation cannot satisfy project evidence

`DiagnosticProjectEvidence` is evidence about the current project tree supplied to
the proposal producer.

Material found under `D:\Roby` must not be accepted as that evidence merely because
it has a matching filename, relative path, digest, test name or historical version.

Required invariant:

`HISTORICAL_CONSULTATION != DIAGNOSTIC_PROJECT_EVIDENCE`

A historical observation may motivate comparison or investigation.

It cannot by itself satisfy the current-project evidence gate for proposal
generation.

### Proposal and mutation boundary

The existing self-improvement chain remains unchanged:

`reproduced diagnostic proof -> current hash-bound project evidence -> inert
proposal -> human review`

Historical consultation does not authorize:

- proposal generation by itself;
- proposal approval;
- patch creation;
- code application;
- file mutation;
- rollback;
- autonomous self-modification;
- Planning or Authorization bypass.

Invariant:

`HISTORICAL_CONSULTATION != PROPOSAL_AUTHORIZATION != CODE_MUTATION`

### Existing read-only evidence semantics

`core.governed_read_only_evidence` already defines a useful epistemic boundary:
read-only observations cannot establish truth and cannot modify state.

That semantic rule is reusable for development-history consultation.

The existing type is not automatically declared the owner of the new local source.
Its authorization/planning lineage belongs to its own governed execution context.

Decision:

`READ_ONLY_EVIDENCE_SEMANTICS: REUSABLE`

`READ_ONLY_EVIDENCE_EXECUTION_AUTHORITY: NOT_REASSIGNED`

### Existing governed information-source query path

`GovernedSourceQueryExecutor` is the canonical executor for registered information
sources owned through the Official Conversation Gateway.

Its source model includes declared topics, information regions and query-contract
semantics designed for governed information sources.

No evidence currently proves that a local development-history filesystem should be
promoted into that taxonomy.

Therefore this PRE-RED does not register `D:\Roby` as a generic information source.

Decision:

`GOVERNED_SOURCE_QUERY_EXECUTOR: EXISTING / NOT_SELECTED_AS_OWNER`

### CAP-17 and Personal Documents precedents

CAP-17 and the Personal Documents source work provide mature filesystem safety
precedents:

- explicit authorized root;
- root containment;
- read-only discovery;
- no external symlink traversal by default;
- deterministic relative-path provenance;
- bounded discovery;
- source-domain-specific identity;
- explicit selection before content use.

Those safety semantics may be reused as contract invariants.

Their domain authorities and entity types must not be reused as development-history
identity.

Decision:

`FILESYSTEM_SECURITY_SEMANTICS: REUSABLE`

`CAP17_LIBRARY_AUTHORITY: NOT_REUSED`

`PERSONAL_DOCUMENT_SOURCE_AUTHORITY: NOT_REUSED`

### Missing source authority

No canonical implementation currently owns `D:\Roby` as a historical development
source.

The missing phenomenon is narrower than self-improvement:

`GOVERNED_READ_ONLY_DEVELOPMENT_HISTORY_SOURCE`

Its eventual responsibility, if authorized, would be only to expose bounded,
provenanced historical material for explicit consultation.

It would not own diagnostics, proposal generation, Reasoning, Knowledge, Memory,
Learning, Planning, Authorization or mutation.

### Candidate owner shape

A future implementation may justify a narrow application/infrastructure source
adapter.

It must not be a new self-improvement manager, diagnostic manager, project manager,
Knowledge Base or second brain.

Conceptual role only:

`DevelopmentHistorySourceAdapter`

Exact class and module naming are not authorized by this PRE-RED.

### Governed configuration

The user-authorized deployment root is:

`D:\Roby`

It must not be hardcoded.

A future contract may use a dedicated setting such as:

`ROBY_DEVELOPMENT_HISTORY_ROOT`

The exact configuration key remains a CONTRACT RED detail.

Tests must use temporary roots and never depend on the user's real directory.

### Provenance requirements

Historical source identity must remain distinct from current project identity.

A future candidate should preserve at least:

- historical-source root identity;
- relative path;
- deterministic source identity;
- file type;
- size;
- modification timestamp when available;
- explicit historical epistemic role.

Absolute personal paths must not become cognitive truth or durable current-project
identity.

A historical source reference must not use CAP-17 `local-library:` identity or the
Personal Documents namespace.

### Temporal and epistemic labeling

Every historical observation must remain explicitly non-current unless independently
verified against the current project.

Required labels or equivalent semantics must preserve:

`epistemic_role = historical_development_evidence_not_current_truth`

A historical file with a newer filesystem timestamp does not automatically outrank
current executable evidence.

A historical file with the same relative path does not become the current file.

A historical test result does not become the latest Owner gate.

### Content use boundary

The source may eventually support explicit consultation such as:

- comparing an older design with current architecture;
- understanding why a capability evolved;
- locating prior implementation approaches;
- recovering historical rationale;
- identifying hypotheses for current investigation.

Any current factual conclusion must still be checked against current executable
truth and the latest governed documentation.

### No automatic Memory or Learning

Historical discovery or reading must not automatically write Memory, Learning,
Knowledge or autobiographical state.

If a later block demonstrates a need to admit historical observations into governed
Reasoning, it must reuse the existing evidence and Reasoning authorities and preserve
the historical/non-truth role.

That downstream seam is not authorized here.

### Corpus-shape evidence gap

The repository contains no reliable evidence describing the real contents of
`D:\Roby`.

The PRE-RED cannot establish whether the root primarily contains:

- source trees;
- Markdown or text documentation;
- JSON evidence;
- ZIP archives;
- complete historical project snapshots;
- databases;
- binaries;
- generated artifacts;
- virtual environments;
- caches;
- secrets or local configuration;
- some combination of these.

This is a material contract gap.

### Why formats cannot be invented

Unlike `D:\Documentos`, the intended source is specifically development history.

A `.py` exclusion would likely discard relevant history.

A broad all-files policy could expose irrelevant binaries, credentials, databases,
virtual environments or generated material.

A ZIP policy would require separate archive-containment, decompression-bound and
nested-path rules.

Therefore no suffix allowlist, archive-reading policy or recursive source semantics
can be certified from current evidence.

### Required corpus characterization

Before CONTRACT RED, obtain a metadata-only inventory of `D:\Roby`.

The inventory must not upload file contents.

It should contain only enough information to establish the source model, preferably:

- relative path;
- directory/file marker;
- extension;
- file size;
- optional modification timestamp;
- aggregate counts by extension;
- aggregate counts by top-level directory.

Sensitive filenames may be redacted if necessary while retaining extension and
structural information.

No file content, hashes or ZIP payloads are required for this characterization.

### Archive boundary

If ZIP or other archive files materially represent the development history, archive
handling requires a separate explicit contract.

At minimum it would need to define:

- archive size bounds;
- uncompressed-size bounds;
- entry-count bounds;
- nested archive policy;
- path traversal rejection;
- symlink-like archive entry handling;
- supported content suffixes inside archives;
- provenance including archive and inner relative path.

This PRE-RED does not authorize archive extraction.

### Secret and local-state boundary

A development tree can contain credentials, environment files, local databases,
private configuration or generated runtime state.

A future contract must define exclusions before broad recursive reading.

At minimum, the source must fail closed around material that the corpus inventory
shows to be sensitive or operational rather than historical evidence.

No current evidence justifies a complete exclusion list yet.

### Current-project collision boundary

The historical root may contain a snapshot whose relative paths exactly match the
current repository.

That collision must never collapse identities.

Required invariant:

`HISTORICAL_PATH_MATCH != CURRENT_PROJECT_FILE_IDENTITY`

Any comparison must retain both source domains explicitly.

### No direct proposal handoff

There must be no direct path:

`development history -> DiagnosticProjectEvidence`

and no direct path:

`development history -> DiagnosticProposalRequest`

If history suggests a possible current defect, the system must reacquire and hash the
corresponding evidence from the actual current `project_root` and reproduce the
existing diagnostic proof before the current proposal chain can proceed.

### Smallest future productive chain

Subject to corpus characterization, the smallest acceptable chain is:

`configured historical root -> bounded read-only discovery -> explicit historical
selection -> bounded read -> historical observation`

STOP there initially.

Reasoning admission, comparison automation and proposal influence remain later
questions.

### PRE-RED questions resolved

1. Current self-improvement owner:
   existing CAP-14/self-diagnostics and proposal boundaries.
2. Current project evidence owner:
   existing hash-bound `DiagnosticProjectEvidence` verification.
3. Historical source owner:
   currently missing.
4. Filesystem security precedent:
   reusable as semantics, not as CAP-17/CAP-16 authority.
5. Historical material as current evidence:
   forbidden.
6. Historical material as proposal authorization:
   forbidden.
7. Historical source writes:
   forbidden; read-only only.
8. Historical truth status:
   evidence/not-current-truth.
9. Governed configuration:
   required; never hardcode `D:\Roby`.
10. Supported formats and archive semantics:
    unresolved pending real corpus characterization.

### Demonstrated residual

The demonstrated architectural residual is:

`GOVERNED_READ_ONLY_DEVELOPMENT_HISTORY_SOURCE`

The residual is real, but its source contract is not yet sufficiently specified for
RED because the actual corpus shape is unknown.

### RED decision

`RED_AUTHORIZED: NO`

Reason:

`REAL_D_ROBY_CORPUS_SHAPE_AND_SAFE_SOURCE_FORMAT_BOUNDARY_UNPROVEN`

Creating RED now would force the tests to invent file-format, archive, exclusion and
traversal semantics that are not supported by evidence.

### Required next evidence

The next evidence should be a metadata-only inventory of `D:\Roby`, not another full
project upload.

This protects the user's transfer quota and keeps the next reconciliation focused on
source shape rather than content.

### Next governed action

`MASTER PLAN — D:\Roby DEVELOPMENT HISTORY CORPUS & SOURCE MODEL —
RECONCILIATION`

Input required for that block:

`D:\Roby` metadata-only inventory.

STOP before CONTRACT RED.

### Closure

`D_ROBY_GOVERNED_DEVELOPMENT_HISTORY_SOURCE: NARROWED`

`CURRENT_PROJECT_EVIDENCE_AUTHORITY: EXISTING / UNCHANGED`

`SELF_DIAGNOSTIC_AUTHORITY: EXISTING / UNCHANGED`

`SELF_IMPROVEMENT_PROPOSAL_AUTHORITY: EXISTING / UNCHANGED`

`HISTORICAL_SOURCE_AUTHORITY: MISSING`

`HISTORICAL_SOURCE_ROLE: READ_ONLY_EVIDENCE / NOT_CURRENT_TRUTH`

`HISTORICAL_TO_PROJECT_EVIDENCE_DIRECT_HANDOFF: FORBIDDEN`

`HISTORICAL_TO_PROPOSAL_DIRECT_HANDOFF: FORBIDDEN`

`SELECTED_RESIDUAL: GOVERNED_READ_ONLY_DEVELOPMENT_HISTORY_SOURCE`

`RED_AUTHORIZED: NO`

`PRODUCT_CHANGE: NONE`

`TEST_CHANGE: NONE`

`B2: STOP`

`B3: STOP`

`B4: STOP`
