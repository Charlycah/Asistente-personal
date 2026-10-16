# ROBY XI.2 — General Open Visual Natural Language Admission
## SURGICAL GREEN

Owner-certified RED input: 13,571 PASS / 4 intentional FAIL.

### Productive delta
Exactly one productive Python file changed:
`app/applied_conversational_intelligence.py`

No test Python changed during GREEN.

### Implemented contract
The existing `AppliedConversationalIntelligence` now:
- preserves governed-topic recognition and the existing known-topic path;
- admits an unknown-topic explicit visual request only when the bounded
  `mostrame <visual noun> de <subject>` subject can be extracted;
- rejects missing/blank/punctuation-only subjects;
- constructs the existing request with empty topics, extracted query text,
  limit 5, GLOBAL region and `OPEN_VISUAL_SUBJECT` mode;
- does not select Wikimedia or any provider.

### Surgical evidence in assistant environment
- focal + directly related visual contracts: 44 PASS / 0 FAIL;
- productive/test Python delta versus RED: ACI only;
- changed ACI maximum line length: 84;
- Python syntax/AST valid.

The assistant environment does not expose an executable Ruff command, so Ruff
is deliberately NOT claimed as locally executed here. Owner certification must
run the canonical local cycle and remains authoritative for Ruff and full suite.

### Preserved boundaries
No new authority, InterestTopic, provider selection, selector/executor/query
contract change, gateway change, Wikimedia change, presentation change, or
freshness behavior.

### Formal state
`SURGICAL_GREEN: COMPLETE / PENDING OWNER CERTIFICATION`
`RELATED_VISUAL_CONTRACTS: 44 PASS / 0 FAIL`
`PRODUCTIVE_PYTHON_DELTA: ACI ONLY`
`GREEN_TEST_PYTHON_DELTA: ZERO`
`KNOWN_TOPIC_VISUAL_BEHAVIOR: PRESERVED`
`GENERAL_VISUAL_MODE: OPEN_VISUAL_SUBJECT`
`SUBJECT_EXTRACTION: BOUNDED / FAIL_CLOSED`
`PROVIDER_SELECTION: DOWNSTREAM EXISTING AUTHORITY`
`FRESHNESS: OUT_OF_SCOPE`
`NEW_AUTHORITY: NONE`
`RUFF_ASSISTANT_ENVIRONMENT: NOT AVAILABLE / OWNER CERTIFICATION REQUIRED`
`NEXT_AFTER_OWNER_CERTIFICATION: POST_GREEN_MASTER_PLAN_RECONCILIATION`
