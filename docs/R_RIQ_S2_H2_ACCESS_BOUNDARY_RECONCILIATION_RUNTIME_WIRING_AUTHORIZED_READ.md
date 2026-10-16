# ROBY XI.2 — R-RIQ-S2-H2-ACCESS-BOUNDARY-RECONCILIATION

**Subtitle:** Runtime Wiring & Authorized Read Boundary (Static)

**Class:** Scientific research, static/documentary only. **Status:** CANDIDATE — OWNER APPROVAL PENDING. **STOP_PRODUCTIVE:** ACTIVE.

## 1. Mandate and evidence boundary

Determine where existing operational-result repositories are constructed and connected, and whether an already governed read boundary is demonstrated. No code edits, execution of ROBY, tests, instrumentation, repository duplication, or experimental runs. Source inspected: operative ZIP `ultima version corregida(9).zip`, paths under `ultima version corregida/`. Previously prepared H2 research acts inform terminology, but the observations below are grounded in the source files cited by path and line.

## 2. Static wiring evidence

1. `core/runtime_composition_root/root.py:543` constructs `assembler = OperationalResponseAssembler()` without supplying a repository. At lines 553–568, it constructs `GovernedOperationalConversationPipeline(... response_assembler=assembler, ...)`, without supplying a pipeline repository. At lines 569–579, it stores `response_assembler=assembler` and `conversation_pipeline=pipeline` in `RuntimeComposition`.
2. `core/operational_response_assembly/assembler.py:23–30`: optional `OperationalResponseRepository`; when omitted, `InMemoryOperationalResponseRepository()` is constructed. This repository is an instance attribute, `self.repository`.
3. `core/governed_operational_conversation_pipeline/pipeline.py:40–61`: optional `GovernedConversationPipelineRepository`; when omitted, `InMemoryGovernedConversationPipelineRepository()` is constructed and assigned to `self.repository`. The same pipeline retains `self.response_assembler`.
4. `core/governed_operational_conversation_pipeline/models.py:359–378`: pipeline repository protocol exposes `add`, `get`, `list_all`; in-memory implementation uses an instance dictionary and returns an immutable tuple of current values.
5. `core/operational_response_assembly/models.py:197–216`: response repository protocol similarly exposes `add`, `get`, `list_all`; in-memory implementation stores by response ID.
6. `core/governed_operational_conversation_pipeline/pipeline.py:63–66`: `last_result` uses the pipeline repository's `list_all()`; this is a programmatic read surface on the pipeline instance, not evidence of an external authorized read API.
7. `core/governed_operational_conversation_pipeline/pipeline.py:164–197`: regular processing constructs a `GovernedConversationPipelineResult` containing `operational_response`, then adds it to the pipeline repository. At lines 199–238, interception constructs an `OperationalResponse` directly and adds the containing result to the pipeline repository. At lines 240–273, inactive outcomes are also added to the pipeline repository. Accordingly, the assembler repository alone cannot be presumed exhaustive for all pipeline response paths.

## 3. Authority and access boundary

- **Confirmed statically:** internal programmatic repository reads exist; the runtime composition holds references to the assembler and pipeline; the pipeline result retains its operational response.
- **Conditional:** in-process code possessing the actual composed pipeline instance could read its current repository, subject to the instance being alive and populated. This is an architectural possibility, not a verified access route for a researcher.
- **Not demonstrated:** an already authorized external or research-facing read endpoint; explicit owner/session-scoped authorization on repository `get`/`list_all`; durable storage, restart survival, historical access, or availability of populated real-run instances to this study.
- **Security caveat:** protocol methods accept IDs or no arguments and do not themselves express owner/session authorization. This does not establish that the wider application lacks authorization; the surrounding call chain must be examined before drawing that conclusion.
- **Not demonstrated:** any universal causal linkage between the M389.8 epistemic sufficiency assessment and a final delivered response. The observed `response_id`/`result_id` relationship does not substitute for assessment-to-response correlation evidence.

## 4. Coverage and measurement implications

The pipeline repository is a better *candidate* for observation of its own paths than the assembler repository alone, because the pipeline writes regular, intercepted, and inactive outcomes. This does not establish global completeness for all ROBY outputs or guarantee a lawful read surface. If results are absent, unreachable, uncorrelated, or not independently adjudicated, classify them under the existing H2 measurement contract as missing or insufficient evidence; never convert missingness into an accuracy, abstention, or calibration result.

## 5. Determination

`RUNTIME_WIRING: CONFIRMED_STATICALLY`

`INTERNAL_REPOSITORY_READ: CONFIRMED_STATICALLY`

`PIPELINE_REPOSITORY_COVERAGE: CONDITIONAL_TO_THIS_PIPELINE`

`AUTHORIZED_RESEARCH_READ_BOUNDARY: NOT_DEMONSTRATED`

`REAL_RUNTIME_RESULT_ACCESS: NOT_DEMONSTRATED`

`DURABLE_RESULT_PERSISTENCE: NOT_DEMONSTRATED`

`EPISTEMIC_ASSESSMENT_TO_FINAL_RESPONSE_LINK: NOT_DEMONSTRATED`

`OBSERVATIONAL_EXECUTION_READINESS: NOT_READY`

`C0_C1: EXPERIMENT_NOT_ENABLED`

`NEW_PRODUCTIVE_RESIDUAL: NOT_DEMONSTRATED`

`STOP_PRODUCTIVE: ACTIVE`

## 6. Governed next gate

After local file/hash verification and explicit Owner approval, a strictly static **R-RIQ-S2-H2-READ-CALLER-TRACE — Existing Callers & Authorization Surface** may inspect actual consumers of `RuntimeComposition`, `conversation_pipeline.repository`, `last_result`, and the operational response repository, to determine whether a pre-existing governed read path is exposed. STOP before runtime execution, tests, instrumentation, or any RED/GREEN implementation. Do not reopen previously certified audits or introduce a parallel authority.

## 7. Evidence limitations

This is a static assessment of the operative ZIP, not a proof of live deployment wiring, repository population, permissions in a running process, or experimental outcome. No tests were executed. Owner approval of the preceding access-trace act is not inferred merely from authorization to start this phase.
