# Post-M409.1 — Explicit Deliberation Decision Option Adapter v1

## Purpose

This increment adds a subordinate, deterministic, read-only adapter from certified
`ExplicitDecisionDeliberationEvidence(EXPLICIT)` into M391.6
`GovernedDecisionOption` inputs. It does not call M391.6 and does not enter runtime wiring.

## Contract

Each explicit source alternative maps one-to-one to one `GovernedDecisionOption` and one
read-only provenance binding. The option title is the producer's `normalized_text`.
Identity is an opaque SHA-256 value derived from the versioned adapter namespace, the
source evidence fingerprint and the alternative ordinal.

The evidence remains the canonical conversational provenance. The binding preserves only
the option id, source fingerprint, ordinal and exact source offsets. No span metadata is
inserted into M391.6 fields with unrelated semantics.

All optional decision-evidence links remain neutral in v1:

- `organization_item_id=None`
- `scenario_hypothesis_id=None`
- `causal_relation_id=None`
- `explicit_preference=0.0`

## Governed limits

The adapter:

- does not parse or re-read natural language;
- does not generate, drop, rank or rewrite alternatives;
- does not infer preference;
- does not link M391.5, scenarios or causal evidence;
- does not call `CanonicalDecisionFacade` or `GovernedDecisionAdvisor`;
- does not persist state or start background work;
- does not execute actions or grant authority;
- does not modify Producer v1, Foundation v1 or M391.6;
- does not add runtime wiring, Initiative, Proactive Care, Residential or M410 networking.

Non-`EXPLICIT` evidence is rejected fail-closed.

## Validation state

Implementation includes focused architecture tests. M361 is synchronized by the official
generator. Final closure requires clean `ruff check .` and full `pytest -q` on the private
validated tree.
