# Post-M409.1 — Hypothesis Deepening Epistemic Gap → Governed Curiosity Productive Consumption v1

## Status

IMPLEMENTED — pending official full-suite validation and certification.

## Purpose

Connect certified `HypothesisEpistemicGap` evidence to the existing governed Curiosity,
Relevance and Personal Initiative capabilities without creating a new authority.

## Productive path

`HypothesisEpistemicGap`
→ `HypothesisGapCuriosityEvidenceAdapter`
→ existing `RelevanceEvaluator`
→ explicit `EpistemicCuriosityRelevance`
→ existing `GovernedEpistemicCuriosityFoundation`
→ existing `GovernedEpistemicCuriosityConsumptionFoundation`
→ existing `PersonalInitiativeEngine`.

This increment ends at governed Curiosity consumption. It does not emit conversation,
write memory, learn, persist a gap, modify knowledge, or execute an action.

## Fail-closed behavior

- Missing relevance candidate keeps evidence at `UNKNOWN`; Curiosity returns `ABSTAIN`.
- Existing relevance rejection maps to `NOT_RELEVANT`; Curiosity produces no question.
- Existing relevance admission maps to `RELEVANT`; only Curiosity may create the question candidate.
- Existing Personal Initiative may still defer or discard delivery after question admission.
- Relevance candidate identity must preserve the exact hypothesis-gap subject.

## Authority preservation

- `governed_reasoning` remains owner of hypothesis deepening and epistemic gaps.
- The gap adapter remains a pure projection and never decides relevance.
- `RelevanceEvaluator` remains the existing relevance authority under the official conversation boundary.
- `GovernedEpistemicCuriosityFoundation` remains the only Curiosity question-candidacy logic.
- `PersonalInitiativeEngine` remains the existing initiative planner.
- No `CuriosityAuthority`, second reasoner, gateway, store, worker, scheduler, memory writer or background process is introduced.

## Explicit exclusions

No `OfficialConversationGateway` emission is added in this increment. No M369 learning,
`OfficialMemoryGateway`, M410, networking or Residential behavior is opened.
