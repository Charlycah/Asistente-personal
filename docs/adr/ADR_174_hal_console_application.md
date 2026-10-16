# ADR-174: ROBY Console Application

## Status

Accepted.

## Context

M162 through M171 established readiness, conversation entry, greeting realization,
voice policy, provider governance and knowledge retrieval boundaries. ROBY still
needed a concrete application edge capable of accepting human input and invoking
those boundaries without moving terminal concerns into the core.

## Decision

Introduce `ROBYConsoleApplication` as a governed application service with an
injected `ConsoleIO` port. The application:

- requires an existing M162 readiness result;
- opens only for ready or degraded runtimes;
- classifies every turn through M163;
- realizes greetings through M164 and M165;
- retains unsupported questions, requests and dialogue routes as explicit
  pending-pipeline outcomes;
- recognizes bounded exit commands;
- records immutable session and turn lineage;
- performs no provider, network or platform side effects.

A minimal `StandardConsoleIO` terminal adapter lives outside the core.

## Consequences

ROBY now has a testable interactive application boundary. This milestone does not
pretend that the general reasoning pipeline is connected: only the already
operational greeting path can produce a natural response. Later milestones may
replace pending outcomes with governed reasoning and response orchestration.
