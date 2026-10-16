# M172 - ROBY Console Application

## Purpose

Provide the first interactive application boundary that can run a governed ROBY
conversation session from console input.

## Operational path

For each accepted turn, M172 preserves the exact M162 readiness lineage and
invokes:

1. M163 Conversation Entry Point;
2. M164 Natural Greeting Response when the entry is a greeting;
3. M165 ROBY Voice and Style Policy before console delivery.

Questions, requests, comments, attention and continuation entries remain
classified but return an explicit `await_pipeline` outcome. M172 does not invent
answers or bypass the architecture.

## Session behavior

- Ready and degraded runtimes may open a console session.
- Blocked readiness produces a single governed notice without reading input.
- EOF and configured exit commands close the session deterministically.
- Turn count is bounded by configuration.
- Session and turn records are immutable and append-only.
- Repeated greeting context is forwarded to M164.

## Governance boundary

The core depends only on the injected `ConsoleIO` protocol. Terminal calls are
implemented by `interfaces.cli.roby_console.StandardConsoleIO`. No provider call,
network access or platform mutation is performed by M172.

## Validation

- Exact M162 readiness lineage.
- Real M163 -> M164 -> M165 greeting flow.
- No fabricated response for unconnected routes.
- Bounded loop, exit and EOF behavior.
- Deterministic sequence and immutable records.
- Blocked readiness cannot consume console input.
- No import-time console side effects.
