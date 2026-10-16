# ROBY XI.2 — Open Visual Capable Source Declaration Without Fake Topic
## Contract RED

### Scope
Contract-only RED for the Owner-certified contract design.

No productive Python is modified. No Wikimedia Commons adapter/source is added.
No freshness or presentation behavior is changed.

### RED obligations
The architecture contract proves:
- empty-topic source without `OPEN_VISUAL_SUBJECT_QUERY` remains invalid;
- empty-topic source with explicit capability must become valid;
- capability does not require empty topics;
- default sources retain real topic declarations;
- NASA remains topic-bounded and lacks the capability;
- an empty-topic capable source must use existing non-default admission;
- when registered it must be eligible for `OPEN_VISUAL_SUBJECT`;
- it must not become a `TOPIC_CONSTRAINED` wildcard;
- query preparation must rely on explicit capability;
- `GovernedInformationItem` empty topics remain invalid;
- no Wikimedia provider or parallel registry/selector/executor is introduced.

### Expected RED
Focused contract result:
`5 FAILED / 6 PASSED`

All five failures arise from the single current productive invariant:
`GovernedInformationSource.__post_init__()` rejects every empty `topics` set.

There are no fixture/API mismatches in the contract test.

### GREEN boundary
The future surgical GREEN is authorized only to deepen
`GovernedInformationSource` declaration validity to the already designed rule:

`bool(topics) OR OPEN_VISUAL_SUBJECT_QUERY in capabilities`

Selector and query-contract capability enforcement already exist and must not be
weakened. `GovernedInformationItem` remains unchanged.

`WIKIMEDIA_COMMONS` remains a later provider-specific integration.
