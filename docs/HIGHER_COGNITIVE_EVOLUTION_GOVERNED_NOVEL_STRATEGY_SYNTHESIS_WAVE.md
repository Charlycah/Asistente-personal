# ROBY XI.2 — Higher Cognitive Evolution
## Adaptive Cognitive Composition — Governed Novel Strategy Synthesis Wave

**Baseline de entrada:** 13.357 tests PASS + Ruff limpio.
**Estado:** CLOSED / PROMOTED — full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.

## Purpose

Add the first bounded strategy-synthesis representation without creating a new planner,
orchestrator, persistence layer or execution authority.

The existing `CognitivePlanner` remains responsible for detecting cognitive needs and tool
requirements. The existing `UnifiedCognitiveCoordinator` remains the Decision/composition
authority and may now produce a read-only `CognitiveStrategyCandidate`.

## Causal contract

`novel problem text`
→ `CognitivePlanner required tools + cognitive needs`
→ `existing capabilities only`
→ `generic cognitive dependency ordering`
→ `CognitiveStrategyCandidate READY or BLOCKED`.

The strategy is advisory only. It never executes capabilities.

## Dependency rules

- evidence acquisition (`memory`, `weather`, `calendar`, `current_affairs`) precedes analysis;
- `reasoning` depends on relevant evidence;
- `planning` may depend on prior evidence/reasoning;
- `decision` depends on prior evidence/reasoning;
- `reflection` reviews prior analytical/decision steps;
- `coordination` depends on prior cognitive work.

These rules are generic cognitive dependencies, not prompt-specific workflows and not `_SCENARIOS`.

## Fail-closed boundaries

If a required selected capability is unavailable, the candidate is `BLOCKED` and exposes no
step list that could be mistaken for an execution plan.

The candidate:

- is advisory-only;
- does not execute;
- does not persist;
- does not learn;
- does not modify Memory;
- grants no authority.

## Novelty / recomposition evidence

The certification proves:

- multi-step strategy synthesis from a non-scenario request;
- evidence-before-reasoning-before-decision dependencies;
- changed relevance removes Weather and changes the strategy fingerprint;
- missing required capability blocks rather than silently degrading;
- irrelevant available capabilities are not added;
- reasonable paraphrases preserve strategy structure;
- different problems produce different compositions;
- a single cognitive need does not fake a multi-step strategy;
- owner/scope/provenance are preserved.

## Architecture

No `StrategyManager`, `ImprovisationEngine`, second planner, second orchestrator, new registry,
scheduler or persistence store was introduced.

This wave does not yet learn strategies from outcomes. That belongs to a later metacognitive
strategy-adaptation contract.
