# ADR-176 — External Retrieval Execution

## Status
Accepted for M174.

## Context
M169 selects governed knowledge sources, M170 creates deterministic retrieval plans, and M171 executes those plans through injected retriever ports. External sources still require a concrete execution boundary that can perform network retrieval without allowing inference-provider calls, platform mutation, implicit source substitution, or unvalidated evidence.

## Decision
Introduce `ExternalRetrievalExecutionAdapter` as the M174 boundary for official documentation, web, news, and API retrieval.

The adapter:

- implements the M171 `KnowledgeRetriever` port;
- accepts only external `KnowledgeRetrievalStep` instances;
- resolves source-specific clients through injection;
- validates source and query lineage;
- applies query, content, reference-count, and HTTPS-reference constraints;
- records immutable execution outcomes;
- contains client exceptions as governed failures;
- never calls inference providers or mutates the platform.

M171 remains the authority that must explicitly permit network execution.

## Consequences
External retrieval becomes executable and testable while preserving the policy and orchestration boundaries established in M169–M171. Concrete HTTP/search/news/API clients remain replaceable infrastructure adapters.
