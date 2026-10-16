# M187 — Local Provider Runtime Adapter

M187 introduces ROBY's first production-oriented local LLM boundary. The adapter
implements the existing `LLMProvider` contract and speaks the OpenAI-compatible
HTTP API exposed by Ollama, LM Studio and llama.cpp servers.

## Scope

- local-only endpoint configuration;
- `GET /v1/models` health observation;
- `POST /v1/chat/completions` inference;
- bounded health and generation timeouts;
- normalized `LLMResponse` failures;
- configurable model, system prompt, token limit and temperature;
- cooperative cancellation before and after transport execution;
- API key kept in request headers and never written to response metadata;
- environment-driven provider construction.

M187 does not select a model autonomously, start a model server, fall back to a
remote provider, or expose chain-of-thought. Provider routing and execution
remain governed by the existing M166–M177 contracts.

## Local examples

Ollama OpenAI compatibility commonly uses:

```text
ROBY_LOCAL_PROVIDER_ENDPOINT=http://127.0.0.1:11434/v1
ROBY_LOCAL_PROVIDER_MODEL=<installed-model-name>
```

LM Studio commonly uses:

```text
ROBY_LOCAL_PROVIDER_ENDPOINT=http://127.0.0.1:1234/v1
ROBY_LOCAL_PROVIDER_MODEL=<loaded-model-name>
```

The model server must be started separately. ROBY never starts or installs it.
