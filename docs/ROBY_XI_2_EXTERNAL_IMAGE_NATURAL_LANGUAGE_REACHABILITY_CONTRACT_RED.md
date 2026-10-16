# ROBY XI.2 — External Image Natural Language Reachability
## CONTRACT RED

## Certified input

Owner-certified PRE-RED baseline:

- 13,504 passes;
- zero failures;
- Ruff clean;
- M361 reproducible.

The PRE-RED identified:

`EXACT_RESIDUAL: EXPLICIT_VISUAL_REQUEST_ADMISSION_VOCABULARY`

and classified the seam as:

`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

## RED scope

One architecture contract is added.

No productive Python is changed.

The RED binds the existing `AppliedConversationalIntelligence` authority to
bounded explicit visual-request language.

## Required behavior

The contract requires:

1. `mostrame fotos de James Webb` is recognized;
2. its canonical query text remains `James Webb`;
3. the existing James Webb topic is preserved;
4. `mostrame imágenes de NASA` is recognized;
5. its canonical query text remains `NASA`;
6. the existing NASA topic is preserved;
7. `mostrame fotos` without a governed topic is not intercepted;
8. `mostrame` without visual-request semantics is not a generic external-query
   key;
9. the existing applied conversational authority remains the capability owner;
10. the existing gateway interpretation and selected governed-query path remain
    the execution owner;
11. freshness/newest ordering is excluded;
12. the certified desktop visual presentation authority remains untouched.

## Expected RED

Focused execution produces:

`3 failed, 6 passed`

The three failures are intentional:

- James Webb visual language is not yet admitted;
- NASA visual language is not yet admitted;
- the existing admission authority does not yet contain the bounded visual
  vocabulary.

The six passing protections demonstrate that the RED does not require a
parallel authority or freshness implementation.

## Productive protection

Productive Python delta is zero.

In particular, this RED does not modify:

- `app/applied_conversational_intelligence.py`;
- `app/official_conversation_gateway.py`;
- `app/nasa_governed_source.py`;
- desktop visual presentation/binding;
- `UnifiedBrain`;
- `runtime_ui_adapter.py`.

## GREEN boundary

The future GREEN must deepen the existing applied conversational admission
semantics only as much as required by this contract.

A bare `mostrame` must not become sufficient by itself.

Freshness ordering remains a later residual.

## Status

`CONTRACT_RED: COMPLETE`

`EXPECTED_FOCAL_RESULT: 3 FAIL / 6 PASS`

`INVALID_RED_FAILURES: ZERO`

`PRODUCTIVE_PYTHON_DELTA: ZERO`

`NEW_AUTHORITY: NONE`

`FRESHNESS_ORDERING: EXCLUDED / LATER`

`NEXT: OWNER RED CERTIFICATION`

STOP before GREEN.
