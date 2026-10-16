# ROBY XI.2 — R-CI-SI-S5-B2-A2-A
## Explicit Discriminating Evidence Materialization / Requirement Binding Foundation
### Contract RED

Status: RED CONTRACTUAL — pending OWNER CERTIFICATION

## 1. Purpose

Freeze the minimum governed contract for admitting an explicit binding
between an existing path-discrimination requirement R and an existing
canonical evidence reference E.

This block establishes only that the exact evidence reference E is explicitly
materialized for the exact requirement R.

It does not determine whether E satisfies R, inspect evidence content,
determine a comparative effect on either path, prefer a path, rank paths,
select a path, or authorize acquisition or execution.

## 2. Certified input boundary

The immediate epistemic upstream authority is R-CI-SI-S5-B2-A1.

The admission boundary MUST consume an actual
`ExplicitPathDiscriminationRequirement` artifact. It MUST NOT reconstruct R
from a requirement identity, path strings, eligibility anchors, or detached
lineage data.

The evidence anchor MUST be an actual canonical
`core.governed_reasoning.evidence.EvidenceReference` artifact.

The foundation MUST reuse `EvidenceReference` as the existing cross-domain
evidence identity. It MUST NOT create a universal evidence DTO, a second
evidence registry, or a parallel evidence authority.

The certified chain is:

`ExplicitPathDiscriminationRequirement R`
+ `EvidenceReference E`
+ explicit R/E materialization declaration
→ admitted R/E materialization binding
→ STOP.

## 3. Existing authority boundaries

The following existing authorities MUST remain unchanged:

- S5-B2-A1 owns the explicit path-discrimination requirement R;
- `EvidenceReference` owns canonical evidence-reference identity;
- existing source-specific adapters and acquisition authorities own creation
  or normalization of their evidence;
- existing evidence registries remain the canonical registry infrastructure;
- requirement satisfaction remains downstream and absent from this block;
- comparative discrimination, preference, ranking, selection, and
  authorization remain downstream and absent.

A common evidence-reference format does not create common epistemic meaning.

`EVIDENCE IDENTITY ≠ REQUIREMENT BINDING`.

`REUSE OF REFERENCE TYPE ≠ TRANSFER OF SOURCE AUTHORITY`.

## 4. Required explicit declaration

The declaration MUST be explicit and MUST identify at minimum:

- the exact discrimination-requirement identity R;
- the exact canonical evidence identity `evidence_id` for E;
- the declaration provenance authority;
- non-empty evidence codes supporting the declaration lineage.

The authorized provenance for this foundation is exactly:

`governed_explicit_discriminating_evidence_materialization_declaration`

The declaration MUST NOT infer the R/E relation from:

- requirement text or labels;
- evidence `summary`;
- evidence `metadata`;
- source type or source id semantics;
- capability name or declared evidence output metadata;
- evidence codes;
- fingerprint similarity;
- timestamps or freshness;
- confidence or evidence quality;
- source kind;
- human or creator identity;
- fuzzy or semantic matching;
- an LLM;
- retrieval.

Evidence codes supporting the declaration MUST NOT be interpreted as the
materialized evidence content and MUST NOT establish satisfaction of R.

## 5. Required admitted relation

A successful admission represents only:

`THE EXACT CANONICAL EVIDENCE REFERENCE E IS EXPLICITLY MATERIALIZED FOR`
`THE EXACT PATH-DISCRIMINATION REQUIREMENT R`.

The admitted relation MUST preserve at minimum:

- the actual requirement anchor R;
- R's epistemic-need identity;
- R's epistemic-need source reference;
- R's epistemic-need lineage kind;
- R's requirement identity;
- the actual canonical evidence anchor E;
- E's exact `evidence_id`;
- E's exact source type;
- E's exact source id;
- E's exact fingerprint;
- declaration provenance authority;
- declaration evidence codes.

The binding MUST NOT state or imply that E satisfies R, is relevant in
content, favors path A, favors path B, is preferable to other evidence, or
makes either path preferable or selectable.

## 6. Contract requirements

### R1 — Exact existing R and E artifacts are mandatory

Admission MUST require an actual `ExplicitPathDiscriminationRequirement` R
and an actual canonical `EvidenceReference` E.

Raw requirement identities, raw evidence ids, detached source metadata,
summaries, dictionaries, reconstructed evidence references, or path strings
MUST NOT substitute for either anchor.

The foundation MUST NOT reconstruct A1 eligibility semantics or the original
source artifact behind E.

### R2 — Exact declaration-to-R correspondence is mandatory

The declaration MUST identify exactly `R.requirement_identity`.

No text inference, metadata inference, fuzzy matching, semantic matching,
LLM interpretation, retrieval, or other repair mechanism may establish or
repair correspondence.

Any requirement-identity mismatch MUST fail closed.

### R3 — Exact declaration-to-E correspondence is mandatory

The declaration MUST identify exactly `E.evidence_id`.

The admission boundary MUST preserve E's exact canonical identity and MUST
NOT substitute another evidence reference based on source type, source id,
summary, metadata, fingerprint similarity, timestamps, or content.

Any evidence-identity mismatch MUST fail closed.

### R4 — Canonical evidence identity and provenance are preserved

The admitted binding MUST preserve E's exact:

- `evidence_id`;
- source type;
- source id;
- fingerprint.

The foundation MUST NOT mutate E, recompute a different evidence identity,
rewrite its source provenance, inspect its source artifact, or create a
second evidence registry entry.

A2-A MUST NOT require E to originate from path A or path B. Evidence may be
bound to R only through the explicit admission discipline regardless of its
source domain.

`PATH THAT MAY RESOLVE X ≠ SOURCE OF DISCRIMINATING EVIDENCE`.

### R5 — Authorized provenance and explicit declaration lineage are mandatory

The declaration provenance MUST equal exactly:

`governed_explicit_discriminating_evidence_materialization_declaration`

The declaration MUST carry non-empty explicit evidence codes.

Absent, blank, synthetic, inferred, or unauthorized provenance or lineage
MUST fail closed.

Human or creator origin MUST NOT bypass this admission discipline.

`DECLARER ≠ ADMISSION AUTHORITY`.

`HUMAN SOURCE ≠ AUTOMATIC R/E BINDING`.

### R6 — Absence or rejection remains epistemically neutral

Missing declaration, rejected declaration, R mismatch, E mismatch,
unauthorized provenance, missing explicit lineage, or attempted inferred
binding MUST produce no admitted R/E materialization binding.

Such absence or rejection MUST NOT create or imply:

- E_DOES_NOT_SATISFY_R;
- E_IS_IRRELEVANT;
- R_IS_UNSATISFIABLE;
- PATHS_EQUIVALENT;
- PATHS_INDISTINGUISHABLE;
- a negative comparative result;
- a preference;
- permission to select either path.

`NOT BOUND ≠ NOT SATISFYING`.

### R7 — Binding remains non-satisfying and non-comparative

An admitted R/E binding MUST represent only explicit materialization of E
for R.

It MUST NOT:

- inspect or interpret evidence content;
- assert that E satisfies R;
- assert that E partially satisfies R;
- score satisfaction;
- compare E with other evidence;
- aggregate multiple evidence references into a satisfaction result;
- determine whether E favors path A or path B;
- compare, rank, prefer, filter, or select either path;
- infer preference from E's source domain;
- infer satisfaction from evidence codes or metadata;
- authorize acquisition or execution.

Zero, one, or many E references may be independently bound to the same R.
Cardinality MUST NOT create satisfaction, preference, ranking, or selection.

### R8 — Read-only, derivational, inert admission boundary

The admission boundary MUST be read-only and derivational.

It MUST NOT:

- mutate R or E;
- mutate or reconstruct A1 eligibility anchors;
- query or mutate the capability registry;
- query or mutate the official runtime;
- query or mutate an evidence registry;
- resolve E back to its original source artifact;
- create or normalize new evidence;
- create evidence bundles;
- infer R/E binding from text or metadata;
- use fuzzy or semantic matching;
- use an LLM or retrieval to establish the relation;
- acquire evidence;
- evaluate evidence quality or requirement satisfaction;
- score, compare, rank, prefer, filter, or select sources or paths;
- select capabilities;
- plan or authorize acquisition;
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

## 7. Evidence-source neutrality

The evidence source domain MUST NOT establish the R/E relation by itself.

Evidence originating from a human, creator, household member, document,
knowledge item, task, briefing, acquired capability output, or another
governed source may participate only as an actual canonical
`EvidenceReference` under the same explicit admission discipline.

Source relationship, availability, accessibility, source type, or creator
status MUST NOT establish binding, satisfaction, preference, truth, or
selection authority.

`HUMAN SOURCE ≠ PRIVILEGED SOURCE`.

`CREATOR STATUS ≠ ADMISSION AUTHORITY`.

## 8. Semantic boundaries

The following distinctions are contractual:

`EVIDENCE REFERENCE ≠ EVIDENCE CONTENT`.

`EVIDENCE IDENTITY ≠ REQUIREMENT BINDING`.

`MATERIALIZED EVIDENCE ≠ SATISFYING EVIDENCE`.

`R/E BINDING ≠ REQUIREMENT SATISFACTION`.

`SATISFACTION ≠ COMPARATIVE EFFECT`.

`COMPARATIVE EFFECT ≠ PREFERENCE`.

`PREFERENCE ≠ SELECTION`.

`SELECTION ≠ AUTHORIZATION`.

`METADATA ≠ ADMISSION`.

`CODE MATCH ≠ ADMISSION`.

`SOURCE PROVENANCE ≠ SATISFACTION`.

`NOT BOUND ≠ NOT SATISFYING`.

`HUMAN SOURCE ≠ PRIVILEGED SOURCE`.

## 9. STOP boundary

This contract STOPS immediately after admission of the explicit R/E
materialization binding.

It does not authorize:

`REQUIREMENT SATISFACTION`
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

Those tests MUST target one absent narrow product seam under
`core.cognitive_maturity` and demonstrate failure exclusively because the
explicit discriminating-evidence materialization / requirement-binding
foundation is not yet implemented.

No GREEN implementation is authorized by this document.
