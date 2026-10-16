# ROBY XI.2 — Open Visual Capable Source Declaration Without Fake Topic
## Contract Design Reconciliation

### Certified input
The provider/integration reconciliation is Owner-certified at 13,531 PASS /
0 FAIL, Ruff clean, with `WIKIMEDIA_COMMONS` selected only as the preferred
future provider candidate.

No provider adapter is introduced by this block.

### Exact existing invariant
`GovernedInformationSource.__post_init__()` currently rejects every source whose
`topics` set is empty.

That invariant correctly protects legacy/topic-constrained source declarations,
but it forces a semantically false `InterestTopic` onto a source authorized only
for general `OPEN_VISUAL_SUBJECT_QUERY`.

### Contract decision
The existing `GovernedInformationSource` model is deepened, not replaced.

Source declaration validity becomes:

1. a source with one or more topics remains valid exactly as today;
2. a source with empty topics is valid only when its explicit `capabilities`
   contains `InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY`;
3. a source with empty topics and no such capability remains invalid;
4. declaring `OPEN_VISUAL_SUBJECT_QUERY` does not require empty topics;
5. capability metadata remains the authorization mechanism for open-visual
   selection and query preparation.

Conceptual predicate:

`bool(topics) OR OPEN_VISUAL_SUBJECT_QUERY in capabilities`

This predicate applies only to source-declaration validity.

### Explicit non-wildcard rule
Empty source topics do not mean "all topics".

`TOPIC_CONSTRAINED` continues to use the existing topic subset contract.
An empty-topic open-visual source therefore cannot become eligible for ordinary
topic-constrained requests.

`OPEN_VISUAL_SUBJECT` continues to require the explicit
`OPEN_VISUAL_SUBJECT_QUERY` capability in both:
- `GovernedConversationalSourceSelector`;
- `GovernedSourceQueryContract.prepare()`.

No eligibility may be inferred from empty topics.

### GovernedInformationItem is unchanged
The existing `GovernedInformationItem` non-empty-topic invariant is not part of
this seam and must remain unchanged.

Provider adapters return raw mappings through the governed query executor; the
existing external-image presentation projects the raw visual fields. This
contract design therefore does not justify weakening information-item topic
requirements or `GovernedInformationSources.accept()`.

### Legacy preservation
All existing default sources retain non-empty topic declarations.
NASA remains topic-bounded and lacks the open-visual capability.
Existing non-open-visual sources with empty topics remain invalid.

### Contract RED obligations
The future RED must prove at least:

1. empty-topic `GovernedInformationSource` without open-visual capability is
   rejected;
2. empty-topic source with `OPEN_VISUAL_SUBJECT_QUERY` is accepted;
3. open-visual capability with non-empty topics is also accepted;
4. all current default sources remain unchanged;
5. NASA still lacks the capability and remains topic-bounded;
6. an empty-topic capable source can be admitted through the existing
   non-default source admission path;
7. when registered, that source can be eligible for an
   `OPEN_VISUAL_SUBJECT` request;
8. the same source is not an accidental wildcard for `TOPIC_CONSTRAINED`;
9. `GovernedSourceQueryContract.prepare()` accepts an open-visual query only
   because of explicit capability, not because source topics are empty;
10. `GovernedInformationItem` still rejects empty topics;
11. no provider adapter, provider-specific source, freshness ordering,
    presentation change, registry, selector, executor, router, or gateway
    authority is introduced.

### Change classification
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

Canonical model:
`GovernedInformationSource`

Existing authorities reused:
- `GovernedInformationSources`;
- `GovernedConversationalSourceSelector`;
- `GovernedSourceQueryContract`;
- `GovernedSourceQueryExecutor`;
- `OfficialConversationGateway`.

### Scope boundary
This seam only makes an honest open-visual source declaration representable.
It does not make Wikimedia Commons productive and does not prove provider
availability.

After this seam is GREEN and reconciled, the provider-specific Wikimedia
Commons contract/integration can be designed separately.

`EXTERNAL_IMAGE_FRESHNESS_ORDERING` remains later.

### Authorization state
`CONTRACT_DESIGN_RECONCILIATION: COMPLETE`
`DECLARATION_VALIDITY_RULE: TOPICS_NONEMPTY OR OPEN_VISUAL_CAPABILITY`
`EMPTY_TOPICS_AS_TOPIC_WILDCARD: FORBIDDEN`
`GOVERNED_INFORMATION_ITEM_CHANGE: FORBIDDEN / OUT OF SCOPE`
`NASA_GENERALIZATION: NO`
`WIKIMEDIA_ADAPTER: NOT IMPLEMENTED`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`CONTRACT_RED_AUTHORIZATION: YES / THIS SEAM ONLY`
`PRODUCTIVE_GREEN_AUTHORIZATION: NO`
`PROVIDER_GREEN_AUTHORIZATION: NO`
`FRESHNESS: EXCLUDED / LATER`
`NEW_AUTHORITY: NONE`
