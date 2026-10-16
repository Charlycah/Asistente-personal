# M83 — Explainable Answers

## Objective

Transform immutable M82 Decision Records into clear, deterministic and verifiable public explanations while preserving source traceability, uncertainty, governance boundaries and the separation between facts and inferences.

## Delivered

- `ExplanationLevel`: concise, standard and audit.
- `ExplanationSectionType` and immutable `ExplanationSection`.
- `CitationKind` and immutable `SourceCitation`.
- immutable `ExplainableAnswer` with stable SHA-256 identity.
- `ExplanationRequest`.
- `ExplainableAnswerRenderer`.
- `ReasoningExplanationManager`.
- public `to_dict()` and plain-text rendering.
- confidence bands from insufficient through very high.
- explicit rendering of conclusions, abstentions, blocks and review requirements.
- separate factual-basis and inference sections.
- evidence fingerprints, claim revisions, rule versions and conflict citations.
- visible limitations, assumptions and human-review history.
- deterministic citation limits and ordering.

## Invariants

- Explanations are generated only from an immutable Decision Record.
- No citation is invented or detached from the record.
- Rule-derived results remain explicitly separate from confirmed facts.
- Abstention and blocked outcomes are never presented as successful conclusions.
- Human-review requirements are always visible.
- Audit output references source identities and versions without copying documents.
- Rendering is deterministic and does not store or expose unrestricted chain-of-thought.
- M83 does not execute actions or modify M77–M82 state.

## Deferred

- Full orchestration and Cognitive Pipeline integration: M84.
- Localization and UI-specific renderers.
- Optional source excerpt resolution through governed adapters.
