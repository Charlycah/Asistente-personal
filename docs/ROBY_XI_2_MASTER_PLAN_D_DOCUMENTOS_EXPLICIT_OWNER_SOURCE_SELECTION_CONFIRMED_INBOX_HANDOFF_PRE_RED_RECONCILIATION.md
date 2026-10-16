# ROBY XI.2 MASTER PLAN

## D:\Documentos Explicit Owner Source Selection & Confirmed Inbox Handoff

### PRE-RED Reconciliation

## 1. Status

This document records the governed PRE-RED reconciliation for the single
candidate promoted by the post-D:\Roby global productive horizon reselection.

Baseline executable truth:

- pytest: 13,387 PASS / 0 FAIL;
- Ruff: clean;
- D:\Roby governed source: CLOSED / OWNER-CERTIFIED;
- D:\Roby explicit Owner consultation: CLOSED / OWNER-CERTIFIED;
- D:\Documentos governed source foundation: CLOSED / OWNER-CERTIFIED;
- product change in this reconciliation: NONE;
- test change in this reconciliation: NONE.

This is not a GREEN implementation document.

This is not a CONTRACT RED implementation.

The purpose is to determine whether one exact contract can be written without
creating a second document authority, bypassing the Inbox, or implicitly
admitting a document into Reasoning.

## 2. Governing rules

The following rules remain controlling:

`INVENTORY BEFORE SURGERY -> REUSE PROOF -> RESIDUAL -> CONTRACT -> RED -> GREEN`

`ONE BRAIN / ONE AUTHORITY PER CAPABILITY`

`CURRENT EXECUTABLE TRUTH + LATEST OWNER GATE > STALE HISTORICAL STATUS LABEL`

`HORIZON != SURGICAL CANDIDATE`

`PARTIAL != DEMONSTRATED RESIDUAL`

`FUTURE != NEXT`

No new manager, Inbox, repository, document entity, Reasoning gateway,
capability registry, or execution loop is authorized by this reconciliation.

## 3. Promoted candidate

The global reselection promoted exactly one candidate:

`EXPLICIT_OWNER_PERSONAL_DOCUMENT_SOURCE_SELECTION_AND_CONFIRMED_INBOX_HANDOFF`

The candidate is narrower than generic document runtime reachability.

It does not authorize:

- autonomous document discovery;
- startup scanning;
- background indexing;
- content-wide semantic indexing;
- automatic ingestion;
- automatic Reasoning;
- automatic Knowledge admission;
- automatic Memory admission;
- automatic Learning admission;
- self-improvement use;
- filesystem writes to D:\Documentos.

## 4. Existing source authority

The existing source authority is:

`app.personal_document_source.PersonalDocumentRootDiscoveryAdapter`

It already owns:

- authorized-root discovery;
- deterministic candidate identity;
- supported-suffix filtering;
- symlink rejection;
- root containment;
- bounded candidate discovery;
- transient last-discovery state;
- selected-source revalidation;
- bounded extraction through the existing document reader;
- handoff to the existing Document Inbox.

This authority must not be duplicated.

The future conversational port must be subordinate to it.

## 5. Existing durable Inbox authority

The canonical durable authority remains:

`core.document_inbox.DocumentInboxManager`

Its `ingest_text()` path:

- validates non-empty content;
- enforces scope;
- computes the content hash;
- deduplicates through the repository;
- builds the canonical `DocumentRecord`;
- saves through the configured repository;
- records Inbox signals.

The future runtime must not create another repository or another document
record type.

## 6. Existing source-to-Inbox handoff

`PersonalDocumentRootDiscoveryAdapter.ingest_selected(candidate_id)` already
performs the canonical source-to-Inbox handoff.

It:

1. requires a candidate from the last bounded discovery;
2. resolves the relative source beneath the authorized root;
3. rejects symlinks and root escape;
4. recomputes candidate metadata;
5. rejects a changed source;
6. reads through `DocumentReadingService`;
7. calls the existing `DocumentInboxManager.ingest_text()`;
8. returns the resulting canonical `DocumentRecord`.

Therefore the residual is not a missing ingestion implementation.

The residual is governed conversational authorization of that existing call.

## 7. Existing downstream Reasoning authority

The existing downstream adapter is:

`PersonalDocumentReasoningAdmissionAdapterV1`

Its contract requires explicit `document_id` values already present in the
Inbox.

It is a separate authority boundary.

The new source-selection capability must not call it.

The required invariant is:

`SOURCE_SELECTION != REASONING_ADMISSION`

and:

`INBOX_HANDOFF != REASONING_ADMISSION`

The future capability must STOP after the Inbox handoff is presented.

## 8. Reuse proof from D:\Roby

The recently certified D:\Roby consultation provides a valid reuse proof for
interaction mechanics only.

Reusable interaction mechanics are:

- explicit Owner intent;
- registration in `OfficialRuntimeCapabilityRegistry`;
- subordinate conversation interception port;
- metadata-only initial matching;
- safe relative-path presentation;
- session-scoped pending state;
- bounded TTL;
- ordinal selection;
- exact presented-relative-path selection;
- candidate IDs hidden from the Owner-facing surface;
- cancellation;
- no autonomous initiation.

The D:\Roby authority itself is not reusable.

The D:\Roby READ_ONLY descriptor is not reusable.

Historical read semantics are not reusable.

## 9. Critical semantic difference from D:\Roby

D:\Roby selection culminates in a read-only observation.

D:\Documentos selection can culminate in durable Inbox persistence.

Therefore:

`HISTORY_SELECTION -> READ_ONLY`

but:

`PERSONAL_DOCUMENT_CONFIRMATION -> DURABLE_INBOX_HANDOFF`

This distinction is mandatory.

The future capability must not be declared READ_ONLY merely because discovery
and presentation are read-only steps.

## 10. Capability effect classification

The existing capability vocabulary already provides:

- `PermissionScope.WRITE`;
- `CapabilityEffectClass.STATE_CHANGING`;
- `CapabilityInteractionScope.HUMAN`;
- `CapabilityInitiationPolicy.HUMAN_APPROVAL`.

No new effect taxonomy is required.

Because confirmed ingestion can save a `DocumentRecord`, the capability must
be represented as state-changing at the descriptor boundary.

PRE-RED decision:

`permission_scope = WRITE`

`effect_class = STATE_CHANGING`

`interaction_scope = HUMAN`

`initiation_policy = HUMAN_APPROVAL`

`requires_confirmation = True`

Risk must not be silently inherited from D:\Roby.

The smallest coherent existing classification is MEDIUM because the operation
changes durable local application state but does not mutate the source file,
access a device, access the network, or authorize an external-world action.

PRE-RED decision:

`risk = MEDIUM`

## 11. Conceptual capability name

The capability name is fixed for the future contract as:

`personal_documents.ingest_selected`

The name reflects the state-changing boundary rather than merely discovery.

No second discovery capability is required.

## 12. Intended runtime composition

The intended productive chain is:

`explicit Owner intent`

`-> Official Conversation Gateway`

`-> OfficialRuntimeCapabilityRegistry`

`-> subordinate Personal Documents interception port`

`-> PersonalDocumentRootDiscoveryAdapter`

`-> safe candidate presentation`

`-> explicit candidate selection`

`-> explicit ingestion confirmation`

`-> PersonalDocumentRootDiscoveryAdapter.ingest_selected()`

`-> existing DocumentInboxManager`

`-> safe DocumentRecord presentation`

`-> STOP`

No Reasoning call belongs in this chain.

## 13. Productive runtime composition requirement

This horizon is specifically about productive reachability.

A future contract must not prove only that an isolated builder can register the
capability.

The official runtime root already constructs one canonical
`DocumentInboxManager` before it constructs the official capability registry.

Therefore the future GREEN must reuse that same Inbox instance.

The future contract must include a root-composition reachability assertion or
an equivalent architectural proof that the official runtime root invokes the
new builder with:

- the existing `OfficialRuntimeCapabilityRegistry`;
- the existing canonical `DocumentInboxManager`;
- the document reading dependency required by the source builder.

A second Inbox instance is forbidden.

## 14. Reader dependency

`DocumentReadingService` is an existing stateless extraction service.

It is already instantiated by other governed document/library surfaces.

The future builder should accept an injected reader for tests and composition.

The builder may use the existing source builder:

`build_personal_document_source_from_environment(...)`

No new extractor is authorized.

No duplicate format parser is authorized.

## 15. Explicit intent boundary

The capability must require an unequivocal Personal Documents source intent.

Safe conceptual intent examples include phrases equivalent to:

- "consultá mis documentos personales";
- "buscá en D:\Documentos";
- "importá desde mis documentos personales";
- "ingresá desde D:\Documentos".

Generic terms are insufficient by themselves:

- "documento";
- "archivo";
- "PDF";
- "mis archivos";
- "leer documento".

Those phrases may belong to existing document reading or attachment flows.

The new capability must not steal them.

## 16. Discovery is non-mutating

An initial explicit source query may call only `discover()`.

Discovery may match only safe candidate metadata.

The initial query must never call `ingest_selected()`.

Required invariant:

`DISCOVERY != INGESTION_AUTHORIZATION`

## 17. Metadata-only matching

The future port may match a user query against:

- `relative_path`;
- filename as represented by `relative_path`;
- suffix metadata when useful for presentation.

It must not read candidate content merely to decide whether a candidate should
be shown.

Required invariant:

`DISCOVERY_SEARCH != CONTENT_SEARCH`

## 18. Safe presentation

Candidate presentation may expose:

- ordinal;
- relative path;
- suffix/type;
- size.

It must not expose:

- absolute configured root;
- internal `source_reference`;
- full candidate ID;
- extracted document content during discovery.

## 19. Selection is not confirmation

This is the central PRE-RED decision.

Selecting a candidate must not ingest it.

Selection only establishes the exact pending candidate for the same session.

After selection, the runtime must ask for explicit confirmation of the durable
Inbox handoff.

Required invariant:

`CANDIDATE_SELECTION != DURABLE_INGESTION_AUTHORIZATION`

## 20. Two-stage pending state

The future port requires two bounded pending stages:

1. `awaiting_selection`;
2. `awaiting_ingestion_confirmation`.

Both stages are ephemeral.

Neither stage is persisted.

Neither stage is Memory.

Neither stage is Knowledge.

Neither stage is Learning.

## 21. Session isolation

Pending state must be keyed by `session_id`.

A selection in another session must not select a candidate.

A confirmation in another session must not authorize ingestion.

Required invariant:

`SESSION_A_CONFIRMATION != SESSION_B_AUTHORIZATION`

## 22. TTL

The bounded pending TTL is fixed at five minutes, matching the recently proven
interaction pattern unless the future contract reveals an existing stronger
canonical TTL.

Expiration must clear authorization state.

After expiration, a bare ordinal or confirmation phrase must not ingest.

## 23. Cancellation

Cancellation must work in both pending stages.

Cancellation must clear the session pending state.

After cancellation, a bare selection or confirmation must not ingest.

## 24. Selection forms

Selection may accept only:

- a visible ordinal from the last presented candidate set;
- the exact relative path from the last presented candidate set.

An arbitrary candidate ID must not be accepted as Owner-facing authorization.

A relative path not presented in that session must not be accepted.

## 25. Confirmation semantics

Confirmation must be explicit and bounded to the selected candidate.

A generic conversational "sí" may be accepted only while the same session is
in `awaiting_ingestion_confirmation` and the prompt immediately identifies the
selected relative path and the durable Inbox effect.

Outside that state, "sí" has no meaning for this capability.

Explicit forms such as "confirmo", "sí, ingresalo" or equivalent may be
accepted only in the active confirmation state.

The port must not infer confirmation from silence, topic continuation, or a
new unrelated request.

## 26. Confirmation prompt

The confirmation prompt must state the effect accurately.

Conceptually:

"Seleccionaste <relative_path>. ¿Confirmás ingresarlo al Document Inbox?"

The prompt must not claim that the document has already been ingested.

It must not imply automatic Reasoning.

## 27. Exactly one handoff attempt

On valid confirmation, the port may call:

`source.ingest_selected(selected.candidate_id)`

exactly once for that pending confirmation.

The pending confirmation must be consumed before or atomically with the
attempt so a repeated confirmation cannot become an accidental second action.

The Inbox itself retains its canonical content-hash deduplication semantics.

The port must not implement a second deduplication authority.

## 28. Source revalidation remains canonical

The future port must not reimplement filesystem validation.

`ingest_selected()` already revalidates:

- selection provenance;
- path containment;
- symlink policy;
- file existence;
- supported suffix;
- candidate identity.

A changed source must fail closed through the existing authority.

## 29. Safe post-ingestion presentation

After successful ingestion, the response may present safe record metadata such
as:

- document title;
- canonical `document_id`;
- normalized category/status when useful.

It must not automatically present the entire document content.

The `document_id` may be exposed because it is the canonical explicit handle
required by the existing downstream Reasoning admission adapter.

Exposing it does not itself admit the record into Reasoning.

## 30. STOP after Inbox handoff

The future capability must STOP after presenting the ingestion result.

It must not call:

- `PersonalDocumentReasoningAdmissionAdapterV1.admit_and_reason()`;
- the governed Reasoning gateway;
- Knowledge runtime;
- Memory runtime;
- Learning;
- proposal generation;
- self-improvement;
- code mutation.

The Owner may make a later explicit request that uses an existing downstream
capability.

That later request is a separate authority decision.

## 31. Failure behavior

The runtime must fail closed when:

- `ROBY_PERSONAL_DOCUMENTS_ROOT` is absent;
- the configured root is invalid;
- the source changes after presentation;
- extraction fails;
- Inbox ingestion rejects the document;
- pending state expires;
- selection is not from the presented set;
- confirmation is absent or invalid.

No fallback filesystem scan is authorized.

No broader root is authorized.

## 32. Builder semantics

The future builder must reuse:

`build_personal_document_source_from_environment(...)`

It must receive the existing canonical Inbox and reader dependencies.

If the Personal Documents root is not configured, the builder must return a
non-provisioned result or `None` and must not register the capability.

If configuration is invalid, it must fail closed without registering a broken
capability.

## 33. Registry semantics

The capability must register in the existing
`OfficialRuntimeCapabilityRegistry`.

No parallel registry is authorized.

No direct bypass of `OfficialCapabilityGateway` is authorized.

Semantic triggers must be narrow enough not to capture existing generic
DocumentReadingService requests.

## 34. Descriptor decision

The future descriptor is fixed conceptually as:

- name: `personal_documents.ingest_selected`;
- kind: FILES;
- risk: MEDIUM;
- permission scope: WRITE;
- initiation policy: HUMAN_APPROVAL;
- effect class: STATE_CHANGING;
- interaction scope: HUMAN;
- requires confirmation: True.

The descriptor describes the maximum effect reachable through the capability,
not merely its first discovery step.

## 35. No autonomous initiation

The capability must not be available to governed autonomous initiation merely
because the root is configured.

Configured availability is not authorization.

Required invariant:

`CONFIGURED_ROOT != OWNER_INTENT`

and:

`OWNER_INTENT != INGESTION_CONFIRMATION`

## 36. No startup scan

Runtime construction must not call `discover()` merely because the root exists.

Discovery occurs only after explicit Owner intent.

This preserves bounded I/O and avoids hidden traversal of D:\Documentos.

## 37. No source mutation

The source root remains read-only from this capability's perspective.

The state-changing effect is limited to ROBY's existing Document Inbox.

The capability must not:

- rename source files;
- move source files;
- delete source files;
- rewrite source files;
- create sidecars beneath D:\Documentos.

## 38. Relationship to existing attachment ingestion

Existing attachment/document ingestion flows remain authoritative for their
own surfaces.

This capability is only for governed discovery and explicit handoff from the
configured Personal Documents root.

It must not replace generic attachment handling.

It must not capture generic "read this document" requests.

## 39. Relationship to D:\Biblioteca

D:\Biblioteca remains a separate governed local-library authority.

Personal Documents must not import or reuse the library catalogue authority.

Only generic architectural lessons such as containment and explicit selection
remain reusable.

## 40. Relationship to D:\Roby

D:\Roby remains historical and read-only.

Its consultation port is a reuse proof for interaction mechanics only.

No historical trust semantics transfer to Personal Documents.

## 41. Relationship to self-improvement

A Personal Document Inbox record is not automatically diagnostic project
evidence.

Nothing in this capability may construct `DiagnosticProjectEvidence`.

Nothing may generate a diagnostic proposal.

## 42. Future CONTRACT RED scope

A future CONTRACT RED is now authorized to specify tests for exactly this
residual.

The contract should prove at minimum:

1. port, descriptor, and builder exist;
2. descriptor is WRITE / STATE_CHANGING / HUMAN / HUMAN_APPROVAL;
3. descriptor requires confirmation and uses MEDIUM risk;
4. only explicit Personal Documents source intent is admitted;
5. discovery matches metadata without reading content;
6. safe presentation exposes only relative metadata;
7. initial discovery never ingests;
8. selection is session-scoped and never ingests;
9. selection accepts only presented ordinal or relative path;
10. confirmation is a separate active state;
11. confirmation in another session cannot ingest;
12. cancellation clears selection and confirmation state;
13. TTL expiration clears selection and confirmation state;
14. valid confirmation calls the existing `ingest_selected()` once;
15. changed source fails closed through existing revalidation;
16. successful result exposes safe DocumentRecord metadata and STOPs;
17. no Reasoning/Knowledge/Memory/Learning/self-improvement handoff occurs;
18. builder registers only when dependencies and root are valid;
19. official runtime root reuses its existing DocumentInboxManager;
20. official runtime root makes the capability productively reachable.

The exact test count is not fixed by PRE-RED.

The CONTRACT RED should choose the smallest test set that proves these clauses
without redundant assertions.

## 43. Expected future product surface

The smallest likely productive addition is one subordinate runtime wiring
module conceptually responsible for:

- the interception port;
- ephemeral pending interaction state;
- descriptor construction;
- environment builder registration.

A minimal official runtime-root wiring change may also be required because
productive reachability is part of the residual.

No other productive module is currently justified.

## 44. Forbidden future GREEN expansion

Even if a CONTRACT RED is later certified, GREEN must not opportunistically
add:

- automatic Reasoning;
- semantic indexing;
- background watchers;
- queues;
- bulk ingestion;
- recursive unbounded scans;
- Inbox replacement;
- document repository replacement;
- new document entity types;
- new Knowledge authority;
- new Memory authority;
- new Learning authority.

## 45. Authority inventory conclusion

Existing authorities are sufficient:

- source discovery/validation: EXISTING;
- document extraction: EXISTING;
- durable Inbox: EXISTING;
- canonical DocumentRecord: EXISTING;
- capability registry: EXISTING;
- official conversation interception: EXISTING;
- downstream explicit Reasoning admission: EXISTING / OUT OF SCOPE.

Missing capability:

- explicit Owner conversational authorization from Personal Documents source
  selection to confirmed existing Inbox handoff.

This is a reachability/authorization residual, not a missing document system.

## 46. PRE-RED verdict

`PRE_RED_RECONCILIATION: COMPLETE`

`RESIDUAL:`

`EXPLICIT_OWNER_PERSONAL_DOCUMENT_SOURCE_SELECTION_AND_CONFIRMED_INBOX_HANDOFF`

`SOURCE_AUTHORITY: EXISTING / UNCHANGED`

`INBOX_AUTHORITY: EXISTING / UNCHANGED`

`DOCUMENT_RECORD_AUTHORITY: EXISTING / UNCHANGED`

`RUNTIME_CAPABILITY_REGISTRY: EXISTING / SELECTED`

`REASONING_ADMISSION_AUTHORITY: EXISTING / OUT_OF_SCOPE`

`NEW_COGNITIVE_AUTHORITY: NONE`

`NEW_PERSISTENCE_AUTHORITY: NONE`

`DESCRIPTOR_PERMISSION: WRITE`

`DESCRIPTOR_EFFECT: STATE_CHANGING`

`DESCRIPTOR_INTERACTION: HUMAN`

`DESCRIPTOR_INITIATION: HUMAN_APPROVAL`

`DESCRIPTOR_CONFIRMATION: REQUIRED`

`DESCRIPTOR_RISK: MEDIUM`

`SELECTION_REQUIRES_WRITE: NO`

`CONFIRMATION_REQUIRED_BEFORE_WRITE: YES`

`AUTO_REASONING_AFTER_INGESTION: FORBIDDEN`

`PRODUCT_CHANGE: NONE`

`TEST_CHANGE: NONE`

`CONTRACT_RED_AUTHORIZED: YES`

`B2/B3/B4: STOP`

## 47. Next governed step

The next permitted block is:

`MASTER PLAN — D:\Documentos EXPLICIT OWNER SOURCE SELECTION`

`& CONFIRMED INBOX HANDOFF — CONTRACT RED`

That block must add contract tests and documentation only.

It must not implement the runtime module.

It must stop after demonstrating the exact expected RED against the currently
absent productive capability.
