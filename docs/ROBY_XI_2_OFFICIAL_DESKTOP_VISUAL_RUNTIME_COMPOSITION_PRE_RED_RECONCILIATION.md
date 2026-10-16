# ROBY XI.2 — Official Desktop Visual Runtime Composition
## PRE-RED Reconciliation

## Owner-certified starting state

The prior POST-GREEN reconciliation is Owner-certified:

- 13,455 tests passed;
- 0 tests failed;
- Ruff clean.

Certified visual foundations already exist and must be reused:

- external-image projection;
- desktop external-image presenter;
- external-image presentation wiring;
- desktop visual companion;
- desktop visual runtime binding.

The demonstrated residual entering this reconciliation is:

`OFFICIAL_DESKTOP_VISUAL_RUNTIME_COMPOSITION`

No productive code or RED tests are added here.

## Mandatory invariant

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION`

A desktop visual result must be a companion of the exact turn that produced the
text.

A second conversational execution is not an acceptable integration mechanism.

## Current productive desktop composition root

`desktop_bootstrap.py` remains the demonstrated official desktop composition
root.

It builds one `LocalConversationUIAdapter` over the existing official
conversation runtime and then decorates that adapter with existing proposal,
episodic-source, optional-service, and personality compositions.

The resulting adapter is passed into the existing `ROBYDesktopApp`.

No parallel desktop controller or conversation gateway is needed.

## Current owner-turn path

The current desktop path is:

`ROBYDesktopApp worker`
-> `DesktopConversationController.submit`
-> decorated UI adapter
-> `LocalConversationUIAdapter.submit_text`
-> `LocalConversationUIAdapter._submit`
-> `UnifiedBrain.process`
-> `OfficialConversationGateway.submit_observed`
-> `OfficialConversationGateway.submit`
-> existing runtime conversation
-> `LocalConversationTurn`
-> `UIResponse`
-> `DesktopMessage`
-> existing `root.after(...)`
-> text transcript

The worker and UI-thread handoff already exist and remain canonical.

## Critical same-turn finding

`UnifiedBrain.process` delegates the owner turn to
`OfficialConversationGateway.submit_observed` or `submit`.

It does not call:

`OfficialConversationGateway.execute_applied_conversational_intelligence`.

The gateway `submit` path also does not call that method.

Therefore the existing applied-intelligence result is not the result object of
the current desktop owner-turn path.

Calling `execute_applied_conversational_intelligence` after the normal desktop
submit would create a second governed conversational/source execution.

That is forbidden.

## Existing turn contract finding

`LocalConversationTurn` is an immutable text/lineage contract containing:

- owner and session identity;
- user and response text;
- status;
- pipeline and operational-response lineage;
- provider/retrieval/network flags;
- rationale and response path;
- creation time and deterministic turn identity.

It contains no governed external-image raw result or visual companion.

Its identity payload includes the response text and lineage fields.

This PRE-RED does not authorize changing `LocalConversationTurn`.

## Exact missing seam

The residual is refined to:

`SAME_TURN_GOVERNED_VISUAL_RESULT_EXPOSURE`

This seam sits upstream of desktop rendering.

The canonical owner-turn execution must expose, mechanically and without a
second query, any governed external-image result already admitted while that
same turn is being produced.

Only then may the certified desktop visual runtime binding project and present
the companion.

## Required architecture direction

Future integration must preserve:

`ONE OFFICIAL OWNER TURN`
-> `ONE EXISTING GOVERNED EXECUTION`
-> `TEXT TURN + OPTIONAL SAME-TURN GOVERNED VISUAL RESULT`
-> `EXISTING UI ADAPTER COMPOSITION`
-> `EXISTING DESKTOP WORKER`
-> `CERTIFIED VISUAL RUNTIME BINDING`
-> `EXISTING UI-THREAD HANDOFF`
-> `ADDITIVE TK VISUAL SURFACE`

The optional visual result is presentation evidence, not a second answer.

It must retain exact artifact identity and provenance from the admitted
governed result.

## Composition ownership

The evidence supports these ownership boundaries:

### Official conversation/runtime

Owns the single governed execution and is the only acceptable place from which
same-turn governed result identity may originate.

### UnifiedBrain

Remains a transparent adapter over the official conversation boundary.

It must not become a second image/source authority.

### LocalConversationUIAdapter

May mechanically expose a same-turn presentation companion only if the
underlying single brain/gateway execution supplies it.

It must not issue a second gateway query.

### Existing desktop wrappers

Proposal review, episodic source constraints, optional-service guard, and
personality composition must remain intact.

A future RED must prove visual transport does not bypass their existing text
semantics.

### Desktop controller

Its existing `DesktopMessage` text contract remains preserved.

No URL parsing or visual source reconstruction belongs here.

### ROBYDesktopApp

Its existing worker remains the background execution boundary.

Preview I/O must not run on the Tk main thread.

### UI handoff

Existing `root.after(...)` and the existing `UIThreadDispatcher` are the
available canonical mechanisms.

No second dispatcher or scheduler is authorized.

## Preview transport

The certified bounded preview fetcher remains the mechanical transport
boundary.

Any future concrete desktop composition must preserve:

- admitted artifact URL only;
- HTTPS-only transport;
- bounded timeout;
- bounded bytes;
- bounded image content type;
- no persistence;
- no source discovery;
- no generic browser/crawler;
- no Vision, Memory, Learning, diagnostics, or Proposal side effects.

## Minimal Tk presentation boundary

A future GREEN may add only the smallest additive Tk-owned visual surface after
the same-turn exposure seam is proven.

The text transcript remains canonical and successful text must survive any
visual failure.

Gallery order and artifact identity must remain unchanged.

Detail/modal presentation must reuse the same artifact without requery.

## Proposed CONTRACT RED dimensions

After Owner certification, CONTRACT RED should prove:

1. one owner turn invokes the canonical governed turn execution exactly once;
2. same-turn visual evidence can be exposed without a second gateway query;
3. visual evidence originates from the exact admitted governed result;
4. no URL or artifact identity is parsed from response text;
5. existing `LocalConversationTurn`, `UIResponse`, and `DesktopMessage`
   contracts remain backward compatible;
6. existing adapter decorators preserve their text behavior;
7. certified desktop visual runtime binding is reused;
8. existing desktop worker remains the only background owner-turn worker;
9. preview I/O remains outside the Tk main thread;
10. Tk mutation uses an existing UI-thread handoff;
11. visual failure preserves successful text;
12. detail presentation reuses the same artifact without requery;
13. no second gateway, brain, source executor, presenter, binding, dispatcher,
    scheduler, or main loop appears;
14. no Vision/repository/Memory/Learning/diagnostics/Proposal/Planning/Execution
    side effects are introduced.

The RED should target the missing seam behavior, not invent an unnecessary
parallel manager or controller.

## Explicit exclusions

Do not create:

- a second `OfficialConversationGateway`;
- a second `UnifiedBrain`;
- a second desktop controller;
- a second applied-intelligence execution;
- a second governed source query;
- another image projection, companion, presenter, or runtime binding;
- another worker, scheduler, dispatcher, or main loop;
- a generic browser/crawler.

Do not mutate current turn identity merely to attach presentation metadata.

## Separate later residuals

Remain outside this block:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

`mostrame fotos` and `ultimas` are not repaired by this composition PRE-RED.

## Reconciled status

`OFFICIAL_DESKTOP_VISUAL_RUNTIME_COMPOSITION_PRE_RED:
COMPLETE / PENDING OWNER CERTIFICATION`

`EXACT MISSING SEAM: SAME_TURN_GOVERNED_VISUAL_RESULT_EXPOSURE`

`CURRENT APPLIED-INTELLIGENCE METHOD: NOT THE OWNER-TURN RESULT PATH`

`SECOND APPLIED/GATEWAY EXECUTION: FORBIDDEN`

`LOCAL_CONVERSATION_TURN: PRESERVE`

`UIResponse/DesktopMessage: PRESERVE`

`EXISTING ADAPTER COMPOSITION/WORKER/UI HANDOFF: REUSE`

`NEW COGNITIVE/SOURCE AUTHORITY: NONE`

`CONTRACT RED: NOT YET OWNER-AUTHORIZED`

STOP for Owner local certification.
