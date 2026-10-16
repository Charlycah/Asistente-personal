# ROBY XI.2 — Ordinary Multi-Hypothesis Reachability

## Entry baseline

13,502 PASS + Ruff clean.

## Architectural reconciliation

The repository already contained the required cognitive owners:

- `GovernedExplicitHypothesisSourceAdapterV1` for explicitly structured scenario or
  causal hypothesis semantics;
- `GovernedScenarioSimulator` and `GovernedCausalPredictiveReasoner` for canonical
  hypothesis-bearing reports;
- `GovernedHypothesisDeepener`;
- `GovernedMultiHypothesisDiscriminator` and productive consumption;
- `GovernedExplanatoryModelComposer` and productive explanatory-model consumption.

The ordinary runtime request, however, admits one explicit structured hypothesis
source per turn. The official productive gateway therefore reached deepening with
only one hypothesis at a time. Multi-hypothesis discrimination and explanatory
model composition existed, but ordinary multi-hypothesis reachability was absent.

Verdict: **existing-owner reachability extension**. No hypothesis generator and no
new cognitive authority are justified.

## Implemented productive path

ordinary explicit structured hypothesis turn
→ existing explicit hypothesis adapter
→ canonical scenario/causal hypothesis
→ bounded exact owner/session/world-snapshot history
→ second genuinely distinct same-kind semantic hypothesis
→ existing scenario simulator or causal predictive reasoner
→ existing hypothesis deepening
→ existing multi-hypothesis discrimination
→ existing explanatory model composition
→ same-turn canonical reasoning references and consultative context.

## Anti-fabrication rule

Diversity is semantic, not textual/source-ID diversity.

Scenario identity uses proposition, world domain, fact key, assumed value and
 temporal scope. Causal identity uses proposition, complete cause/effect structure
and temporal scope. A duplicate semantic hypothesis with another source identifier
or fingerprint replaces the same bounded key and does not increase hypothesis
count.

Scenario and causal histories remain separate. Histories are isolated by exact
owner, session and world snapshot. A hypothesis from another session or world
snapshot cannot be borrowed to manufacture a model.

## Governance

The block remains under `governed_reasoning`. It does not:

- infer missing hypothesis semantics from free text;
- establish truth or causality;
- create facts;
- persist the bounded hypothesis history;
- write Memory or World Model;
- create Learning;
- execute Structural Transfer;
- register rules;
- execute actions;
- grant authority.

The explanatory model reaches reasoning only as consultative, revisable context.

## Validation

Six new end-to-end architecture tests cover:

1. two distinct ordinary scenario sources producing a model;
2. semantic duplicate rejection as false diversity;
3. session isolation;
4. same-turn reasoning-source references/context;
5. governance boundaries;
6. the equivalent ordinary causal path.

Expanded affected perimeter: **40 PASS**.

`py_compile` passed for all modified Python files. Modified Python files have no
lines longer than 88 characters.

Official promotion remains gated by local `ruff check .` and full `pytest -q`.
Expected full count: **13,508 PASS**.
