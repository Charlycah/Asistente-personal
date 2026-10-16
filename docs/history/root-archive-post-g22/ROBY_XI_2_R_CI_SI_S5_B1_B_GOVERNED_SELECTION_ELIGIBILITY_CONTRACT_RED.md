# ROBY XI.2 — R-CI-SI-S5-B1-B
## Governed Selection Eligibility — RED Contractual

Status: RED CONTRACTUAL — FROZEN FOR OWNER CERTIFICATION

## 1. Purpose

Freeze the minimum governed contract that composes already-admitted explicit
epistemic suitability with the exact current registry and canonical runtime
operability evidence of the same epistemic resolution path, only to determine
whether that path has positive evidence for selection eligibility.

B1-B is read-only and derivational. It does not select, prefer, rank, authorize,
or execute any resolution path.

## 2. Certified input boundary

The contract consumes existing governed evidence only:

- one `ExplicitEpistemicSuitability` admitted by S5-B1-A for exact `(X, C, D)`;
- the exact S5-A `CanonicalRuntimeReadinessProjectionObservation` whose nested
  S4-Z observation preserves the same S4-T resolution binding `(X, C, D)`; and
- the canonical runtime-readiness evidence already preserved by S5-A where it
  exists.

B1-B MUST NOT reconstruct suitability, registry availability, runtime
readiness, or an S4-T resolution binding from raw identifiers.

## 3. Existing authority boundaries

S5-B1-A owns explicit epistemic suitability admission.

S4-Z owns current registry resolution-path availability.

S5-A owns projection of canonical runtime readiness onto the exact S4-Z path.

The existing runtime-readiness authority owns the meaning of its canonical
`ready`, availability, degraded state, blockers, warnings, residents, and
dependency evidence.

B1-B owns only the narrow composition:

`SUITABLE(X,C/D) + POSITIVE CURRENT OPERABILITY(C) → SELECTION ELIGIBILITY`.

It MUST NOT become a second suitability authority, registry authority, runtime
readiness authority, source selector, acquisition planner, or authorization
authority.

## 4. Required eligibility semantics

A path may be positively eligible for selection only when all of the following
are present for the exact same path:

- admitted `ExplicitEpistemicSuitability` for X/C/D;
- S4-Z status `REGISTRY_AVAILABLE` for that exact C/D binding;
- S5-A runtime projection for exact C;
- canonical runtime-readiness evidence is present; and
- canonical `runtime_readiness.ready is True`.

The positive result means only that the path may enter a later governed source
selection boundary.

`ELIGIBLE != PREFERRED != RANKED != SELECTED != AUTHORIZED`.

Absence of positive eligibility MUST NOT create `UNSUITABLE` or any other
negative epistemic authority.

## 5. Contract requirements

### R1 — Exact governed evidence anchors are mandatory

B1-B MUST require an actual `ExplicitEpistemicSuitability` and an actual S5-A
`CanonicalRuntimeReadinessProjectionObservation`.

It MUST NOT admit raw X/C/D strings, registry descriptors, runtime nodes,
readiness reports detached from S5-A lineage, or newly reconstructed S4-T
bindings as substitutes.

### R2 — Exact same-path correspondence is mandatory

The B1-A suitability relation and the S5-A observation MUST refer to the exact
same epistemic resolution path.

At minimum, B1-B MUST require exact equality of:

- epistemic need identity X;
- capability name C;
- declared evidence output D;
- epistemic-need source reference; and
- epistemic-need lineage kind.

The comparison MUST follow the nested S5-A → S4-Z → S4-T binding lineage.

Any mismatch MUST fail closed with no positive eligibility result.

No fuzzy, semantic, case-insensitive, alias, substring, embedding, retrieval,
or LLM matching may repair a mismatch.

### R3 — Current registry availability is mandatory

The nested S4-Z observation MUST be exactly `REGISTRY_AVAILABLE`.

`NOT_REGISTERED`, `EVIDENCE_DECLARATION_MISMATCH`, and `DISABLED` MUST NOT
produce positive selection eligibility, even when B1-A suitability exists.

These states MUST NOT erase or negate the suitability evidence.

`NOT CURRENTLY ELIGIBLE != UNSUITABLE`.

### R4 — Canonical positive runtime readiness is mandatory

Positive selection eligibility requires canonical runtime-readiness evidence
preserved by S5-A and `runtime_readiness.ready is True`.

B1-B MUST NOT recreate readiness rules from lifecycle, dependency declarations,
blockers, warnings, residents, availability labels, or other runtime metadata.

`READINESS_NOT_PROVISIONED`, `READINESS_NOT_DECLARED`, `UNKNOWN`, a missing
canonical readiness object, or canonical `ready is not True` MUST NOT produce
positive eligibility.

None of those states may be converted into `UNSUITABLE`.

### R5 — DEGRADED follows canonical readiness, not a new B1-B policy

S5-A preserves `DEGRADED` without collapsing it into `UNAVAILABLE`.

Therefore B1-B MUST NOT define `DEGRADED` as automatically eligible or
automatically ineligible.

A `DEGRADED` path may receive positive selection eligibility only when the
canonical readiness object preserved by S5-A explicitly reports
`ready is True`.

If canonical readiness reports `ready is not True`, no positive eligibility is
established.

B1-B MUST NOT reinterpret blockers or warnings to override that canonical
judgment.

`DEGRADED != UNAVAILABLE`.

### R6 — Eligibility absence is not negative suitability

If suitability is absent, the path has no B1-B positive eligibility basis.

If suitability exists but registry availability or canonical readiness does not
provide positive current operability, B1-B produces no positive eligibility.

Neither case may create an `UNSUITABLE` assertion, negative suitability score,
negative source authority, or permanent path prohibition.

`NO POSITIVE ELIGIBILITY != UNSUITABLE`.

Operational state may change without changing the admitted B1-A suitability
relation.

### R7 — Zero, one, or many eligible paths remain unranked and auditable

B1-B MUST NOT infer selection from cardinality.

Zero, one, or many paths may independently have positive selection eligibility.
One eligible path MUST NOT become selected merely because it is unique.

B1-B MUST NOT compare, score, rank, prefer, or choose among eligible paths.

Where B1-B composes a set/report, it MUST preserve the original path evidence
and deterministic upstream ordering. Paths without positive eligibility MUST
remain auditable rather than being physically filtered away.

`ONE ELIGIBLE PATH != SELECTED PATH`.

### R8 — Read-only, derivational, non-selective boundary

The B1-B seam MUST be `read_only=True` and `derivational=True`.

It MUST NOT:

- mutate B1-A suitability or any S4-T/S4-Z/S5-A evidence;
- create or reconstruct suitability declarations or suitability relations;
- query or mutate the capability registry;
- query or mutate the official runtime;
- create or reconstruct runtime graphs or readiness evidence;
- reproduce canonical runtime-readiness rules;
- infer suitability from operational state;
- use text, metadata, tags, risk, confidence, freshness, source authority,
  semantic matching, fuzzy matching, embeddings, retrieval, or LLM inference
  to establish eligibility;
- score, compare, rank, prefer, filter, or select sources/capabilities;
- plan, authorize, or perform evidence acquisition;
- certify truth or grant cognitive authority;
- create questions or assign question-worthiness;
- assign relevance or invoke curiosity;
- create goals or invoke initiative;
- invoke conversation;
- persist results or modify memory;
- create learning candidates;
- execute actions; or
- claim subjective experience or consciousness.

## 6. Human-as-evidence boundary

A human-backed C/D path receives no special eligibility treatment.

Human identity, creator status, household membership, conversational
availability, or relationship to ROBY MUST NOT bypass suitability, registry
availability, canonical readiness, or exact-path correspondence.

`HUMAN AVAILABILITY != HUMAN EPISTEMIC AUTHORITY`.

`NEED_TO_KNOW != NEED_TO_ASK_HUMAN`.

## 7. Semantic boundaries

The following distinctions are contractual:

`SUITABLE != OPERABLE`

`OPERABLE != SUITABLE`

`REGISTRY_AVAILABLE != ELIGIBLE`

`RUNTIME READY != ELIGIBLE` without admitted suitability

`ELIGIBLE != PREFERRED`

`ELIGIBLE != RANKED`

`ELIGIBLE != SELECTED`

`ELIGIBLE != AUTHORIZED`

`NO POSITIVE ELIGIBILITY != UNSUITABLE`

`DEGRADED != UNAVAILABLE`

`ONE ELIGIBLE PATH != SELECTED PATH`

## 8. STOP boundary

The block ends after determining whether exact governed evidence establishes
positive selection eligibility for the exact existing resolution path.

`EXPLICIT SUITABILITY(X,C/D)`
`+ EXACT S5-A / S4-Z / S4-T PATH LINEAGE`
`+ REGISTRY_AVAILABLE`
`+ CANONICAL RUNTIME READINESS.ready == True`
`→ ELIGIBLE FOR LATER SELECTION`
`→ STOP`

No progression is authorized to:

`SOURCE PREFERENCE → SOURCE RANKING → SOURCE SELECTION → ACQUISITION`
`→ AUTHORIZATION → NEED-TO-ASK / QUESTION-WORTHINESS → RELEVANCE`
`→ CURIOSITY → INITIATIVE → CONVERSATION`.

## 9. RED-test target after owner certification

After this contractual document is owner-certified, RED tests should require
one minimal subordinate composition seam only, conceptually under:

`core.cognitive_maturity.governed_selection_eligibility`

The RED tests MUST fail exclusively because that eligibility seam is absent.

They MUST NOT require changes to S4-T, S4-W, S4-Z, S5-A, S5-B1-A, capability
registry, runtime graph/readiness authority, evidence acquisition planning,
source selection, authorization, curiosity, initiative, or conversation
authorities.

No productive implementation is authorized by this RED contractual step.
