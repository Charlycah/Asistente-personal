# RC-1.1 — Governed Recalled Knowledge Structural Projection v1

## Purpose

RC-1.1 connects existing cognitive-memory recall with RC-1 structural transfer
without giving memory retrieval semantic, inference, learning, or action
authority.

The bounded flow is:

`CognitiveMemoryRecall -> governed structural projection -> RC-1 matcher -> STOP`

## Authority boundaries

- `CognitiveMemoryRecall` remains the relevance/retrieval authority.
- `GovernedContextualRuleInterpretationProducer` remains bounded rule
  interpretation authority.
- `GovernedBoundedSemanticRoleRelationGrounder` remains semantic grounding
  authority.
- `GovernedStructuralKnowledgeTransferMatcher` remains structural compatibility
  authority.
- No inference rule is registered and no inference is authorized by RC-1.1.

## Projection contract

`GovernedRecalledKnowledgeStructuralProjector` consumes an already-produced
`CognitiveMemoryRecallResult`. It never queries the memory store itself.

At most the first five recalled items are considered. For each item the
projector:

1. preserves `memory_id`, recall score, memory confidence, category, and a
   SHA-256 content fingerprint;
2. passes the memory content through the existing bounded rule interpreter;
3. passes only valid rule candidates through the existing semantic grounder;
4. compiles the certified grounding through the existing contextual rule compiler;
5. exposes the structural grounding together with that certified ephemeral
   compilation only when both stages succeed.

Relevant but non-structural memories are rejected as unsupported. Ambiguous
memories expose no partial grounding.

## Outcomes

- `PROJECTED`: one or more certified recalled structures are available.
- `UNSUPPORTED`: recalled memories were relevant but none was structurally
  certifiable.
- `AMBIGUOUS`: no structure is exposed because semantic projection was
  ambiguous.
- `INSUFFICIENT`: recall supplied no usable memory candidates.

Mixed batches may project certified items while recording unsupported or
ambiguous memory ids separately.

## Provenance

Each projected item preserves:

- cognitive memory id;
- memory content fingerprint;
- memory confidence;
- recall score;
- memory category;
- semantic grounding fingerprint;
- grounding-compilation fingerprint and instantiation spec;
- current scope.

The semantic grounding source reference is tied to the memory id and content
fingerprint.

## Governed limits

RC-1.1 is read-only and session-local. It does not:

- persist projection results;
- create or modify Memory;
- create or modify Learning;
- mutate the world model;
- establish truth;
- authorize inference;
- register rules;
- execute actions;
- grant authority;
- call providers;
- perform retrieval.

Memory retrieval remains upstream and separate.

## Explicit non-goals

RC-1.1 does not automatically apply recalled knowledge, select among ambiguous
structural matches, create generalized rules, add embeddings, perform semantic
search over all memory, or persist structural annotations back into memory.

Final repository closure requires `ruff check .` and full `pytest -q`.
