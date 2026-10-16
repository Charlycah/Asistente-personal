# Post-M409.1 — Governed Hypothesis Epistemic Delta Foundation v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Describe the structural epistemic delta between two already-governed Hypothesis Deepening
reports using explicit triggering evidence. The Foundation does not create or revise the
AFTER reasoning state.

## Inputs
- BEFORE: `GovernedHypothesisDeepeningReport`.
- TRIGGER: `GovernedHypothesisDeltaTrigger` with explicit evidence references and provenance.
- AFTER: `GovernedHypothesisDeepeningReport`.

The BEFORE and AFTER reports must preserve the same source kind/reference. The trigger must
identify the AFTER snapshot. BEFORE and AFTER snapshots may differ and remain explicit.

## Delta semantics
Per-hypothesis structural outcomes are `UNCHANGED`, `EVIDENCE_CHANGED`, `RELATION_CHANGED`,
`RELATION_AND_EVIDENCE_CHANGED`, `NEW_HYPOTHESIS`, `MISSING_FROM_AFTER`, and
`PROPOSITION_CONFLICT`.

`MISSING_FROM_AFTER` and `PROPOSITION_CONFLICT` require review. Missing does not mean false or
deleted. Removed evidence references remain descriptive and are never treated as revocation.

## Authority
Canonical authority remains `governed_reasoning`. The delta is read-only and consultative.
It does not establish truth/falsity, modify hypotheses, invent confidence/probabilities,
persist results, create Memory/Learning, invoke Reasoning, Curiosity, Planning or capabilities,
modify the world model, grant authority, or start background processing.

## Deferred semantics
`STRENGTHENED` / `WEAKENED` interpretation is deliberately outside Foundation v1. A later
governed checkpoint may define semantic transitions only after the structural delta is
certified.

## Validation
Architecture/semantic tests cover unchanged state, evidence-only change, relation-only change,
combined change, new hypothesis, missing hypothesis review, proposition conflict, explicit
source/snapshot lineage, source review propagation, deterministic output, and governed
non-authoritative defaults.
