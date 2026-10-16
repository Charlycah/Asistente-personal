# ROBY XI.2 — General Open Visual Natural Language Admission
## CONTRACT RED

### Owner-certified input
Contract Design input is Owner-certified:
- 13,562 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated / reproducible.

### RED scope
One architecture contract is added:
`tests/architecture/test_general_open_visual_natural_language_admission_contract_red.py`

No productive Python is changed.

The RED encodes the certified Contract Design:
- arbitrary explicit visual subject admission;
- `OPEN_VISUAL_SUBJECT` representation;
- bounded subject extraction;
- known-topic visual compatibility;
- fail-closed subjectless/punctuation-only requests;
- provider ignorance inside ACI;
- downstream existing Wikimedia selection;
- existing selector UNAVAILABLE behavior;
- gateway execution ownership;
- no parallel authority;
- freshness exclusion.

### Intentional failure convergence
Focal RED result:
`4 FAILED / 9 PASSED`

Related contract result:
`4 FAILED / 40 PASSED`

The four intentional failures are:
1. Saturn is still NOT_RECOGNIZED instead of an open-visual request.
2. Nazca is still NOT_RECOGNIZED instead of an open-visual request.
3. downstream capable-Wikimedia selection cannot start because ACI returns no
   request for Saturn.
4. existing UNAVAILABLE behavior cannot be reached from natural language
   because ACI returns no request for Saturn.

All four converge on the same absent productive seam:
`EXPLICIT_GENERAL_VISUAL_LANGUAGE_TO_OPEN_VISUAL_REQUEST_ADMISSION`
with
`BOUNDED_OPEN_VISUAL_SUBJECT_EXTRACTION`.

### Protected GREEN evidence
The RED already passes the protections for:
- James Webb known-topic visual compatibility;
- NASA known-topic visual compatibility;
- subjectless visual requests fail closed;
- punctuation-only subject fails closed under current behavior;
- non-visual `mostrame` remains not recognized;
- ACI contains no Wikimedia/provider selection;
- gateway remains execution owner;
- no parallel visual authority;
- no freshness behavior.

Existing related contracts outside the new failing obligations remain green.

### GREEN authorization boundary
If Owner certification reproduces the intentional RED, Surgical GREEN is
authorized only in:
`app/applied_conversational_intelligence.py`

Expected GREEN:
- reuse `GovernedConversationalRequestMode`;
- add bounded subject extraction within existing ACI;
- admit valid unknown visual subjects as `OPEN_VISUAL_SUBJECT`;
- preserve known-topic path;
- preserve fail-closed cases.

No other productive Python file is authorized unless RED certification exposes
a genuine contradiction and a new reconciliation is performed first.

### Formal state
`CONTRACT_RED: COMPLETE / PENDING OWNER CERTIFICATION`
`FOCAL: 4 INTENTIONAL FAIL / 9 PASS`
`RELATED: 4 INTENTIONAL FAIL / 40 PASS`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`RED_TEST_DELTA: ONE ARCHITECTURE TEST`
`FAILURE_CONVERGENCE: ACI GENERAL VISUAL ADMISSION + SUBJECT EXTRACTION`
`KNOWN_TOPIC_VISUAL_BEHAVIOR: GREEN / PRESERVED`
`SUBJECTLESS_FAIL_CLOSED: GREEN`
`PROVIDER_SELECTION_AUTHORITY: DOWNSTREAM / GREEN`
`GATEWAY_AUTHORITY: GREEN`
`FRESHNESS: OUT_OF_SCOPE / GREEN`
`NEW_AUTHORITY: NONE`
`EXPECTED_GREEN_PRODUCTIVE_DELTA: ACI ONLY`
