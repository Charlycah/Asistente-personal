# ROBY XI.2 — External Image Freshness Order Source Capability Declaration
## CONTRACT DESIGN RECONCILIATION

### Certified input
Owner-certified PRE-RED baseline:
- 13,575 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated / reproducible;
- parent residual: `EXTERNAL_IMAGE_FRESHNESS_ORDERING`;
- exact prerequisite:
  `EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`.

This step designs the contract only. No productive Python or test change is
made.

## 1. Classification and authority
Classification:
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

Canonical authority remains:
`app.governed_information_sources.InformationSourceCapability`
and the existing immutable `GovernedInformationSource.capabilities`.

No second capability registry, provider feature manager, freshness manager,
selector, executor, router, or planner is authorized.

## 2. New capability semantic
Future enum member:

`EXTERNAL_IMAGE_NEWEST_FIRST_QUERY = "external_image_newest_first_query"`

Meaning:
the source explicitly declares that its governed adapter can receive an
external-image query whose requested result order is newest-first and can
project that order into a provider-supported query semantic without inferring
order from incidental result metadata.

The capability does NOT mean:
- generic temporal filtering;
- arbitrary date-window support;
- timestamp presence;
- creation-time metadata accuracy for every returned item;
- UI-side sorting;
- executor-side sorting;
- automatic fetching;
- general open-visual subject support.

Permanent:
`NEWEST_FIRST_CAPABILITY != TIMESTAMP_METADATA`
`NEWEST_FIRST_CAPABILITY != DATE_FILTER_CAPABILITY`
`NEWEST_FIRST_CAPABILITY != OPEN_VISUAL_SUBJECT_QUERY`

## 3. Capability independence
Capabilities compose explicitly.

A source may have:
- neither capability;
- only `OPEN_VISUAL_SUBJECT_QUERY`;
- only `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`;
- both, if each semantic is independently proven.

No implication in either direction is permitted.

## 4. Legacy/default source preservation
All existing default governed sources remain with their current empty
capability sets in this prerequisite block, including NASA.

Rationale:
NASA currently demonstrates date-bound filtering and returns date metadata,
but no certified newest-first external-image query contract has been proven.

Therefore:
`NASA_NEWEST_FIRST_CAPABILITY: NOT DECLARED`

No capability may be inferred from NASA's `published_at`,
`year_start/year_end`, source authority, confidence, or official status.

## 5. Wikimedia declaration
Wikimedia Commons is the only current candidate for later declaration because
provider documentation supports an explicit newest-first search-order semantic.

However this capability-declaration prerequisite must preserve dependency
ordering.

The future GREEN for this block may declare
`EXTERNAL_IMAGE_NEWEST_FIRST_QUERY` on the existing
`WikimediaCommonsGovernedSourceAdapter.source_declaration` only if the same
contract also establishes that declaration as a governed promise to be consumed
by the subsequent order-representation/provider-projection blocks.

It does NOT yet make natural-language freshness reachable and does NOT yet
change the adapter request parameters.

Expected Wikimedia capabilities after this block:
- `OPEN_VISUAL_SUBJECT_QUERY`
- `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`

## 6. Empty-topic invariant
The existing exception allowing an empty source topic set remains tied to
`OPEN_VISUAL_SUBJECT_QUERY`.

The new newest-first capability MUST NOT independently authorize empty topics.

Thus a hypothetical source with:
- empty topics; and
- only `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`

must still be rejected by `GovernedInformationSource`.

This prevents freshness capability from accidentally becoming a wildcard
source-admission capability.

## 7. Selection and query-contract behavior in this block
This prerequisite block does NOT yet modify source eligibility.

The selector and query contract currently have no freshness-order request
representation to consume, so they must not be changed prematurely.

Therefore:
- no freshness capability filtering in selector yet;
- no freshness capability validation in query contract yet;
- no query model field yet;
- no provider order parameter yet;
- no natural-language freshness admission yet.

Those belong to subsequent residuals.

## 8. Contract RED obligations
The future RED must prove at minimum:

1. `InformationSourceCapability` exposes exactly
   `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY` with value
   `"external_image_newest_first_query"`.
2. Legacy/default sources retain empty capability sets.
3. NASA does not claim the new capability.
4. Wikimedia source declaration explicitly contains both
   `OPEN_VISUAL_SUBJECT_QUERY` and `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`.
5. Timestamp-bearing source/item metadata does not automatically add the
   capability.
6. A source with topics may explicitly declare the new capability without
   needing `OPEN_VISUAL_SUBJECT_QUERY`.
7. Empty topics plus only newest-first capability remain invalid.
8. Empty topics plus `OPEN_VISUAL_SUBJECT_QUERY` remain valid, preserving the
   certified invariant.
9. No selector/query-contract/executor/presentation authority is created or
   modified by the GREEN.
10. No freshness order request representation or provider parameter is
    introduced in this block.
11. No parallel freshness/provider authority module appears.

## 9. Expected RED failure convergence
Before GREEN, RED should fail only because:
- enum member is absent; and
- Wikimedia does not yet declare it.

Existing behavior around empty topics, legacy capability defaults, NASA, and
absence of premature downstream wiring should remain green.

The RED must not require a provider request-order implementation yet.

## 10. Expected surgical GREEN envelope
Expected productive Python delta:

1. `app/governed_information_sources.py`
   - add the enum member only.
2. `app/wikimedia_commons_governed_source.py`
   - add the new capability to the existing immutable source declaration.

No other productive Python file is authorized.

In particular, do not modify:
- `app/applied_conversational_intelligence.py`;
- `app/governed_conversational_request_mode.py`;
- `app/governed_conversational_source_selection.py`;
- `app/governed_source_query.py`;
- `app/governed_source_query_executor.py`;
- `app/nasa_governed_source.py`;
- runtime wiring/composition;
- OfficialConversationGateway;
- desktop/presentation modules.

## 11. Post-block residual
After this declaration is certified, the parent residual remains open at:

`GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`

No productive provider projection or natural-language freshness behavior may be
claimed from capability declaration alone.

## 12. Formal design state
`CONTRACT_DESIGN_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`PARENT: EXTERNAL_IMAGE_FRESHNESS_ORDERING`
`SEAM: EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`CANONICAL_AUTHORITY: InformationSourceCapability + GovernedInformationSource.capabilities`
`NEW_CAPABILITY: EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`
`CAPABILITY_VALUE: external_image_newest_first_query`
`WIKIMEDIA_EXPECTED_DECLARATION: OPEN_VISUAL_SUBJECT_QUERY + EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`
`NASA_EXPECTED_DECLARATION: NONE`
`EMPTY_TOPIC_EXCEPTION: OPEN_VISUAL_SUBJECT_QUERY ONLY`
`SELECTOR_CHANGE: NONE`
`QUERY_CONTRACT_CHANGE: NONE`
`EXECUTOR_CHANGE: NONE`
`PROVIDER_QUERY_CHANGE: NONE`
`NATURAL_LANGUAGE_CHANGE: NONE`
`EXPECTED_GREEN_PRODUCTIVE_DELTA: governed_information_sources.py + wikimedia_commons_governed_source.py ONLY`
`PRODUCTIVE_PYTHON_DELTA_NOW: ZERO`
`TEST_DELTA_NOW: ZERO`
`NEW_AUTHORITY: NONE`
`CONTRACT_RED_AUTHORIZATION_AFTER_OWNER_CERTIFICATION: YES`
`NEXT: EXTERNAL IMAGE FRESHNESS ORDER SOURCE CAPABILITY DECLARATION — CONTRACT RED`
