# ADR-189 — Local Provider Runtime Adapter

## Decision

ROBY uses one OpenAI-compatible local HTTP adapter behind the existing
`LLMProvider` port. Provider-specific products remain deployment details.

## Consequences

- ROBY stays independent from Ollama, LM Studio and llama.cpp SDKs.
- Local provider failures are normalized at the boundary.
- Every network call has an explicit timeout.
- Health observation does not perform inference.
- No remote fallback is implicit.
