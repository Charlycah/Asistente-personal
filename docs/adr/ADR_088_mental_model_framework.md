# ADR-088 — Governed Mental Model Framework

## Status

Accepted for M86.

## Context

ROBY already had transient mental state, working memory, episodic memory, domain memories and knowledge access. None represented a stable, revisable internal model of a subject while preserving the distinction between experience, interpretation and fact.

## Decision

Introduce governed mental models in `core.adaptive_cognition`. A model is an immutable revisioned aggregate identified by subject, kind, owner and Scope Guard domains. Its assertions carry confidence, lifecycle status and direct provenance references.

Episodes may produce update proposals, but cannot mutate models automatically. Low-confidence proposals require approval. Conflicting assertions are retained and marked disputed, placing the model in review-required state. Query is deterministic and owner/domain constrained.

## Consequences

- Stable internal representations remain distinct from episodic records and knowledge.
- Every accepted change has an immutable revision history.
- Contradictions are visible rather than overwritten.
- M87 and M88 can inspect model uncertainty and revision history.
- M89 may later govern promotion into knowledge without changing M86 contracts.
