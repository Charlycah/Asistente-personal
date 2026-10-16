# ROBY XI.2 — Open Visual Subject Capable Source Availability
## PRE-RED Reconciliation

### Certified input
Baseline: `OPEN_VISUAL_SOURCE_CAPABILITY_DECLARATION_POST_GREEN_MASTER_PLAN_RECONCILIATION`.
Owner certification: 13,531 PASS / 0 FAIL, Ruff clean, M361 regenerated.

The capability-declaration seam is closed and is not reopened.

### Question under audit
Does the current productive system already contain a governed source and registered
adapter that may legitimately serve `OPEN_VISUAL_SUBJECT` requests for arbitrary
subjects?

### Productive evidence
The canonical source capability vocabulary contains
`InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY`.
The existing canonical selector and `GovernedSourceQueryContract` require that
explicit capability for open-visual requests.

No current `GovernedInformationSource` declaration assigns that capability.
Therefore no current productive source is governedly eligible for general
open-visual subject queries.

This is deliberate. Empty topics, arbitrary `query_text`, `media_type`, network
access, source kind, or an adapter's technical ability do not imply authorization.

### Existing adapters
NASA can technically transport arbitrary `query_text` to NASA Images and defaults
its media type to image, but its governed declaration remains topic-bounded and
does not declare `OPEN_VISUAL_SUBJECT_QUERY`. It is not a general image source.

Apple audiovisual, Cultura CABA, Argentina healthy eating, and Foursquare are
domain-specific integrations. Their ability to accept query text does not make
them general visual sources.

Foursquare provides an important architectural precedent: an adapter may carry a
`source_declaration`, and the existing `GovernedSourceQueryExecutor.register()`
path admits that non-default declaration through the existing governed contract.
This proves that a future provider does not require a second registry or executor.

### Exact residual
`OPEN_VISUAL_SUBJECT_CAPABLE_SOURCE_AVAILABILITY` remains demonstrated.

Its missing condition is not capability vocabulary or selector enforcement.
Those are already GREEN. The missing condition is:

`GOVERNED_GENERAL_OPEN_VISUAL_PROVIDER_INTEGRATION`

A real provider must be demonstrated whose API, provenance, media behavior,
credentials/availability policy, declaration, adapter, and registration are
compatible with the existing governed source architecture.

### Classification
This PRE-RED does not authorize a provider.

A future provider integration, if required after provider research/reconciliation,
must reuse:
- `GovernedInformationSources`;
- `GovernedSourceQueryContract`;
- `GovernedSourceQueryExecutor`;
- `GovernedConversationalSourceSelector`;
- `OfficialConversationGateway`;
- the existing non-default `source_declaration` admission path.

No new source registry, selector, executor, router, gateway authority, visual
presentation authority, or independent execution loop is justified.

### Provider-selection gate
Before CONTRACT RED, the next step must identify and justify a concrete provider
against at least:
1. general/open image search semantics rather than a bounded domain;
2. usable result URLs/preview metadata compatible with existing presentation;
3. provenance/source identity sufficient for governed information items;
4. credential and network behavior compatible with governed runtime policy;
5. explicit `OPEN_VISUAL_SUBJECT_QUERY` declaration;
6. existing executor registration/admission compatibility;
7. bounded failure behavior and typed unavailability;
8. no requirement to weaken topic-constrained sources or generalize NASA.

Provider identity is not selected by this reconciliation.

### Exclusions
- NASA generalization: forbidden.
- Empty topics as wildcard eligibility: forbidden.
- Adapter technical ability as authorization: forbidden.
- Freshness ordering: excluded / later.
- Presentation changes: excluded.
- Natural-language admission: closed / not reopened.
- Capability declaration: closed / not reopened.

### Authorization state
`OPEN_VISUAL_SUBJECT_CAPABLE_SOURCE_AVAILABILITY_PRE_RED_RECONCILIATION: COMPLETE`
`CURRENT_CAPABLE_PRODUCTIVE_SOURCE: NONE DEMONSTRATED`
`EXACT_RESIDUAL: GOVERNED_GENERAL_OPEN_VISUAL_PROVIDER_INTEGRATION`
`PROVIDER_SELECTION: NOT YET MADE`
`PROVIDER_ADDITION_AUTHORIZATION: NO`
`CONTRACT_RED_AUTHORIZATION: NO`
`PRODUCTIVE_GREEN_AUTHORIZATION: NO`
`NEW_AUTHORITY: NONE`

Next governed step:
`GOVERNED GENERAL OPEN VISUAL PROVIDER — PROVIDER/INTEGRATION RECONCILIATION`
Freshness remains later.


## Provider / integration reconciliation outcome
Preferred provider candidate: WIKIMEDIA_COMMONS.
Prerequisite seam: OPEN_VISUAL_CAPABLE_SOURCE_DECLARATION_WITHOUT_FAKE_TOPIC.
CONTRACT RED: not authorized; provider GREEN: not authorized.
