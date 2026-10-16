# ROBY XI.2 — Open Visual Subject Eligible Governed Source Reachability
## PRE-RED RECONCILIATION

## 1. Certified starting point

Input baseline:

`OPEN VISUAL SUBJECT GOVERNED REQUEST REPRESENTATION — POST-GREEN MASTER PLAN
RECONCILIATION`

Owner certification:

- 13,523 PASS;
- 0 FAIL;
- Ruff clean;
- M361 regenerated and reproducible.

The representation seam is closed. This reconciliation does not reopen it.

## 2. Residual under audit

`OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY`

The current system can represent an explicit open visual subject through:

- `GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT`;
- empty `topics` only in that explicit mode;
- a required non-empty `query_text`.

The canonical selector intentionally makes every current source ineligible for
that mode. Therefore representation exists while source reachability does not.

## 3. Existing canonical authorities

The audit confirms these existing owners and integration surfaces:

- `GovernedInformationSources` — canonical source declaration registry;
- `GovernedConversationalSourceSelector` — canonical source selector;
- `GovernedSourceQueryContract` — canonical query validation contract;
- `GovernedSourceQueryExecutor` — single governed execution authority;
- `OfficialConversationGateway` — owner of the productive conversation path;
- source-specific adapters — bounded execution implementations only.

No new registry, selector, executor, router, or conversation authority is
justified.

## 4. Source declaration evidence

`GovernedInformationSource` currently declares:

- source identity and name;
- source kind and status;
- governed topic coverage;
- network and automatic-fetch safety flags;
- authority, provenance, evidence, coverage, regions, and confidence.

It does not currently declare a capability dimension authorizing an open
visual-subject query.

The absence is semantic source metadata, not an execution-authority gap.

## 5. Why adapter behavior is not source authorization

The NASA adapter can technically consume `query_text` and has a bounded
`media_type` parameter. That technical behavior does not authorize NASA for
arbitrary open visual subjects.

NASA's governed source declaration remains bounded to its declared space and
NASA topics.

Therefore:

`ADAPTER_TECHNICAL_ABILITY != GOVERNED_SOURCE_ELIGIBILITY`

and:

`QUERY_TEXT_SUPPORT != OPEN_VISUAL_SUBJECT_AUTHORIZATION`

NASA must not become eligible for `pistas de Nazca` merely because its adapter
can send arbitrary text to an upstream endpoint.

## 6. Existing selector boundary

The selector currently rejects every `OPEN_VISUAL_SUBJECT` request before the
legacy topic-subset test.

That safeguard is correct for the current baseline because no source has an
explicit open-visual capability declaration.

The future seam must not delete the safeguard and fall through to:

`empty_topics.issubset(source.topics)`.

Instead, open-visual eligibility must require an affirmative source declaration.

## 7. Existing query-contract boundary

`GovernedSourceQueryContract.prepare()` currently validates source status,
topic coverage, and region coverage.

For defense in depth, future open-visual queries must also be rejected here
unless the resolved source explicitly declares the matching capability.

Selector eligibility alone is not sufficient authorization for direct query
preparation or executor entry.

## 8. Existing executor and admission route

`GovernedSourceQueryExecutor` already owns adapter registration.

Its existing `source_declaration` path can admit an explicit non-default
`GovernedInformationSource` into the contract-owned registry before execution.

This demonstrates that a future source does not require a second registry or
executor merely because it is not a default source.

It does not demonstrate that such a source already exists.

## 9. Refined semantic seam

The minimum demonstrated semantic deepening is an explicit source capability
that can authorize the request mode independently from topic coverage.

Conceptually:

`OPEN_VISUAL_SUBJECT_QUERY`

The exact productive type/name remains a contract-design decision and is not
authorized by this PRE-RED reconciliation.

The capability must be declarative metadata owned by the existing governed
source declaration. It must not be inferred from:

- empty topics;
- adapter method signatures;
- network availability;
- source kind;
- `media_type` parameters;
- `query_text` support;
- a source being registered in the executor.

## 10. Two distinct requirements remain

This residual contains two coupled but distinct obligations:

1. `OPEN_VISUAL_SOURCE_CAPABILITY_DECLARATION`
   - existing source metadata can explicitly declare bounded eligibility;
   - selector and query contract can validate that declaration.

2. `OPEN_VISUAL_SUBJECT_CAPABLE_SOURCE_AVAILABILITY`
   - at least one governed source must actually declare that capability and
     have a compatible registered adapter before an open subject can be
     selected and executed.

The first obligation can be designed without pretending the second already
exists.

## 11. No demonstrated current general source

The audited current adapters are source-specific and semantically bounded.

No existing current declaration demonstrates authority to serve arbitrary
external visual subjects such as `pistas de Nazca`.

Therefore:

`CURRENT_GENERAL_OPEN_VISUAL_SOURCE: NOT_DEMONSTRATED`

A future source candidate must be separately justified against its real API,
provenance, media behavior, safety, registration, and governed declaration.

This PRE-RED does not select or add that provider.

## 12. Classification

The source-capability declaration itself is best classified as:

`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

because it deepens the existing governed source declaration, selector, and
query contract without creating a new authority.

Actual availability of a new provider/source, if later demonstrated necessary,
is a separate integration decision and must not be smuggled into this
classification.

## 13. Contract-design gate

Evidence is sufficient to authorize a bounded contract-design reconciliation
for the capability-declaration seam.

It is not yet sufficient to authorize CONTRACT RED because the exact source
capability representation and its interaction with legacy topic-constrained
sources must first be fixed contractually.

It is not sufficient to authorize a productive source/provider.

## 14. Required next contract-design questions

The next reconciliation must fix, without implementation:

1. the minimum explicit source-capability representation;
2. the default for all legacy sources;
3. selector eligibility for `OPEN_VISUAL_SUBJECT`;
4. query-contract defense-in-depth validation;
5. compatibility with topic-constrained selection;
6. whether capability declarations are a set or another bounded value;
7. how non-default source declarations carry the capability;
8. typed `UNAVAILABLE` behavior when no capable registered source exists;
9. the boundary between capability declaration and actual provider addition;
10. exclusions for freshness, ranking, and presentation.

## 15. Work ordering

The governed ordering is now:

1. representation seam — CLOSED / OWNER-CERTIFIED;
2. source capability declaration — CONTRACT DESIGN NEXT;
3. capable source availability/integration — LATER, only if justified;
4. `EXTERNAL_IMAGE_FRESHNESS_ORDERING` — LATER.

No provider selection is authorized by this ordering.

## 16. Integrity

This PRE-RED reconciliation changes documentation only.

Productive Python delta: zero.

Test Python delta: zero.

No historical guard or hash is rewritten.

No new authority is introduced.

## 17. Status

`PRE_RED_RECONCILIATION: COMPLETE`

`REPRESENTATION_SEAM: CLOSED / NOT_REOPENED`

`EXACT_RESIDUAL: OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY`

`FIRST_REFINED_SEAM: OPEN_VISUAL_SOURCE_CAPABILITY_DECLARATION`

`SECOND_REFINED_SEAM: OPEN_VISUAL_SUBJECT_CAPABLE_SOURCE_AVAILABILITY`

`CURRENT_GENERAL_OPEN_VISUAL_SOURCE: NOT_DEMONSTRATED`

`NASA_AS_GENERAL_IMAGE_SOURCE: REJECTED`

`ADAPTER_TECHNICAL_ABILITY_AS_AUTHORIZATION: REJECTED`

`EMPTY_TOPICS_AS_ELIGIBILITY: FORBIDDEN`

`EXISTING_SOURCE_REGISTRY: REUSED`

`EXISTING_SELECTOR: REUSED`

`EXISTING_QUERY_CONTRACT: REUSED`

`EXISTING_EXECUTOR: REUSED`

`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`

`CONTRACT_DESIGN_AUTHORIZATION: YES / CAPABILITY DECLARATION SEAM ONLY`

`CONTRACT_RED_AUTHORIZATION: NO`

`PRODUCTIVE_GREEN_AUTHORIZATION: NO`

`PROVIDER_ADDITION_AUTHORIZATION: NO`

`FRESHNESS: EXCLUDED`

`PRESENTATION: EXCLUDED`

`PRODUCTIVE_PYTHON_DELTA: ZERO`

`TEST_PYTHON_DELTA: ZERO`

`NEW_AUTHORITY: NONE`
