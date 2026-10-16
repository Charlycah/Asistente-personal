# ROBY XI.2 — R-CI-SI-S5-B2-A1
## Explicit Path Discrimination Requirement Foundation — RED Contractual

Status: RED CONTRACTUAL — pending OWNER CERTIFICATION

## 1. Purpose

Freeze the minimum governed contract for admitting an explicit epistemic
requirement that is material to discriminating two distinct, positively
eligible resolution paths for the same exact epistemic need.

This block establishes only WHAT EVIDENCE IS REQUIRED TO DISCRIMINATE.
It does not acquire that evidence, evaluate it, prefer a path, rank paths,
select a path, or authorize execution.

## 2. Certified input boundary

The immediate upstream authority is R-CI-SI-S5-B1-B.

The admission boundary MUST consume two actual
`GovernedSelectionEligibility` artifacts. It MUST NOT reconstruct their
suitability, resolution binding, registry availability, runtime readiness,
or eligibility semantics.

Both anchors MUST be positively eligible and MUST refer to the same exact
epistemic need lineage while representing distinct resolution paths.

The certified upstream chain remains:

`ExplicitEpistemicSuitability`
→ `GovernedSelectionEligibility`
→ this explicit discrimination-requirement admission boundary
→ STOP.

## 3. Existing authority boundaries

The following existing authorities MUST remain unchanged:

- S4-T owns explicit epistemic resolution binding.
- S5-B1-A owns explicit epistemic suitability admission.
- S5-B1-B owns governed selection eligibility.
- hypothesis discrimination owns hypothesis-specific discrimination.
- evidence acquisition/planning authorities remain downstream.
- source preference, ranking, selection, and authorization remain absent
  from this foundation.

A discrimination requirement for eligible resolution paths is a distinct
semantic relation. Reuse of a similarly named hypothesis DTO or authority
MUST NOT transfer authority into this chain.

`PATH ≠ HYPOTHESIS`.

`REUSE OF TYPE ≠ REUSE OF AUTHORITY`.

## 4. Required explicit declaration

The declaration MUST be explicit and MUST identify at minimum:

- the exact epistemic need identity X;
- exact path A by capability name and declared evidence output;
- exact path B by capability name and declared evidence output;
- an explicit discrimination-requirement identity R;
- the declaration provenance authority;
- non-empty evidence codes supporting the declaration lineage.

The authorized provenance for this foundation is exactly:

`governed_explicit_path_discrimination_requirement_declaration`

The declaration MUST NOT infer the requirement from free text, capability
metadata, tags, semantic similarity, fuzzy matching, an LLM, retrieval,
confidence, source kind, runtime status, or human/creator identity.

Evidence codes supporting the declaration MUST NOT be interpreted as the
future discriminating evidence requested by R.

The declaration MUST NOT contain or encode a winner, loser, preferred path,
selected path, rank, score, weight, priority, recommendation, or equivalent
preference direction.

## 5. Required admitted relation

A successful admission represents only:

`R IS AN EXPLICIT GOVERNED REQUIREMENT MATERIAL TO DISCRIMINATING`
`PATH A FROM PATH B FOR EXACT X`.

The admitted relation MUST preserve:

- X;
- the epistemic-need source reference;
- the epistemic-need lineage kind;
- exact path A identity;
- exact path B identity;
- requirement identity R;
- declaration provenance authority;
- declaration evidence codes.

The pair is semantically neutral. Argument order MUST NOT encode preference.
The admitted relation MUST NOT state that A is better than B, B is better
than A, either path is selected, or either path is authorized.

## 6. Contract requirements

### R1 — Two exact existing B1-B eligibility anchors are mandatory

Admission MUST require two actual `GovernedSelectionEligibility` artifacts.
Raw strings, detached suitability objects, resolution bindings, capability
descriptors, runtime observations, or reconstructed eligibility data MUST
NOT substitute for either anchor.

Both anchors MUST have `eligible_for_selection is True`.

A non-positive eligibility anchor MUST fail closed and MUST NOT be promoted
by this foundation.

### R2 — Exact same-X lineage correspondence is mandatory

Both eligibility anchors MUST refer to exactly the same:

- epistemic need identity;
- epistemic-need source reference;
- epistemic-need lineage kind.

The declaration MUST identify that same exact X.

No text inference, metadata inference, fuzzy matching, semantic matching,
LLM interpretation, retrieval, or other repair mechanism may establish or
repair correspondence.

Any mismatch MUST fail closed.

### R3 — The two eligible paths must be structurally distinct

The compared anchors MUST represent distinct resolution paths.

At minimum, the exact `(capability_name, declared_evidence_output)` path
identity MUST differ between A and B.

`DISCRIMINATE(A, A)` MUST NOT be admitted.

Distinctness MUST NOT itself create preference, ranking, or selection.

### R4 — Exact declaration-to-pair correspondence is mandatory

The explicit declaration MUST correspond exactly to:

- X;
- path A capability and declared evidence output;
- path B capability and declared evidence output;
- explicit requirement identity R.

The admission boundary MUST NOT substitute another capability, evidence
output, need, requirement, or path by semantic similarity.

Pair-order handling MUST remain preference-neutral. Reversing A and B MUST
NOT create a different winner, loser, priority, score, or recommendation.

### R5 — Authorized provenance and explicit lineage are mandatory

The declaration provenance MUST equal exactly:

`governed_explicit_path_discrimination_requirement_declaration`

The declaration MUST carry non-empty explicit evidence codes.

Absent, blank, synthetic, inferred, or unauthorized provenance/lineage MUST
fail closed.

Human or creator origin MUST NOT bypass this admission discipline.

`DECLARER ≠ ADMISSION AUTHORITY`.

`HUMAN AS EVIDENCE ≠ HUMAN AS TRUTH`.

### R6 — Absence or rejection remains epistemically neutral

Missing declaration, rejected declaration, non-positive eligibility,
lineage mismatch, same-path input, or unauthorized provenance MUST produce
no admitted discrimination requirement.

Such absence or rejection MUST NOT create or imply:

- PATHS_EQUIVALENT;
- PATHS_INDISTINGUISHABLE;
- NO_DISCRIMINATION_NEEDED;
- EITHER_PATH_ACCEPTABLE;
- UNSUITABLE;
- a negative preference;
- permission to select either path.

`NOT ADMITTED ≠ PATHS EQUIVALENT`.

### R7 — Requirement identity remains non-preferential and non-selective

An admitted requirement MUST represent only what evidence is required to
perform a future discrimination between A and B for X.

It MUST NOT:

- acquire the required evidence;
- assert that the required evidence exists;
- evaluate evidence against R;
- compare evidence quality;
- determine a comparative winner;
- score, rank, prefer, filter, or select either path;
- infer selection from there being only one other eligible path;
- authorize acquisition or execution.

Zero or one eligible path MUST NOT synthesize a pairwise requirement.
Multiple admitted pairwise requirements MUST remain independent and
unranked.

### R8 — Read-only, derivational, inert admission boundary

The admission boundary MUST be read-only and derivational.

It MUST NOT:

- mutate either eligibility anchor;
- mutate or reconstruct suitability;
- mutate or reconstruct resolution bindings;
- query or mutate the capability registry;
- query or mutate the official runtime;
- create runtime graphs or readiness evidence;
- create or reconstruct eligibility;
- infer discrimination requirements;
- infer requirements from text or metadata;
- use fuzzy or semantic matching;
- use an LLM or retrieval to establish the relation;
- acquire or evaluate discriminating evidence;
- score, compare, rank, prefer, filter, or select sources/paths;
- select capabilities;
- plan or authorize acquisition;
- acquire evidence;
- certify truth or grant cognitive authority;
- create questions or assign question-worthiness;
- assign relevance or invoke curiosity;
- create goals or invoke initiative;
- invoke conversation;
- persist results or modify memory;
- create learning candidates;
- execute actions;
- claim subjective experience or consciousness.

No `app.*` dependency may be introduced into `core` by the future GREEN.

## 7. Human-as-evidence boundary

A human, creator, household member, document, capability, or other governed
source may contribute evidence supporting an explicit declaration only
through the same admission discipline.

Creator status, relationship, availability, conversational accessibility,
or a human assertion MUST NOT automatically establish the requirement and
MUST NOT establish preference, selection, truth, or authority.

`CREATOR STATUS ≠ ADMISSION AUTHORITY`.

`HUMAN SOURCE ≠ PRIVILEGED SOURCE`.

## 8. Semantic boundaries

The following distinctions are contractual:

`DECLARATION ≠ TRUTH`.

`DECLARER ≠ ADMISSION AUTHORITY`.

`REQUIREMENT ≠ DISCRIMINATING EVIDENCE`.

`REQUIREMENT ≠ COMPARATIVE RESULT`.

`REQUIREMENT ≠ PREFERENCE`.

`PREFERENCE ≠ SELECTION`.

`SELECTION ≠ AUTHORIZATION`.

`NOT ADMITTED ≠ PATHS EQUIVALENT`.

`PAIR ORDER ≠ PREFERENCE DIRECTION`.

`ONE ELIGIBLE PATH ≠ SELECTED PATH`.

`HUMAN AS EVIDENCE ≠ HUMAN AS TRUTH`.

## 9. STOP boundary

This contract STOPS immediately after admission of the explicit path
discrimination requirement.

It does not authorize:

`DISCRIMINATING EVIDENCE ACQUISITION`
→ `DISCRIMINATING EVIDENCE EVALUATION`
→ `COMPARATIVE DISCRIMINATION RESULT`
→ `SOURCE PREFERENCE`
→ `RANKING`
→ `SOURCE SELECTION`
→ `ACQUISITION AUTHORIZATION`
→ `NEED-TO-ASK`
→ `QUESTION-WORTHINESS`
→ `RELEVANCE`
→ `CURIOSITY`
→ `INITIATIVE`
→ `CONVERSATION`.

## 10. RED-test target after owner certification

After OWNER CERTIFICATION of this contractual RED, the next authorized
increment is RED TESTS R1-R8 only.

Those tests should target one absent narrow product seam under
`core.cognitive_maturity` and demonstrate failure exclusively because the
explicit path-discrimination-requirement foundation is not yet implemented.

No GREEN implementation is authorized by this document.
