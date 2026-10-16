# ROBY XI.2 — R-CI-SI-S5-B1-A
## Explicit Epistemic Suitability Foundation — RED Contractual

Status: RED CONTRACTUAL — FROZEN FOR OWNER CERTIFICATION

## 1. Purpose

Freeze the minimum governed contract for admitting explicit evidence that one
already-admitted S4-T epistemic resolution binding `(X, C, D)` is suitable as
an epistemic resolution path for that exact need.

B1-A is read-only and derivational. It does not infer suitability, rank paths,
select a source, authorize acquisition, or grant cognitive authority.

## 2. Certified input boundary

The contract consumes:

- one existing `EpistemicResolutionBinding` produced by S4-T; and
- one explicit epistemic-suitability declaration referring to the exact
  epistemic need identity X and exact C/D represented by that binding.

The existing S4-T binding remains the canonical authority for the relation
`C/D RESOLVES X`. B1-A MUST NOT reconstruct, broaden, repair, or replace that
relation.

B1-A MUST NOT require the capability registry, runtime graph, runtime-readiness
report, acquisition planner, source selector, authorization authority, or
conversation authorities in order to admit suitability.

## 3. Existing canonical precedent and authority boundary

S4-T already establishes the governed pattern:

`ExplicitEpistemicResolutionDeclaration`
`→ EpistemicResolutionBindingAdmission`
`→ EpistemicResolutionBinding`.

Its admission requires explicit identity, exact C/D correspondence, authorized
provenance, and non-inferred lineage. B1-A reuses that architectural discipline,
not S4-T's semantic authority.

S4-T owns:

`C/D RESOLVES X`.

B1-A may own only:

`an admitted explicit declaration supports SUITABLE(X, C/D)`.

`RESOLUTION BINDING != SUITABILITY BINDING`.

## 4. Required explicit suitability declaration

The B1-A declaration MUST explicitly carry enough information to identify:

- epistemic need identity X;
- capability name C;
- declared evidence output D;
- provenance authority; and
- one or more explicit evidence codes establishing declaration lineage.

The declaration MUST NOT derive X, C, D, or suitability from free text,
metadata, tags, confidence, freshness, embeddings, retrieval, fuzzy matching,
semantic matching, or LLM inference.

The authorized provenance token for this foundation is frozen as:

`governed_explicit_epistemic_suitability_declaration`.

This token authorizes admission provenance only. It does not make the declarer
a truth authority, cognitive authority, source selector, or acquisition
authority.

## 5. Required admitted suitability relation

A successful admission MUST preserve, at minimum:

- exact capability name C from the existing S4-T binding;
- exact declared evidence output D from that binding;
- exact epistemic need identity X from that binding;
- the S4-T epistemic-need source reference;
- the S4-T epistemic-need lineage kind;
- the suitability declaration provenance authority;
- the suitability declaration evidence codes; and
- `read_only=True`.

The admitted relation is evidence only that the exact existing resolution path
has explicit governed suitability support for X.

It MUST NOT represent a score, preference, rank, selection, authorization,
truth certification, or execution decision.

## 6. Contract requirements

### R1 — Exact existing S4-T binding is mandatory

B1-A MUST require an actual `EpistemicResolutionBinding` as its resolution-path
anchor.

It MUST NOT create a binding from raw capability names, registry descriptors,
evidence-output text, metadata, or a new resolution declaration.

The admitted suitability relation MUST preserve the exact X/C/D and epistemic
lineage represented by that existing binding.

### R2 — Exact declaration-to-binding correspondence is mandatory

The suitability declaration MUST identify the same X, C, and D as the supplied
S4-T binding.

Any mismatch in epistemic need identity, capability name, or declared evidence
output MUST fail closed and produce no admitted suitability relation.

No fuzzy, semantic, case-insensitive substitute, alias, retrieval, embedding,
substring, or LLM matching may repair a mismatch.

### R3 — Authorized suitability provenance is mandatory

The declaration MUST carry exactly:

`governed_explicit_epistemic_suitability_declaration`.

Any other provenance authority MUST fail closed.

Authorized provenance means only that the declaration is eligible for this
admission boundary. It MUST NOT grant truth authority, cognitive authority,
source preference, source selection, or acquisition authorization.

### R4 — Explicit independent evidence lineage is mandatory

The declaration MUST contain at least one non-empty evidence code and MUST
preserve those evidence codes in the admitted relation.

The declaration MUST reject attempts to mark suitability as inferred from text
or metadata, produced by fuzzy or semantic matching, or synthesized through LLM
or retrieval inference.

`EXPLICIT SUITABILITY != INFERRED SUITABILITY`.

### R5 — Admission is independent of current registry/runtime operability

B1-A MUST NOT query or require current capability registration, enabled state,
runtime graph membership, runtime availability, runtime readiness, blockers, or
warnings in order to admit suitability.

An existing S4-T binding may remain epistemically suitable even when the
corresponding path is not currently operable.

`SUITABILITY != CURRENT OPERABILITY`.

Current operability remains owned by S4-Z/S5-A and may only be composed by a
later explicitly authorized block.

### R6 — Absence or rejection is not UNSUITABLE

If no explicit suitability declaration exists, B1-A produces no admitted
suitability relation.

If a declaration fails exact correspondence, provenance, or explicit-lineage
requirements, B1-A MUST fail closed and produce no admitted suitability
relation.

Neither case may be represented as `UNSUITABLE`.

`NO DECLARATION != UNSUITABLE`.

`REJECTED DECLARATION != UNSUITABLE`.

B1-A introduces no negative-suitability authority.

### R7 — Multiple admitted suitable paths remain non-ranked

Zero, one, or many S4-T bindings may independently receive admitted suitability
evidence for the same epistemic need identity.

B1-A MUST NOT compare, score, rank, prefer, deduplicate across distinct C/D
bindings, or choose among those relations.

`MULTIPLE SUITABLE PATHS != AMBIGUITY RESOLVED`.

`ONE SUITABLE PATH != AUTOMATIC SELECTION`.

### R8 — Read-only, derivational, non-selective boundary

The B1-A admission seam MUST be `read_only=True` and `derivational=True`.

It MUST NOT:

- mutate the S4-T binding or any upstream evidence;
- query or mutate the capability registry;
- query or mutate the official runtime;
- create or reconstruct runtime graphs or readiness evidence;
- create new S4-T resolution bindings;
- infer suitability from text, metadata, confidence, freshness, tags, risk,
  capability kind, source authority, or runtime state;
- use fuzzy, semantic, embedding, retrieval, substring, or LLM matching to
  synthesize suitability;
- score, compare, rank, prefer, filter, or select sources/capabilities;
- plan, authorize, or perform evidence acquisition;
- certify truth or grant cognitive authority;
- create questions or assign question-worthiness;
- assign relevance or invoke curiosity;
- create goals or invoke initiative;
- invoke conversation;
- persist results or modify memory;
- create learning candidates;
- execute actions;
- claim subjective experience or consciousness.

## 7. Human-as-evidence boundary

A human-originated declaration may be represented only through the same
explicit declaration and admission rules as any other origin.

Human identity, creator status, household membership, conversational
availability, or relationship to ROBY MUST NOT by themselves imply suitability,
truth, preference, selection, or authority.

`HUMAN AS EVIDENCE != HUMAN AS TRUTH`.

`HUMAN AVAILABILITY != HUMAN EPISTEMIC AUTHORITY`.

## 8. Semantic boundaries

The following distinctions are contractual:

`C/D RESOLVES X != C/D IS SUITABLE FOR X`

`SUITABLE != PREFERRED`

`SUITABLE != SELECTED`

`SUITABLE != AUTHORIZED`

`SUITABILITY != CURRENT OPERABILITY`

`REGISTRY AVAILABLE != SUITABLE`

`RUNTIME READY != SUITABLE`

`SOURCE AUTHORITY != SOURCE PREFERENCE`

`PROVENANCE != SOURCE PREFERENCE`

`NO DECLARATION != UNSUITABLE`

`REJECTED DECLARATION != UNSUITABLE`

`ONE SUITABLE PATH != AUTOMATIC SELECTION`

## 9. STOP boundary

The block ends after admission, or fail-closed non-admission, of explicit
suitability evidence for an exact existing S4-T `(X, C, D)` binding.

`EXISTING S4-T RESOLUTION BINDING`
`+ EXPLICIT SUITABILITY DECLARATION`
`+ AUTHORIZED EXACT PROVENANCE`
`+ EXACT X/C/D CORRESPONDENCE`
`→ ADMITTED EXPLICIT EPISTEMIC SUITABILITY`
`→ STOP`

No progression is authorized to:

`SELECTION ELIGIBILITY → SOURCE PREFERENCE → SOURCE SELECTION → ACQUISITION`
`→ NEED-TO-ASK / QUESTION-WORTHINESS → RELEVANCE → CURIOSITY → INITIATIVE`
`→ CONVERSATION`.

## 10. RED-test target after owner certification

After this contractual document is owner-certified, RED tests should require
one minimal subordinate admission seam only, conceptually under:

`core.cognitive_maturity.explicit_epistemic_suitability`

The RED tests MUST fail exclusively because that suitability foundation seam is
absent.

They MUST NOT require changes to S4-T, S4-W, S4-Z, S5-A, capability registry,
runtime graph/readiness, evidence acquisition planning, source selection,
authorization, curiosity, initiative, or conversation authorities.

No productive implementation is authorized by this RED contractual step.
