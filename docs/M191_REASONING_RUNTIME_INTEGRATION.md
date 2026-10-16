# M191 — Reasoning Runtime Integration

M191 connects the existing governed reasoning architecture to the official
cognitive runtime introduced in M189.

## Operational flow

A `GovernedReasoningSource` resolves an already governed reasoning result for
one user turn. `ReasoningRuntimeContributor` projects only publishable context
into the provider request:

- governed conclusion;
- confidence and explainable summary;
- limitations and assumptions;
- exact lineage references kept outside the prompt.

Blocked and review-required results are skipped. Abstention is preserved as an
explicit caution instruction and never converted into an invented conclusion.

## Composition

The official cognitive contributor order is:

1. living conversation;
2. governed reasoning;
3. additional configured cognitive contributors.

The integration cannot execute tools, mutate memory, call a provider, or bypass
existing governance.
