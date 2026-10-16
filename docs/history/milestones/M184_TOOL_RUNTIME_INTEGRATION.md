# M184 — Tool Runtime Integration

## Objective

Integrate ROBY's existing governed tool gateway into the official local operational runtime while preserving local-first execution, explicit permission boundaries, exact composition ownership, and turn-level audit lineage.

## Scope

M184 adds:

- an explicit tool runtime integration port consumed by M178 turn preparation;
- deterministic explicit local commands using `/tool <capability> <json-object>`;
- execution exclusively through the existing M61 `ToolGatewayManager`;
- capability registration, enablement, consent, handler isolation, and audit reuse;
- tool output injection into the provider request as governed turn evidence;
- immutable runtime invocation/context models and per-process history;
- fail-closed handling for unknown, disabled, unavailable, or failing tools;
- preventive blocking of capabilities marked as platform-mutating.

## Runtime sequence

1. The composition root builds the graph without observing or executing tools.
2. M177 preparation builds the normal inference request and applies M183 memory context when configured.
3. M184 inspects the turn for the explicit `/tool` command boundary.
4. Non-tool turns are observed by M61 but never dispatched.
5. Tool turns are normalized into a deterministic invocation and routed through M61.
6. M61 applies registration, enablement, consent, and handler governance.
7. Successful read-only output is appended to the LLM request as structured evidence.
8. The local provider continues through the existing governed M177 pipeline.

## Governance and safety

The console and parser do not own routing authority. Tool handlers are never called directly by the operational runtime. Unknown capabilities fail closed. Handler exceptions are reduced to their exception class and do not leak internal messages. Capabilities declaring write or mutation side effects are blocked before dispatch because M177's operational contract forbids platform mutation.

## Command contract

```text
/tool weather.current {"city":"Buenos Aires"}
```

The payload is optional and defaults to `{}`. When present, it must be a JSON object and respect the configured size limit.

## Exclusions

M184 does not add autonomous tool selection, natural-language argument synthesis, write-capable tools, background execution, tool-result persistence, remote adapters, or a new permission system. Long-lived lifecycle integration remains M185.
