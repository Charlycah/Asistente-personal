# M177 — Governed Operational Conversation Pipeline

## Objective

Establish ROBY's first official operational conversation pipeline for non-greeting turns.

## Operational path

1. Normalize owner, session, and turn text into an immutable request.
2. Ask an injected preparation port for an already-governed provider route, inference request, and optional retrieval plan.
3. Execute the exact local route through M173.
4. Execute the exact retrieval plan through M171 when configured.
5. Assemble the final response through M175 without rewriting provider output.
6. Persist an immutable pipeline result with exact lineage and side-effect flags.

The `execute(owner, session_id, text)` method implements the operational pipeline contract already consumed by M176.

## Governance

- M177 does not classify intent, evaluate provider health, choose provider policy, select routes, or build retrieval plans.
- Those upstream decisions arrive through `GovernedConversationPreparationPort` and remain the responsibility of the M178 composition root and its collaborators.
- Only M173 may call the local provider.
- Only M171 may perform retrieval, subject to its independent permissions.
- Only M175 assembles the response.
- Exceptions are contained and converted to a governed non-deliverable response.
- M177 never mutates the platform.

## Delivered

- Immutable pipeline request, preparation, result, status, and configuration models.
- A preparation port separating orchestration from cognitive and policy decisions.
- Exact M173, M171, and M175 lineage preservation.
- Optional governed retrieval.
- Append-only in-memory result repository.
- Direct compatibility with M176 `OperationalDesktopPipeline`.

## Validation

- 27 focused M177 tests.
- 57 combined M176–M177 integration tests.
- Ruff clean.
- 4971 repository tests passing without regressions.
