# ROBY XI.2 — Open Visual Capable Source Declaration Without Fake Topic
## Surgical GREEN

### Productive change
Exactly one productive Python file changed:
`app/governed_information_sources.py`.

`GovernedInformationSource.__post_init__()` now rejects empty topics unless the
same source declaration explicitly carries
`InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY`.

Implemented predicate:
`bool(topics) OR OPEN_VISUAL_SUBJECT_QUERY in capabilities`.

### Preserved boundaries
- empty topics are not a topic wildcard;
- selector open-visual capability enforcement is unchanged;
- query-contract open-visual capability enforcement is unchanged;
- `GovernedInformationItem` is unchanged;
- all default source declarations are unchanged;
- NASA is unchanged and not generalized;
- no Wikimedia Commons source or adapter is introduced;
- no provider, freshness, presentation, registry, executor, selector, router, or
  gateway authority is introduced.

### Verification
The new RED contract plus the prior source-capability contract pass locally.
The broader relevant source/query/selection contract set also passes locally.
Python AST and line-length checks pass; productive file maximum line length is
88.

The execution environment used to build this artifact does not provide the
`ruff` Python module. Ruff cleanliness therefore remains subject to Owner local
certification; no claim of local Ruff execution is made here.

### Delta
Productive Python delta: exactly one file.
Test Python delta from the certified CONTRACT RED: zero.
