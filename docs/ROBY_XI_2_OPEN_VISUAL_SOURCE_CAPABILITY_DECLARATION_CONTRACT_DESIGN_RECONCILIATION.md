# ROBY XI.2 — Open Visual Source Capability Declaration
## CONTRACT DESIGN RECONCILIATION

## 1. Certified starting point

Input baseline:

`OPEN VISUAL SUBJECT ELIGIBLE GOVERNED SOURCE REACHABILITY — PRE-RED RECONCILIATION`

Owner certification:

- 13,523 PASS;
- 0 FAIL;
- Ruff clean;
- M361 regenerated and reproducible.

The request-representation seam remains closed and is not reopened.

## 2. Seam under design

`OPEN_VISUAL_SOURCE_CAPABILITY_DECLARATION`

This seam answers only how an existing governed source declaration explicitly
authorizes an `OPEN_VISUAL_SUBJECT` query and how existing authorities validate
that authorization.

It does not add or select a provider.

## 3. Existing authority remains canonical

The design preserves:

- `GovernedInformationSource` / `GovernedInformationSources` as source metadata
  and declaration authority;
- `GovernedConversationalSourceSelector` as source-selection authority;
- `GovernedSourceQueryContract` as query-validation authority;
- `GovernedSourceQueryExecutor` as execution authority;
- `OfficialConversationGateway` as productive conversation owner.

No visual-specific registry, selector, executor, router, or source manager is
permitted.

## 4. Minimum capability representation

The source declaration needs an explicit semantic capability vocabulary.

Contractually, the minimum representation is:

`InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY`

and each `GovernedInformationSource` carries:

`capabilities: frozenset[InformationSourceCapability]`

The exact field is declarative metadata. It grants eligibility only for the
semantic request mode it names; it does not itself enable network access,
register an adapter, or execute a query.

A set is preferred over a single flag/value because source capabilities are an
extensible metadata dimension while preserving one source declaration
authority. This does not create a capability manager or secondary registry.

## 5. Safe legacy default

For every existing source declaration, including NASA, the default is:

`capabilities = frozenset()`

Therefore no historical source becomes open-visual capable merely because the
new field exists.

Existing constructors that do not provide capabilities remain semantically
unchanged.

NASA must not receive `OPEN_VISUAL_SUBJECT_QUERY` in this seam.

## 6. Topic-constrained compatibility

For `GovernedConversationalRequestMode.TOPIC_CONSTRAINED`:

- non-empty topics remain required;
- selector topic-subset eligibility remains authoritative;
- query-contract topic-subset validation remains authoritative;
- capability metadata does not replace topic coverage;
- ranking and region behavior remain unchanged.

Therefore this seam must not weaken or reinterpret legacy topic semantics.

## 7. Open-visual selector contract

For `GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT`, selector
eligibility must require all existing general conditions plus the affirmative
source declaration:

`InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY in source.capabilities`

The selector must not infer this from:

- `topics == frozenset()`;
- `query_text` support;
- adapter registration;
- source kind or authority;
- network flags;
- `media_type` parameters.

If no registered declared source has the capability, selection returns the
existing typed `UNAVAILABLE` result with no source and no query.

## 8. Query-contract defense in depth

`GovernedSourceQueryContract.prepare()` must independently validate the same
capability for an `OPEN_VISUAL_SUBJECT` query.

A direct query that names a source without the declared capability must be
rejected even if it bypasses conversational selection.

For topic-constrained queries, existing topic validation remains unchanged.

Thus:

`SELECTOR ELIGIBILITY != SOLE AUTHORIZATION`

and:

`SOURCE DECLARATION -> SELECTOR CHECK + QUERY CONTRACT CHECK`

## 9. Non-default source declarations

The existing non-default source admission path may carry the same
`GovernedInformationSource.capabilities` metadata.

No second admission mechanism is required.

A future source declaring `OPEN_VISUAL_SUBJECT_QUERY` is not automatically
usable: it must still satisfy normal declaration/status/registration and have a
compatible registered adapter before productive execution can occur.

## 10. Capability declaration is not provider availability

This contract-design seam deliberately separates:

1. semantic permission in source metadata; from
2. actual availability of a capable governed source and adapter.

Therefore completing this seam may still leave every real open-visual request
`UNAVAILABLE`.

That is correct until `OPEN_VISUAL_SUBJECT_CAPABLE_SOURCE_AVAILABILITY` is
separately reconciled and authorized.

## 11. Contract RED obligations

A bounded future CONTRACT RED may require:

1. canonical `InformationSourceCapability` vocabulary;
2. `OPEN_VISUAL_SUBJECT_QUERY` capability value;
3. legacy source declarations default to an empty capability set;
4. NASA remains without the open-visual capability;
5. topic-constrained selection behavior remains unchanged;
6. open-visual selection rejects a registered source without the capability;
7. open-visual selection can select an otherwise eligible synthetic/non-default
   declaration that explicitly has the capability;
8. open-visual no-capable-source state remains typed `UNAVAILABLE`;
9. `GovernedSourceQueryContract.prepare()` rejects open-visual queries against
   a source lacking the capability;
10. the query contract accepts an otherwise valid open-visual query against a
    declaration carrying the capability;
11. non-default source admission preserves capability metadata;
12. no parallel registry, selector, executor, router, or manager appears;
13. no provider, freshness, ranking, or presentation behavior is introduced.

Synthetic declarations in contract tests are contract fixtures only and must
not be treated as authorization for a productive provider.

## 12. Classification

`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

The change deepens existing source declaration and validation surfaces. It does
not establish a new authority.

## 13. RED authorization boundary

The semantic contract is now sufficiently precise for a bounded CONTRACT RED
covering only `OPEN_VISUAL_SOURCE_CAPABILITY_DECLARATION`.

CONTRACT RED is authorized for this first seam only.

Productive GREEN remains unauthorized until that RED is created and Owner
certified.

Provider/source addition remains unauthorized.

## 14. Explicit exclusions

This design does not authorize:

- making NASA a general image source;
- adding a general image provider or adapter;
- external image freshness ordering;
- changing source ranking;
- changing desktop presentation;
- changing natural-language admission;
- reopening request representation;
- interpreting empty topics as a wildcard.

## 15. Work ordering

1. request representation — CLOSED / OWNER-CERTIFIED;
2. source capability declaration — CONTRACT RED NEXT;
3. capable source availability/integration — LATER / SEPARATE;
4. external image freshness ordering — LATER.

## 16. Integrity

This reconciliation changes documentation only.

Productive Python delta: zero.

Test Python delta: zero.

No historical guard or hash is rewritten.

No new authority is introduced.

## 17. Status

`CONTRACT_DESIGN_RECONCILIATION: COMPLETE`

`CAPABILITY_REPRESENTATION: EXPLICIT FROZEN SET`

`CAPABILITY_VALUE: OPEN_VISUAL_SUBJECT_QUERY`

`LEGACY_SOURCE_DEFAULT: EMPTY CAPABILITY SET`

`NASA_OPEN_VISUAL_CAPABILITY: ABSENT / REQUIRED TO REMAIN ABSENT`

`TOPIC_CONSTRAINED_BEHAVIOR: PRESERVED`

`OPEN_VISUAL_SELECTOR_AUTHORIZATION: EXPLICIT CAPABILITY REQUIRED`

`QUERY_CONTRACT_DEFENSE_IN_DEPTH: REQUIRED`

`NO_CAPABLE_SOURCE: TYPED UNAVAILABLE`

`NON_DEFAULT_SOURCE_PATH: EXISTING / REUSED`

`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`

`CONTRACT_RED_AUTHORIZATION: YES / CAPABILITY DECLARATION SEAM ONLY`

`PRODUCTIVE_GREEN_AUTHORIZATION: NO`

`PROVIDER_ADDITION_AUTHORIZATION: NO`

`FRESHNESS: EXCLUDED`

`NEW_AUTHORITY: NONE`
