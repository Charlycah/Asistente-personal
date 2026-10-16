# M173 - Local Provider Execution Adapter

## Purpose

Execute a provider call only when M168 has declared a valid local route, while
preserving route lineage and local-first governance.

## Operational path

1. Receive the exact `GovernedProviderRoute` from M168.
2. Verify that execution was requested and enabled.
3. Require an active local route with a selected local provider.
4. Resolve the provider through an injected `LLMProvider` port.
5. Force the routed model into the inference request.
6. Execute and validate the normalized `LLMResponse`.
7. Publish an immutable execution result.

## Outcomes

- `completed`: accepted local inference with matching provider and model.
- `rejected`: provider output violates response lineage or content limits.
- `failed`: provider rejects, raises, or returns an invalid response type.
- `withheld`: route, registration, permissions, prompt, or model request is invalid.
- `not_applicable`: execution was not requested.

## Governance boundary

- Local routes only.
- No remote fallback.
- No external network authorization.
- No platform mutation.
- No provider discovery outside injected ports.
- Exact M168 route lineage is retained.

## Validation

- 32 focused tests.
- Ruff clean.
- Complete suite passing with no regressions.
