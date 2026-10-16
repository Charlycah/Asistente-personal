# M174 — External Retrieval Execution

## Objective
Provide ROBY with the first governed network knowledge-retrieval boundary downstream from M171.

## Delivered

- `ExternalRetrievalExecutionAdapter` implementing the M171 retriever port.
- External source support for official documentation, web, news, and APIs.
- Source-specific injected client registry.
- Immutable request, client-result, execution-result, and repository models.
- Query, content, reference-count, and HTTPS validation.
- Explicit handling for disabled, unsupported, unregistered, rejected, and failed retrievals.
- Preservation of exact M170 step lineage.
- Integration tests proving M171 still blocks network access by default.

## Architectural boundary
M174 performs retrieval only. It does not:

- choose knowledge sources;
- build retrieval plans;
- authorize network access globally;
- invoke an LLM provider;
- synthesize a final answer;
- mutate platform state.

## Validation

- Ruff clean.
- 36 focused M174 tests passing.
- Full repository suite passing without regressions.
