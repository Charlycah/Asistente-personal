# ROBY XI.2 — General Open Visual Natural Language Admission
## CONTRACT DESIGN RECONCILIATION

### Owner-certified starting state
Starting PRE-RED is Owner-certified:
- 13,562 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated / reproducible;
- productive Python delta zero;
- test delta zero.

This Contract Design changes documentation only.

### Classification
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

Canonical admission/request-construction authority remains:
`app.applied_conversational_intelligence:AppliedConversationalIntelligence`

No new intent router, NLP authority, selector, executor, registry, gateway,
presenter, manager, planner, agent, or loop is authorized.

### Existing closed contracts reused
The design reuses without modification:
- `GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT`;
- empty topics permitted only in that mode;
- non-empty `query_text` required in that mode;
- open-visual source capability declaration;
- Wikimedia Commons governed adapter;
- Wikimedia runtime configuration and official registration;
- existing governed source selector;
- existing query contract/executor;
- OfficialConversationGateway execution authority;
- certified desktop visual presentation chain.

`QUERY_TEXT != SOURCE_ELIGIBILITY_AUTHORITY`
`EMPTY_OPEN_VISUAL_TOPICS != WILDCARD`

### Admission decision contract
`AppliedConversationalIntelligence.interpret()` must preserve current topic
recognition first.

A request enters the new open-visual branch only when ALL are true:
1. it is an explicit visual request under the existing bounded visual-language
   semantics;
2. no existing governed `InterestTopic` was matched;
3. a meaningful bounded visual subject can be extracted.

If a governed topic is already matched, existing topic-constrained behavior is
preserved.

Therefore:
`KNOWN_TOPIC_VISUAL_BEHAVIOR: PRESERVE / TOPIC_CONSTRAINED`

Examples remaining compatible:
- `Roby, mostrame fotos de James Webb.` -> existing known-topic request;
- `Roby, mostrame imágenes de NASA.` -> existing known-topic request.

Examples entering the new branch:
- `Roby, mostrame fotos de Saturno.`
- `Roby, mostrame imágenes de las pistas de Nazca.`

Examples that remain not recognized by this capability:
- `Roby, mostrame fotos.`
- `Roby, mostrame imágenes.`
- `Roby, mostrame cómo funciona esto.`

### Visual-language boundary
This block does not broaden general external-query vocabulary.

The existing visual admission signal remains bounded to the certified
`mostrame` + visual-noun semantics (`foto`, `fotos`, `imagen`, `imágenes`,
`imagenes`).

Supporting arbitrary synonyms, English commands, implicit visual requests, or
non-visual `mostrame` is not required by this contract.

### Bounded subject-extraction contract
Subject extraction belongs inside the existing ACI request-construction
authority.

It is not a new router or NLP authority.

For the Contract RED, the minimum accepted grammar is the already-demonstrated
Spanish visual form:

`mostrame <visual noun> de <subject>`

The extractor must:
1. operate on normalized user text;
2. identify the existing bounded visual imperative and visual noun;
3. require the connector `de` for the general-subject branch;
4. preserve the meaningful text following that connector as the search
   subject;
5. trim surrounding whitespace and terminal conversational punctuation;
6. preserve internal words, accents, and ordinary capitalization;
7. reject an absent/blank subject;
8. reject a subject reduced to punctuation;
9. never manufacture an `InterestTopic`;
10. never choose a source id.

Canonical examples:
- `Roby, mostrame fotos de Saturno.` -> `Saturno`
- `Roby, mostrame imágenes de las pistas de Nazca.` -> `las pistas de Nazca`

The earlier representation contract used `pistas de Nazca` as a manually
constructed query example. That contract proved transport semantics, not a
natural-language article-removal rule. This design therefore does NOT
authorize semantic rewriting such as automatically removing `las`.

### Prefix handling
The existing examples include the conversational vocative `Roby,`.

Subject extraction is anchored on the bounded `mostrame` visual phrase, so
text before that phrase is not part of the extracted subject.

This is structural extraction only; it does not introduce a general vocative
parser.

### Request-construction contract
For a valid unknown-subject visual request, ACI constructs exactly one existing
`GovernedConversationalSourceSelectionRequest` with:
- `text`: existing normalized full request;
- `topics=frozenset()`;
- `query_text`: bounded extracted subject;
- `limit=5`, preserving current ACI behavior;
- `region=InformationRegion.GLOBAL`;
- `mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT`.

Other request fields keep existing defaults unless the RED demonstrates a
contradiction.

ACI must not resolve Wikimedia or any other provider.

### Fail-closed contract
If visual language is detected but no meaningful subject is extractable:
- interpretation remains `NOT_RECOGNIZED`;
- request is `None`;
- no governed query executes.

If a valid open-visual request is constructed but no capable source is
registered, the existing downstream selector remains responsible for typed
`UNAVAILABLE`.

Therefore:
`NO_SUBJECT != OPEN_SEARCH`
`NO_CAPABLE_SOURCE != FALLBACK_SOURCE`

### Existing execution ownership
No gateway changes are required by design.

The existing flow remains:
`OfficialConversationGateway`
-> `interpret_applied_conversational_intelligence`
-> existing ACI
-> existing request
-> `execute_selected_governed_conversational_query`
-> existing selector/query contract/executor.

### Freshness boundary
Words and semantics such as latest/newest/most recent remain outside this
block.

This design must not add:
- sorting;
- date filters;
- `published_after`;
- provider-specific recency parameters;
- freshness ranking.

`EXTERNAL_IMAGE_FRESHNESS_ORDERING` remains a later residual.

### Contract RED obligations
A single bounded architecture contract should prove at least:

1. arbitrary `Saturno` visual request is recognized;
2. its request mode is `OPEN_VISUAL_SUBJECT`;
3. its topics are exactly empty;
4. its query text is exactly `Saturno`;
5. its region is GLOBAL and limit remains 5;
6. Nazca request is recognized as open visual;
7. Nazca query preserves meaningful subject text (`las pistas de Nazca`);
8. known James Webb visual request remains recognized with existing topic;
9. known James Webb request remains `TOPIC_CONSTRAINED`;
10. known NASA visual request remains existing topic-constrained behavior;
11. subjectless `mostrame fotos` remains NOT_RECOGNIZED;
12. subjectless `mostrame imágenes` remains NOT_RECOGNIZED;
13. punctuation-only subject fails closed;
14. non-visual `mostrame cómo funciona esto` remains NOT_RECOGNIZED;
15. open-visual request construction does not choose a source id;
16. existing selector capability gating remains unchanged;
17. no capable registered source still yields existing `UNAVAILABLE`;
18. registered capable Wikimedia can be selected downstream from the produced
    open-visual request without direct ACI provider knowledge;
19. existing gateway remains execution owner;
20. no freshness ordering is introduced;
21. no new router/selector/executor/registry/presenter/manager/agent/planner
    authority is introduced;
22. certified request-mode/source-capability/provider modules remain unchanged.

RED failures must converge on absent general-subject admission/extraction in
ACI, not on provider configuration, selector, executor, presentation, or
freshness.

### Expected future GREEN envelope
If Contract RED proves this design, expected productive Python delta is:

`app/applied_conversational_intelligence.py`

only.

No other productive Python file is authorized unless RED exposes a genuine
contract contradiction requiring a new reconciliation.

Likely implementation shape:
- import/reuse `GovernedConversationalRequestMode`;
- bounded private/static subject extraction inside ACI;
- branch unknown-topic explicit visual requests into the existing open-visual
  request representation;
- preserve the current known-topic branch.

This is design guidance, not implementation authorization.

### Explicit protection
Must remain unchanged through RED and expected GREEN:
- `app/governed_conversational_request_mode.py`;
- `app/governed_conversational_source_selection.py`;
- `app/governed_source_query.py`;
- `app/governed_source_query_executor.py`;
- `app/governed_information_sources.py`;
- `app/wikimedia_commons_governed_source.py`;
- `app/runtime_environment_wiring.py`;
- `app/official_runtime_composition.py`;
- `app/official_conversation_gateway.py`;
- desktop external-image presentation/composition modules.

### Next authorization
`CONTRACT_RED_AUTHORIZATION: YES`

Next:
`GENERAL OPEN VISUAL NATURAL LANGUAGE ADMISSION — CONTRACT RED`

The RED may add tests/documentation only. It must not modify productive Python.

### Formal state
`CONTRACT_DESIGN_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`CANONICAL_AUTHORITY: APPLIED_CONVERSATIONAL_INTELLIGENCE`
`KNOWN_TOPIC_VISUAL_BEHAVIOR: PRESERVE / TOPIC_CONSTRAINED`
`GENERAL_VISUAL_MODE: OPEN_VISUAL_SUBJECT`
`GENERAL_VISUAL_TOPICS: EMPTY BY REPRESENTATION / NEVER WILDCARD`
`SUBJECT_EXTRACTION: BOUNDED / FAIL_CLOSED`
`SUBJECT_EXTRACTION_GRAMMAR: MOSTRAME + VISUAL_NOUN + DE + SUBJECT`
`REGION: GLOBAL`
`ACI_LIMIT: 5`
`PROVIDER_SELECTION: DOWNSTREAM EXISTING AUTHORITY`
`FRESHNESS: OUT_OF_SCOPE / LATER`
`EXPECTED_GREEN_PRODUCTIVE_DELTA: ACI ONLY`
`NEW_AUTHORITY: NONE`
`CONTRACT_RED_AUTHORIZATION: YES`
`NEXT: CONTRACT_RED`
