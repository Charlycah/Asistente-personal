# ROBY XI.2 — R-CI-SI-S5-B2-A2-B
## Explicit Requirement Satisfaction Foundation — Contract RED

Status: RED CONTRACTUAL — pending OWNER CERTIFICATION

## 1. Purpose

Freeze the minimum governed contract for admitting a positive explicit
requirement-satisfaction relation between an already admitted discriminating
evidence materialization and its exact path-discrimination requirement.

This block establishes only that the exact canonical evidence E already
materialized for the exact requirement R is explicitly admitted as satisfying
R.

It does not certify universal truth, inspect evidence content, infer semantic
fit, determine how E affects path A or path B, prefer a path, rank paths,
select a path, or authorize acquisition or execution.

## 2. Certified input boundary

The immediate epistemic upstream authority is R-CI-SI-S5-B2-A2-A.

The admission boundary MUST consume an actual
`ExplicitDiscriminatingEvidenceMaterialization` artifact. It MUST NOT
reconstruct the R/E materialization relation from a requirement identity,
evidence id, detached R and E artifacts, source metadata, or lineage data.

The certified chain is:

`ExplicitDiscriminatingEvidenceMaterialization M`
+ explicit requirement-satisfaction declaration
→ admitted positive requirement-satisfaction relation
→ STOP.

M already preserves the actual
`ExplicitPathDiscriminationRequirement` R and the actual canonical
`EvidenceReference` E. This foundation MUST reuse those anchors exactly.

## 3. Existing authority boundaries

The following existing authorities MUST remain unchanged:

- S5-B2-A1 owns the explicit path-discrimination requirement R;
- `EvidenceReference` owns canonical evidence-reference identity;
- S5-B2-A2-A owns explicit materialization and binding of E to R;
- source-specific authorities continue to own creation or normalization of E;
- existing evidence-quality authorities keep their existing domain semantics;
- existing epistemic normalization authorities keep their existing roles;
- hypothesis discrimination remains hypothesis-specific;
- comparative path discrimination remains downstream and absent here;
- preference, ranking, selection, and authorization remain downstream.

A valid evidence reference does not establish requirement satisfaction.

A strong or well-formed evidence assessment does not establish requirement
satisfaction.

`MATERIALIZED(R,E) ≠ SATISFIES(R,E)`.

`EVIDENCE QUALITY ≠ REQUIREMENT SATISFACTION`.

`REUSE OF EVIDENCE IDENTITY ≠ TRANSFER OF EPISTEMIC AUTHORITY`.

## 4. Required explicit declaration

The declaration MUST be explicit and MUST identify at minimum:

- the exact requirement identity already preserved by M;
- the exact canonical evidence identity already preserved by M;
- the declaration provenance authority;
- non-empty evidence codes supporting the declaration lineage.

The authorized provenance for this foundation is exactly:

`governed_explicit_requirement_satisfaction_declaration`

The declaration MUST NOT infer satisfaction from:

- requirement text, labels, or naming;
- evidence `summary` or evidence content;
- evidence `metadata`;
- source type or source id semantics;
- capability names or declared evidence-output metadata;
- evidence codes from A1, A2-A, or this declaration;
- fingerprint similarity;
- timestamps or freshness;
- confidence or evidence-quality classifications;
- source kind, authority labels, or provenance alone;
- human, creator, or household identity;
- fuzzy or semantic matching;
- an LLM;
- retrieval.

Evidence codes supporting the satisfaction declaration establish only the
explicit lineage of that declaration. They MUST NOT be treated as the
materialized evidence content or as an automatic proof of satisfaction.

## 5. Required admitted relation

A successful admission represents only:

`THE EXACT CANONICAL EVIDENCE E ALREADY MATERIALIZED FOR THE EXACT`
`PATH-DISCRIMINATION REQUIREMENT R IS EXPLICITLY ADMITTED AS SATISFYING R`.

The admitted relation MUST preserve at minimum:

- the actual materialization anchor M;
- the actual requirement anchor R preserved by M;
- R's epistemic-need identity;
- R's epistemic-need source reference;
- R's epistemic-need lineage kind;
- R's exact requirement identity;
- the actual canonical evidence anchor E preserved by M;
- E's exact evidence id;
- E's exact source type;
- E's exact source id;
- E's exact fingerprint;
- satisfaction-declaration provenance authority;
- satisfaction-declaration evidence codes.

The admitted relation MUST NOT state or imply that E is universally true,
favors path A, favors path B, makes either path preferable, ranks evidence,
selects a path, or authorizes any acquisition or execution.

## 6. Contract requirements

### R1 — Exact existing A2-A materialization anchor is mandatory

Admission MUST require an actual
`ExplicitDiscriminatingEvidenceMaterialization` M.

Detached R and E artifacts, raw requirement identities, raw evidence ids,
dictionaries, summaries, source metadata, or reconstructed materialization
objects MUST NOT substitute for M.

The foundation MUST NOT recreate A1 or A2-A admission semantics.

### R2 — Exact declaration-to-requirement correspondence is mandatory

The declaration MUST identify exactly `M.requirement_identity`.

That identity MUST remain the exact requirement identity of the actual R
already preserved by M.

No text inference, metadata inference, fuzzy matching, semantic matching,
LLM interpretation, retrieval, or repair mechanism may establish or repair
correspondence.

Any requirement-identity mismatch MUST fail closed.

### R3 — Exact declaration-to-evidence correspondence is mandatory

The declaration MUST identify exactly `M.evidence_id`.

That identity MUST remain the exact canonical evidence id of the actual E
already preserved by M.

The admission boundary MUST NOT substitute another evidence reference based
on source type, source id, summary, metadata, fingerprint similarity,
timestamps, evidence quality, or content.

Any evidence-identity mismatch MUST fail closed.

### R4 — Upstream R/E anchors and lineage are preserved exactly

A successful satisfaction relation MUST preserve M and its actual R and E
anchors without mutation or reconstruction.

It MUST preserve the exact epistemic-need lineage, requirement identity,
evidence identity, evidence source type, evidence source id, and evidence
fingerprint already certified by A2-A.

The foundation MUST NOT query an evidence registry, capability registry, or
runtime to rebuild or strengthen the relation.

It MUST NOT require E to originate from path A or path B.

`SOURCE OF E ≠ PATH FAVORED BY E`.

### R5 — Authorized provenance and explicit satisfaction lineage are mandatory

The satisfaction-declaration provenance MUST equal exactly:

`governed_explicit_requirement_satisfaction_declaration`

The declaration MUST carry non-empty explicit evidence codes.

Absent, blank, synthetic, inferred, or unauthorized provenance or lineage
MUST fail closed.

The A2-A materialization provenance MUST NOT substitute for satisfaction
provenance.

Human, creator, or household origin MUST NOT bypass this discipline.

`MATERIALIZATION DECLARER ≠ SATISFACTION DECLARER`.

`DECLARER ≠ ADMISSION AUTHORITY`.

### R6 — Absence or rejection remains epistemically neutral

Missing declaration, rejected declaration, requirement mismatch, evidence
mismatch, unauthorized provenance, missing explicit lineage, or attempted
inferred satisfaction MUST produce no admitted satisfaction relation.

Such absence or rejection MUST NOT create or imply:

- E_DOES_NOT_SATISFY_R;
- E_PARTIALLY_SATISFIES_R;
- E_IS_IRRELEVANT;
- E_IS_FALSE;
- R_IS_UNSATISFIABLE;
- PATHS_ARE_EQUIVALENT;
- PATHS_ARE_INDISTINGUISHABLE;
- a negative comparative result;
- a preference;
- permission to select either path.

`NO SATISFACTION ADMISSION ≠ DOES NOT SATISFY`.

### R7 — Satisfaction remains non-comparative and non-selective

An admitted relation MUST represent only the positive explicit relation
`SATISFIES(R,E)` for the exact upstream M.

It MUST NOT:

- inspect or interpret evidence content;
- invent FULL, PARTIAL, WEAK, or scored satisfaction states;
- infer satisfaction from evidence quality or provenance;
- compare E with other evidence references;
- aggregate multiple satisfying evidence references;
- determine whether E favors path A or path B;
- determine comparative discrimination effect;
- rank or prefer evidence or paths;
- filter or select a path;
- authorize acquisition or execution;
- certify universal truth.

Zero, one, or multiple distinct evidence materializations may independently
have positive admitted satisfaction relations for the same R. Cardinality
MUST NOT create ranking, preference, aggregation, or selection.

`SATISFIED ≠ TRUE`.

`SATISFIED ≠ FAVORS A`.

`SATISFIED ≠ FAVORS B`.

`SATISFIED ≠ COMPARATIVE EFFECT`.

`SATISFIED ≠ PREFERRED ≠ SELECTED ≠ AUTHORIZED`.

### R8 — The foundation is read-only, derivational, and inert

The declaration, admitted relation, and admission boundary MUST remain
read-only and derivational.

This foundation MUST NOT:

- mutate M, R, or E;
- create or normalize evidence;
- query or mutate evidence registries;
- query capability registries or runtime readiness;
- resolve or acquire sources;
- use fuzzy matching, semantic matching, an LLM, or retrieval;
- evaluate evidence quality or freshness;
- inspect evidence content;
- compute partial satisfaction or satisfaction scores;
- compute comparative discrimination effect;
- score, compare, rank, prefer, filter, or select sources or paths;
- plan or authorize acquisition;
- certify truth;
- create questions or assign question-worthiness;
- assign relevance;
- invoke curiosity;
- create goals;
- invoke initiative or conversation;
- persist results or modify memory;
- create learning candidates;
- execute actions;
- grant cognitive authority;
- claim subjective experience or consciousness.

A future core GREEN implementation MUST NOT depend on `app.*`.

## 7. Evidence-source neutrality

The satisfaction relation is source-neutral.

Human, creator, household, document, knowledge, task, briefing, acquired
output, or another governed source may participate only through the actual
canonical E already preserved by M.

Source identity, accessibility, relationship, provenance, quality, or
availability MUST NOT by itself establish satisfaction, comparative effect,
preference, truth, selection, or authorization.

`HUMAN SOURCE ≠ PRIVILEGED SATISFACTION SOURCE`.

## 8. Architectural non-goals

This block MUST NOT create:

- a second evidence registry;
- a universal evidence DTO;
- a satisfaction scorer;
- a semantic evidence matcher;
- a new reasoner or cognitive brain;
- a source-preference authority;
- a path selector;
- an acquisition planner;
- an authorization authority;
- a truth-certification authority.

The expected future implementation shape is a narrow declaration DTO, a
narrow admitted satisfaction relation, and a narrow admission boundary under
`core.cognitive_maturity`.

## 9. STOP boundary

The architectural chain ends here:

`PATH-DISCRIMINATION REQUIREMENT R`
→ `EXPLICIT R/E MATERIALIZATION M`
→ `EXPLICIT POSITIVE REQUIREMENT SATISFACTION`
→ STOP.

This contract does NOT authorize:

`COMPARATIVE DISCRIMINATION EFFECT`
→ `SOURCE OR PATH PREFERENCE`
→ `RANKING`
→ `SOURCE OR PATH SELECTION`
→ `ACQUISITION AUTHORIZATION`
→ `NEED-TO-ASK`
→ `QUESTION-WORTHINESS`
→ `RELEVANCE`
→ `CURIOSITY`
→ `INITIATIVE`
→ `CONVERSATION`.

## 10. RED acceptance condition

After OWNER CERTIFICATION of this contractual document, the next increment
may add RED tests R1-R8 against one absent narrow product seam under
`core.cognitive_maturity`.

Those tests MUST fail exclusively because the requirement-satisfaction
foundation is absent.

No GREEN implementation is authorized by this document alone.

## 11. Frozen semantic boundary

`MATERIALIZED ≠ SATISFIED`.

`SATISFIED ≠ TRUE`.

`SATISFIED ≠ COMPARATIVE EFFECT`.

`COMPARATIVE EFFECT ≠ PREFERENCE`.

`PREFERENCE ≠ SELECTION`.

`SELECTION ≠ AUTHORIZATION`.

`NO SATISFACTION ADMISSION ≠ DOES NOT SATISFY`.
