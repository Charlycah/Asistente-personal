# ADR-142 — Presence Situation Assessment

## Status
Accepted.

## Context
M139 provides governed anonymous event semantics. ROBY now needs a downstream boundary that assesses those semantics as an ambient situation without recomputing continuity, redetecting change, reinterpreting meaning, identifying people, inferring activities, or deciding a response.

## Decision
Introduce `core.presence_situation_assessment` as M140.

M140 consumes only governed M139 results and maps the latest valid interpretation to one of four situational classes:

- stable;
- transition;
- uncertain;
- interrupted.

The assessment preserves the source interpretation, semantic meaning, presence states, confidence, owner, and ambient-context lineage. Stable no-event interpretations are represented explicitly and suppressed. Non-actionable, stale, future, weak, excessive, mismatched-owner, or mixed-lineage inputs are reviewed or blocked deterministically.

## Boundaries
M140 does not perform observation resolution, presence understanding, continuity evaluation, change detection, event interpretation, identity inference, biometrics, precise counting, activity or intent inference, individual or movement tracking, response decisions, sensor access, provider access, platform mutation, or automation.

## Consequences
The Ambient Context chain gains a pure situational-assessment layer while preserving strict responsibility boundaries and preparing a later integration milestone without coupling assessment to action.
