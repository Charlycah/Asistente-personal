# ADR-167 - ROBY Voice and Style Policy

## Decision

Introduce M165 as the deterministic policy layer that preserves ROBY's voice after
response generation. It centralizes conversational warmth, concise delivery,
accent-free visible Spanish, whitespace normalization, and rejection of
bureaucratic acknowledgement phrases.

## Boundaries

M165 consumes M164 output. It does not generate semantic content, call a model,
access the network, or mutate the platform. Provider-specific prompting remains
outside this module; every provider must pass through this policy before delivery.
