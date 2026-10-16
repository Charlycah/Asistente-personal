# ROBY XI.2 — D:\Roby Governed Development History Source

## Current-State Reconciliation

### Starting state

Owner-certified baseline: 13,401 PASS / 0 FAIL / Ruff clean.

This block is inventory/reconciliation only. It changes no product code and stops
before CONTRACT RED.

### Owner intent

`D:\Roby` may be consulted as read-only development history. ROBY may report a
historical finding, explain why it may matter, and suggest how it could be improved
under human review.

ROBY must not modify its history, code, architecture, governance or configuration as
a consequence of that consultation.

The intended semantic chain is:

`read historical material -> identify a possible improvement -> explain evidence and
rationale -> verify against current executable/project truth -> human-reviewable
proposal`

It is never:

`historical material -> autonomous change`

### Existing authorities that must be reused

#### Read-only filesystem-source pattern

`app.personal_document_source.PersonalDocumentRootDiscoveryAdapter` already proves a
bounded application-side pattern for an explicitly configured local root:

- recursive bounded discovery;
- deterministic source identity;
- relative-path provenance;
- symlink rejection;
- root-containment enforcement;
- revalidation before selected ingestion;
- no background scan;
- no automatic cognition.

This is a reusable source-governance pattern. It is not authorization to treat
`D:\Roby` as ordinary Personal Documents or to reuse the Personal Documents namespace
without a source/trust contract.

#### Document and Reasoning authorities

The canonical Document Inbox and `DocumentReadingService` already own document
lifecycle and text extraction. Explicitly selected document evidence can already be
normalized and admitted to the existing governed Reasoning gateway through
`PersonalDocumentReasoningAdmissionAdapterV1`.

No new reasoning brain or historical reasoning authority is required.

#### Self-diagnostics and improvement proposal authorities

The repository already contains the bounded chain:

`explicit technical observations -> threshold -> explicit hypothesis -> reproducible
proof -> hash-bound current project evidence -> DiagnosticProposal -> canonical
Governed Proposal inbox -> human review`

`SelfImprovementGovernedProposalReachability` explicitly reports:

- autonomous execution disabled;
- code mutation disabled.

The existing proposal generator verifies current files and tests against SHA-256
content digests before a proposal can be produced.

Therefore the requested ability to say "I found this historical issue; this may be
improvable; here is how and why" does not require a new self-improvement authority.

### Critical trust boundary

Historical development material is evidence about ROBY's development history. It is
not automatically evidence about ROBY's current executable state.

Permanent invariants:

`HISTORICAL_DEVELOPMENT_MATERIAL != CURRENT_EXECUTABLE_PROJECT_EVIDENCE`

`HISTORICAL_FINDING != CURRENT_DEFECT`

`HISTORICAL_SUGGESTION != CHANGE_AUTHORIZATION`

`HUMAN_APPROVAL != AUTONOMOUS_APPLICATION`

A historical document may identify where current verification should look. It may not
satisfy the existing reproduced-proof or hash-bound current-project-evidence gates by
itself.

### Current residual

No canonical productive source contract currently distinguishes `D:\Roby`
development-history material from ordinary personal documents while preserving its
specific historical/trust semantics.

The smallest demonstrated residual is therefore source-side and trust-side:

`explicit authorized development-history root -> bounded read-only discovery ->
development-history provenance/trust classification -> explicit human-selected
material -> existing document/evidence/reasoning authorities`

The residual stops before self-diagnostics and proposal generation. Those downstream
authorities already exist.

### Required source semantics

A future contract should preserve at least:

- configured root, never hardcoded `D:\Roby` in product code;
- read-only access;
- bounded deterministic discovery;
- root containment and external-symlink rejection;
- relative path and stable source identity/provenance;
- explicit `development-history` source semantics;
- historical/current trust distinction;
- explicit selection before ingestion/admission;
- no startup/background scanner;
- no automatic Memory or Learning write;
- no automatic self-diagnostic trigger;
- no automatic proposal;
- no code/history/configuration mutation.

### Improvement suggestion boundary

Once historical material has been explicitly selected and reasoned over, ROBY may
produce an advisory observation such as:

- what historical decision or implementation it found;
- whether current evidence confirms, supersedes or contradicts it;
- what might be improved;
- why the improvement may be useful;
- which current authorities/files/tests would be relevant;
- expected risks and validation requirements.

Promotion into the existing governed self-improvement proposal path requires fresh
current evidence and all existing proof gates. The historical source does not bypass
those gates.

### Duplicate-risk exclusions

Do not create:

- `DevelopmentHistoryManager` as a cognitive authority;
- `SelfHistoryBrain`;
- `SelfImprovementManager`;
- another Reasoning authority;
- another Proposal inbox;
- autonomous patcher/editor;
- background history watcher;
- historical Memory/Learning writer.

### Reconciliation result

`D_ROBY_HISTORY_SOURCE: MISSING_CANONICAL_SOURCE_TRUST_SEAM`

`DOWNSTREAM_REASONING: EXISTING / REUSE`

`SELF_DIAGNOSTICS: EXISTING / REUSE`

`IMPROVEMENT_PROPOSAL_GENERATION: EXISTING / REUSE`

`HUMAN_REVIEW: EXISTING / REQUIRED`

`AUTONOMOUS_EXECUTION: FORBIDDEN`

`CODE_OR_HISTORY_MUTATION: FORBIDDEN`

`DEMONSTRATED_RESIDUAL: AUTHORIZED_READ_ONLY_DEVELOPMENT_HISTORY_SOURCE_AND_TRUST_PROJECTION`

`PRE_RED_READINESS: YES`

`CONTRACT_RED_AUTHORIZATION: NO — STOP FOR OWNER CERTIFICATION OF THIS RECONCILIATION`

### Recommended next block after Owner certification

`D:\Roby GOVERNED DEVELOPMENT HISTORY SOURCE — PRE-RED RECONCILIATION`

That block must specify the exact reuse/composition contract and tests before any
productive implementation is touched.
