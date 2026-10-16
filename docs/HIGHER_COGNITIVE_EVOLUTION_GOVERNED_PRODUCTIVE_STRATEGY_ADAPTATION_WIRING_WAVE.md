# ROBY XI.2 — Higher Cognitive Evolution
## Governed Productive Strategy Adaptation Wiring Wave

**Baseline de entrada:** 13.399 tests PASS + Ruff limpio.  
**Estado:** CLOSED / PROMOTED — full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.

## Purpose

Move the recently certified strategy-adaptation contracts into ROBY's ordinary productive cognitive
preparation path without creating a second planner, coordinator or cognitive runtime.

## Productive path closed

The official runtime now injects the **same** `UnifiedCognitiveCoordinator` instance that is already
registered as `cognition.unified_coordination_runtime` into `RuntimeCompositionDependencies` as the
strategy authority used by preparation.

For an ordinary provider-bound turn:

`OfficialConversationGateway`
→ `GovernedOperationalConversationPipeline`
→ `GovernedRuntimePreparation`
→ existing `UnifiedCognitiveCoordinator`
→ planner-derived `CognitiveStrategyCandidate`
→ `GovernedCognitiveStrategyApplication`
→ existing `CognitiveRuntimeOrchestrator`
→ `CognitiveStrategyApplicationEvidence`
→ normal provider preparation continues.

No HCE-specific branch is added to `OfficialConversationGateway`.

## Same authority / same runtime

`runtime_root_factory.py` creates one `UnifiedCognitiveCoordinator`.

That exact object is:

- registered in the official capability registry;
- injected into the official runtime composition dependencies;
- used by `GovernedRuntimePreparation` to prepare strategy application.

No duplicate coordinator is instantiated.

The existing `CognitiveRuntimeOrchestrator` remains the only runtime authority for cognitive
contributors.

## Ordinary-turn behavior

A multi-step cognitive request may now receive a bounded strategy application automatically during
normal preparation.

A single-need/non-strategic turn returns no strategy application and preserves the historical
runtime behavior.

Strategy application does not alter provider routing, execute registry capabilities, authorize
external tools, persist data, create Memory or create Learning.

## Turn evidence

`GovernedConversationPreparation` now preserves the exact
`CognitiveStrategyApplicationEvidence` produced by the cognitive runtime.

This keeps the strategy instance lineage available to the rest of the productive turn without
creating a repository.

## Transient metacognitive history seam

`UnifiedCognitiveCoordinator` may retain, only for the lifetime of the runtime process:

- strategy instances it productively prepared;
- already-certified `GovernedStrategyOutcomeObservation` values explicitly supplied to it.

It does **not** fabricate outcome evidence.

`observe_productive_strategy_outcome(...)` rejects observations whose strategy instance was not
actually prepared by that coordinator.

When compatible certified observations are present, the existing metacognitive adaptation contract
may influence a later current-eligible strategy structure. Otherwise the ordinary baseline strategy
is used with no influence.

This transient history is not Memory, Learning or a durable preference store.

## Important remaining epistemic boundary

The productive cognitive runtime currently provides exact strategy application evidence, but this
wave does not invent a `GovernedReasoningMethodOutcomeObservation` from provider success, response
text, contributor completion or confidence alone.

Therefore automatic strategy-outcome learning remains fail-closed until an existing certified
reasoning-outcome producer supplies the exact governed observation required by the already-promoted
metacognitive contract.

This is intentional: productive reachability is closed without weakening causal attribution.

## Validation

New productive wiring contract: **5 PASS**.

Focused matrix across:

- productive runtime composition;
- official runtime factory;
- cognitive runtime orchestration;
- Novel Strategy Synthesis;
- Strategy Application Outcome Evidence;
- Strategy Outcome → Metacognitive Adaptation;
- Strategy Structural Identity & Future Influence;

resulted in **97 PASS**.

`py_compile` and line-length checks are clean in the modified Python files.
Full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.

## Architecture decision

No `AdaptiveStrategyRuntime`, `MetaPlanner`, `StrategyPreferenceRepository`, second coordinator,
second CognitiveRuntimeOrchestrator, second Memory or second Learning writer was introduced.

The productive adaptation seam now exists under the same governed authorities; uncertified outcome
attribution remains blocked by design.
