# ADR-083 — Conflict and Uncertainty

## Status

Accepted.

## Context

M77 normalized evidence, M78 introduced claims, M79 assembled governed context and M80 added deterministic inference. The system now needs to detect incompatible claims and quantify uncertainty without silently choosing a preferred answer.

## Decision

Introduce a dedicated conflict and uncertainty layer with:

- immutable conflict records;
- deterministic conflict identifiers;
- explicit severity and resolution states;
- policy-driven precedence;
- mandatory human review for high-severity conflicts;
- confidence bounded by input confidence and unresolved conflict caps;
- no mutation of evidence, claims or inference results.

M81 detects active claims that share owner, subject and predicate but assert incompatible values. Stale and superseded claims are excluded from active conflict detection.

Resolution is conservative. Automatic resolution is allowed only when deterministic precedence distinguishes candidates. High-severity conflicts require human review. Unresolved conflicts cap confidence.

## Consequences

- Conflicts become first-class, auditable domain objects.
- Confidence is no longer a free scalar; it is accompanied by explicit factors.
- Inference outputs remain proposals and cannot override stronger source-backed claims silently.
- Decision persistence and user-facing explanations remain deferred to M82 and M83.
