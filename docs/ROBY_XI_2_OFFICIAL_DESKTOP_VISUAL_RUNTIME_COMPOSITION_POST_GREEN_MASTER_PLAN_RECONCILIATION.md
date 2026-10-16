# ROBY XI.2 — Official Desktop Visual Runtime Composition
## POST-GREEN Master Plan Reconciliation

## Owner-certified starting state

The Surgical GREEN is Owner-certified:

- 13,467 tests passed;
- 0 tests failed;
- Ruff clean.

Certified foundations to reuse:

- governed external-image projection;
- desktop external-image presenter;
- external-image presentation wiring;
- desktop visual companion;
- desktop visual runtime binding;
- same-turn governed visual-result exposure.

No productive code is added by this reconciliation.

## Productive-consumer audit

Repository search for:

- `SameTurnVisualRuntimeComposition`;
- `SameTurnVisualUIAdapterComposition`;
- `submit_with_visual_companion`;
- `expose_same_turn_governed_visual_result`;

shows no productive composition-root consumer of the new same-turn runtime/UI
compositions.

`submit_with_visual_companion` exists on the desktop controller, but the
desktop worker does not call it.

Therefore the GREEN is a certified foundation, not final desktop reachability.

## Current official desktop composition

`desktop_bootstrap.py` still constructs:

`LocalConversationUIAdapter(runtime)`
-> `GovernedProposalDesktopReviewComposition`
-> `EpisodicSourceConstraintDesktopComposition`
-> `OptionalServiceGuardUIAdapter`
-> `ConversationalPersonalityUIAdapter`
-> `ROBYDesktopApp`

No `SameTurnVisualRuntimeComposition` or
`SameTurnVisualUIAdapterComposition` is inserted into that chain.

The existing decorators remain governed behavior and must not be bypassed.

## Current worker path

The official desktop worker still calls:

`self.controller.submit(...)`

with document/source/evidence/visual-context arguments.

It then posts:

`root.after(0, lambda: finish_submit(messages))`

The worker does not call `submit_with_visual_companion`.

The finish path accepts only text `DesktopMessage` objects and appends them to
the transcript.

No governed external-image companion reaches Tk.

## Applied-execution audit

`OfficialConversationGateway.execute_applied_conversational_intelligence`
exists, but repository search still finds no productive caller.

The normal desktop owner-turn path remains separate.

Binding that method as a second call after `controller.submit` is forbidden.

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION`

remains mandatory.

## Preview/presenter audit

The following certified foundations exist:

- `BoundedExternalImagePreviewFetcher`;
- `DesktopExternalImagePresenter`;
- `present_desktop_runtime_visuals`;
- `dispatch_desktop_runtime_visual_render`.

No productive desktop composition currently instantiates and connects them for
the same completed owner turn.

Therefore preview rendering is also not end-to-end reachable.

## Exact demonstrated residual

The remaining productive residual is:

`OFFICIAL_DESKTOP_SAME_TURN_VISUAL_COMPOSITION_ROOT_BINDING`

This is narrower than another visual subsystem.

It means the official composition root must bind the already-certified
same-turn result exposure and visual presentation path into the existing
desktop turn without adding another conversational execution.

## Required next reconciliation

Before CONTRACT RED, a surgical PRE-RED must prove the exact existing
single-execution source for the applied result.

It must determine:

1. where the existing governed applied-result selection may replace, rather
   than follow, the normal owner-turn execution;
2. how that execution yields the canonical `LocalConversationTurn` required by
   existing desktop text semantics;
3. how existing proposal, episodic-source, optional-service, and personality
   decorators remain effective;
4. how explicit document/source/evidence/visual-context arguments remain
   preserved;
5. how the existing worker obtains text plus optional visual companion without
   a second worker;
6. how the certified runtime binding consumes the exact admitted applied
   result;
7. how bounded preview I/O remains off the Tk main thread;
8. how existing `root.after` or `UIThreadDispatcher` performs Tk mutation;
9. what minimal additive Tk visual surface owns inline/gallery/detail display;
10. how visual failure preserves successful text.

No exact productive callable should be invented before that evidence exists.

## Preserved contracts

Remain unchanged unless later evidence explicitly proves otherwise:

- `LocalConversationTurn`;
- `UIResponse`;
- `DesktopMessage`.

The transcript remains canonical for text.

## Duplicate-risk exclusions

Do not create:

- another `OfficialConversationGateway`;
- another `UnifiedBrain`;
- another source-query executor;
- another desktop controller;
- another same-turn exposure module;
- another projection, companion, presenter, or runtime binding;
- another worker, scheduler, dispatcher, or main loop;
- a generic browser/crawler.

Do not parse visual identity from response text.

Do not update historical hashes to permit unintended protected-file changes.

## Separate later residuals

Remain outside this block:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

The phrases `mostrame fotos` and `ultimas` are not repaired here.

## Reconciled status

`POST_GREEN_MASTER_PLAN_RECONCILIATION:
COMPLETE / PENDING OWNER CERTIFICATION`

`GREEN FOUNDATION: CERTIFIED / REUSE`

`PRODUCTIVE COMPOSITION-ROOT CONSUMER: ABSENT`

`DEMONSTRATED PRODUCTIVE RESIDUAL:
OFFICIAL_DESKTOP_SAME_TURN_VISUAL_COMPOSITION_ROOT_BINDING`

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION: MANDATORY`

`SECOND APPLIED/GATEWAY EXECUTION: FORBIDDEN`

`NEW COGNITIVE/SOURCE AUTHORITY: NONE`

`NEXT PRE-RED: NOT YET OWNER-AUTHORIZED`

STOP for Owner local certification.
