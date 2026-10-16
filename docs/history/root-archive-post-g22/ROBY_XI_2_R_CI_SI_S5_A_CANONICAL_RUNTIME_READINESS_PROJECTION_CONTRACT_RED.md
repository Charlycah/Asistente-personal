# ROBY XI.2 — R-CI-SI-S5-A
## Canonical Runtime Readiness Projection — RED Contractual

Status: RED CONTRACTUAL — FROZEN FOR OWNER CERTIFICATION

## 1. Purpose

Freeze the minimum governed contract that projects canonical runtime-readiness evidence onto S4-Z current-registry resolution-path observations, without creating a second runtime graph, readiness authority, dependency model, source selector, acquisition planner, authorization authority, or conversational authority.

S5-A is read-only and derivational. It does not own runtime state or readiness semantics.

## 2. Certified input boundary

The contract consumes:

- one `CurrentRegistryResolutionPathAvailabilityReport` produced by S4-Z; and
- the canonical `OfficialROBYRuntime`, including its owned `capability_graph` when provisioned and its existing runtime-readiness authority.

Each S4-Z observation preserves the original S4-T binding `(capability_name C, declared_evidence_output D)`.

Only observations whose S4-Z status is `REGISTRY_AVAILABLE` are eligible for runtime-readiness projection. All other observations remain preserved without runtime promotion.

## 3. Existing canonical authority

The canonical identity bridge already exists through official runtime registration projection:

`RuntimeCapabilityRegistration.descriptor.name`
`→ RuntimeCapabilityRequirement.capability_id`
`→ RuntimeCapabilityGraph`
`→ RuntimeCapabilityReadiness.capability_id`.

S5-A MUST NOT create an identity mapper or infer cross-model identity by fuzzy, semantic, embedding, retrieval, substring, or LLM matching.

The canonical graph is owned by `OfficialROBYRuntime.capability_graph`. S5-A MUST NOT reconstruct a graph from the capability registry or runtime registrations.

Runtime readiness semantics remain owned by the existing runtime-readiness service and its canonical products.

## 4. Required readiness-projection states

Every S4-Z observation MUST remain represented. For a `REGISTRY_AVAILABLE` C/D path, S5-A MUST distinguish:

- `READINESS_NOT_PROVISIONED`: the canonical runtime has no provisioned `capability_graph`.
- `READINESS_NOT_DECLARED`: the canonical graph exists, but exact canonical C has no node/readiness declaration in that graph.
- `UNKNOWN`: canonical readiness evidence for C exists and reports `RuntimeCapabilityAvailability.UNKNOWN`.
- `AVAILABLE`: canonical readiness evidence for C exists and reports `RuntimeCapabilityAvailability.AVAILABLE`.
- `DEGRADED`: canonical readiness evidence for C exists and reports `RuntimeCapabilityAvailability.DEGRADED`.
- `UNAVAILABLE`: canonical readiness evidence for C exists and reports `RuntimeCapabilityAvailability.UNAVAILABLE`.

`READINESS_NOT_PROVISIONED`, `READINESS_NOT_DECLARED`, and `UNKNOWN` are distinct states.

For a S4-Z observation that is not `REGISTRY_AVAILABLE`, S5-A MUST preserve the observation and MUST NOT assign or infer runtime availability for that path.

## 5. Contract requirements

### R1 — Canonical runtime graph ownership

S5-A MUST obtain the runtime-readiness domain from the canonical `OfficialROBYRuntime.capability_graph`.

If that graph is `None`, every otherwise eligible `REGISTRY_AVAILABLE` path MUST remain preserved and report `READINESS_NOT_PROVISIONED`.

Graph absence MUST NOT be converted into `UNAVAILABLE`.

### R2 — Undeclared runtime readiness is explicit

If the canonical graph exists but exact canonical C is absent from that graph, the original C/D path MUST remain preserved and report `READINESS_NOT_DECLARED`.

A missing runtime node MUST NOT be converted into `UNKNOWN`, `UNAVAILABLE`, a synthetic empty dependency declaration, or a substitute capability.

`UNDECLARED != DECLARED EMPTY`.

### R3 — Canonical UNKNOWN remains UNKNOWN

If canonical runtime-readiness evidence exists for C and reports `RuntimeCapabilityAvailability.UNKNOWN`, S5-A MUST preserve that exact semantic state as `UNKNOWN`.

`UNKNOWN != READINESS_NOT_DECLARED`.

### R4 — AVAILABLE / DEGRADED / UNAVAILABLE are preserved exactly

If canonical runtime-readiness evidence for C reports `AVAILABLE`, `DEGRADED`, or `UNAVAILABLE`, S5-A MUST preserve that exact availability state without reinterpretation.

In particular, `DEGRADED` MUST NOT be collapsed into `UNAVAILABLE` merely because warnings exist.

### R5 — Runtime readiness applies to C, not evidence output D

S5-A MUST preserve the original C/D binding and associate the canonical runtime-readiness observation of C with that path.

It MUST NOT claim that runtime readiness independently certifies D.

`RUNTIME_READINESS(C) != EVIDENCE_READINESS(D)`.

### R6 — Non-registry-available paths are preserved without promotion

S4-Z observations with `NOT_REGISTERED`, `EVIDENCE_DECLARATION_MISMATCH`, or `DISABLED` MUST remain auditable and unchanged.

S5-A MUST NOT use runtime evidence to repair, override, promote, or substitute those registry-scoped states.

### R7 — Complete lineage and canonical readiness evidence preservation

The S5-A result MUST preserve the complete S4-Z material anchor and every original S4-Z observation/binding.

Where canonical runtime readiness exists, the projection MUST preserve the canonical readiness evidence for C, including its availability, `ready`, `degraded`, blockers, warnings, resident requirements, and description, without mutating that evidence.

Representation MUST be deterministic and preserve S4-Z ordering.

### R8 — Read-only, derivational, non-selective boundary

The S5-A projector MUST be `read_only=True` and `derivational=True`.

It MUST NOT:

- mutate the capability registry or official runtime;
- create or reconstruct a runtime capability graph;
- create dependency declarations;
- create a second runtime-readiness authority;
- use `JsonCapabilityModel` as a parallel readiness authority;
- perform semantic/fuzzy capability matching;
- discover substitute resolution paths;
- filter unavailable or undeclared paths from the result;
- rank sources or capabilities;
- select sources or capabilities;
- plan or authorize acquisition;
- acquire evidence;
- create questions;
- assign question-worthiness;
- assign relevance;
- invoke curiosity;
- create goals;
- invoke initiative;
- invoke conversation;
- persist results;
- modify memory;
- create learning candidates;
- execute actions;
- grant authority;
- claim subjective experience or consciousness.

Zero, one, or many runtime-ready paths remain observational only. One `AVAILABLE` path does NOT mean selected path.

## 6. Canonical evidence acquisition rule

S5-A MUST reuse the runtime-owned canonical graph and the existing runtime-readiness evaluation path. It MUST NOT reproduce readiness rules for lifecycle, supervisor, residents, capability dependencies, blockers, warnings, or degradation.

A readiness report supplied without sufficient canonical runtime/graph lineage MUST NOT be treated as canonical merely because it contains a matching capability identifier.

## 7. Semantic boundaries

The following distinctions are contractual:

`REGISTRY_AVAILABLE != RUNTIME_AVAILABLE`

`READINESS_NOT_PROVISIONED != UNAVAILABLE`

`READINESS_NOT_DECLARED != UNAVAILABLE`

`UNKNOWN != READINESS_NOT_DECLARED`

`AVAILABLE != SELECTED`

`DEGRADED != UNAVAILABLE`

`READY != AUTHORIZED != SELECTED`

`RUNTIME_READINESS(C) != EVIDENCE_READINESS(D)`

## 8. STOP boundary

The block ends after preserving every S4-Z path and, only where legitimate, associating the canonical runtime-readiness observation of C.

`MATERIAL PATH SET`
`→ CURRENT REGISTRY AVAILABILITY`
`→ CANONICAL RUNTIME READINESS PROJECTION`
`→ STOP`

No progression is authorized to:

`SOURCE SELECTION → NEED-TO-ASK / QUESTION-WORTHINESS → RELEVANCE → CURIOSITY`.

## 9. RED-test target after owner certification

After this contractual document is owner-certified, RED tests should require one minimal subordinate projection seam only, expected conceptually under:

`core.cognitive_maturity.canonical_runtime_readiness_projection`

The RED tests MUST fail exclusively because that projection seam is absent. They MUST NOT require changes to S4-Z, S4-W, S4-T, `OfficialRuntimeCapabilityRegistry`, `RuntimeCapabilityGraph`, `OfficialROBYRuntime`, `RuntimeHealthReadinessService`, source selection, planning, authorization, or conversational authorities.

No productive implementation is authorized by this RED contractual step.
