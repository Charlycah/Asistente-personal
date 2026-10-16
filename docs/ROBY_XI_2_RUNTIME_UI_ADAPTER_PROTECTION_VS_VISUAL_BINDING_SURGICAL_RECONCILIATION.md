# ROBY XI.2 — Runtime UI Adapter Protection vs Visual Binding
## SURGICAL RECONCILIATION

## Certified input

The input is the Owner-certified blocked GREEN reconciliation:

- 10 intentional RED failures;
- 13,494 passes;
- Ruff clean;
- productive delta zero;
- `runtime_ui_adapter.py` byte identity preserved.

## Question

Does the visual root binding require governed evolution of the protected
`runtime_ui_adapter.py`, or can the residual be closed additively outside it?

## Historical protection evidence

The protected adapter SHA is:

`2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1`

Three active architecture contracts still assert that exact identity.

### S1-C proposal review guard

Its own contract states that proposal review must be composed outside both
protected conversational surfaces.

It explicitly requires a bounded exterior desktop composition seam and says
that the protected UI adapter must not own proposal-review semantics or state.

Therefore its byte guard is architectural placement evidence, not merely an
obsolete snapshot.

### Adaptive delivery tone guard

It explicitly asserts that the local adapter remains byte-identical while the
desktop controller forwards the exact canonical delivery tone to the existing
voice reader.

It also forbids the desktop from owning or recomputing adaptive personality.

Again, the intended pattern is exterior reachability around the protected
adapter.

### Documentary current-truth precedence guard

This contract protects a set of productive surfaces and documentary
authorities together.

Its purpose is documentary precedence and historical current-truth
reconciliation. It does not define a new visual extension seam.

Nevertheless its byte guard is still active and cannot be silently replaced.

## Existing additive visual surfaces

The repository already contains certified additive components:

- `SameTurnGovernedVisualResult`;
- `SameTurnVisualRuntimeComposition`;
- `SameTurnVisualUIAdapterComposition`;
- `AppliedConversationalIntelligenceOwnerTurnComposition`;
- `bind_applied_result_to_desktop`;
- `present_desktop_runtime_visuals`;
- `dispatch_desktop_runtime_visual_render`;
- external-image presenter and dispatcher contracts.

No new visual manager, agent, planner, executor or cognitive authority is
needed.

## Important lifecycle evolution already completed

The canonical `OfficialConversationGateway` now executes the applied branch
inside the owner-turn lifecycle and exposes the exact successful applied
result through `last_applied_owner_turn_result`.

`UnifiedBrain.process` already delegates one owner turn through the canonical
gateway and preserves explicit document, source, evidence and visual context.

Therefore the earlier same-turn composition design must not independently
execute an applied branch and then a fallback branch.

The correct present-day additive seam is a wrapper/delegation composition
around the protected UI adapter that:

1. delegates the owner turn exactly once through the existing adapter;
2. reads the exact gateway-owned applied result after that same execution;
3. returns the unchanged `UIResponse` plus that optional result;
4. preserves explicit current-turn context through the existing path;
5. introduces no new owner-turn or cognitive authority.

## Finding about the current RED

The Owner-certified RED correctly identified the productive visual residual,
but four assertions overconstrained its implementation location.

They require:

- `LocalConversationUIAdapter.submit_text_with_visual_companion`;
- direct one-brain execution inside that new adapter method;
- gateway-result reading inside that new adapter method;
- matching methods directly on protected runtime UI decorators.

Those requirements conflict with active historical placement protections.

The RED therefore captured the right behavior but the wrong mandatory
implementation surface.

This is not authorization to weaken the behavioral contract.

## Architectural decision

`runtime_ui_adapter.py` remains protected and byte-identical.

No Class-2 evolution of that adapter is justified by current evidence.

The visual binding must use additive exterior composition/delegation and
reuse the already-certified visual transport/runtime/presentation surfaces.

The current RED must be surgically repaired before GREEN.

The repair must replace implementation-location assertions with behavioral
obligations proving:

- one desktop owner action causes one canonical owner-turn execution;
- the exact gateway-owned applied result is exposed after that execution;
- explicit document/source/evidence/visual context remains preserved;
- ordinary non-applied turns preserve the existing text path;
- existing proposal review, source constraint, service guard and personality
  behavior remain composed without moving their authorities;
- the existing Tk worker and `root.after` boundary remain unique;
- existing external-image presentation and UI dispatch are reused;
- presentation failure never re-executes the owner turn.

## Out of scope

Still separate:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

No new recognition or latest-result ordering is authorized.

## Status

`SURGICAL_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`

`DECISION: PRESERVE PROTECTED RUNTIME_UI_ADAPTER`

`REQUIRED PATTERN: ADDITIVE EXTERIOR COMPOSITION`

`CURRENT RED: BEHAVIORALLY VALID / IMPLEMENTATION-LOCATION OVERCONSTRAINED`

`NEXT STEP: CONTRACT RED SURGICAL REPAIR`

`PRODUCTIVE PYTHON DELTA: ZERO`

`TEST PYTHON DELTA: ZERO`

`NEW AUTHORITY: NONE`

STOP before RED repair.
