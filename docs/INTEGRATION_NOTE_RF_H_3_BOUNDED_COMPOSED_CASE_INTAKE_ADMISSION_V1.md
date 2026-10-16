# RF-H/3 — Bounded Composed Case Intake & Admission v1

## Scope

RF-H/3 closes the productive boundary required by the historical H-R1 case:
two already-certified temporary rule specs can be grounded and admitted from one
explicit case observation, then consumed by the existing single bounded
rule-result propagation pass.

## Governed authorities retained

- `GovernedContextualCaseRoleGrounder` remains case-role authority.
- `GovernedContextualCaseClaimProjector` remains explicit-case claim authority.
- `ProductiveTemporaryRuleIntake` remains the productive composition boundary.
- `GovernedTemporaryConcreteRuleAdmissionBoundary` remains admission authority.
- `GovernedInferenceEngine` remains the only inference/propagation authority.
- `TemporaryContextualPredicateVocabularyFactory` remains predicate identity
  authority.

No parallel parser, registry, inference engine, persistence layer, Memory,
Learning, world-model mutation, action path, provider path, or retrieval path is
introduced.

## Historical H-R1 compatibility

The bounded case grounder additionally recognizes the explicit form:

`<actor> puede <capability> únicamente a partir de <resource>`

The exclusivity marker is itself sufficient evidence for the Neral
no-alternative condition. Bounded informational resource failures include
explicit illegibility/corruption forms.

When the same case explicitly states that the capability is indispensable for a
dependent capability, the Neral capability binding reuses that explicit
prerequisite entity reference. This makes the Neral conclusion and Velar
prerequisite refer to one concrete entity without free-form semantic guessing.

A bounded Spanish enclitic form such as `reproducirlo` is resolved only against
the explicit prerequisite object phrase in the same relation.

## Cross-rule predicate identity

Predicate identity is now stable for the same semantic predicate label inside
the same scope, independent of teaching-source provenance. Entry and vocabulary
fingerprints still preserve their source provenance.

Historical Neral's bounded-postcondition compatibility compiles its conclusion
as availability of the concrete capability entity. This is restricted to that
already-certified historical Neral grammar; the legacy canonical Neral compile
shape is preserved.

## Deferred Velar availability premise

For H-R1, the explicit case supplies the `required_for` relation but does not
claim that the prerequisite capability is unavailable. The case grounder may
therefore bind both Velar roles while marking availability as deferred when the
same case contains the bounded historical Neral dependency.

The projector excludes that deferred unavailable premise. It is satisfied only
by Neral's `RULE_RESULT` during RF-H/1 propagation.

## Bounded composed intake

One observation may admit at most two compatible pending specs. Aggregate
`projections` and `admissions` are exposed while legacy singular `projection`
and `admission` continue to point to the final admitted item.

Current-turn projected claims are overlaid ephemerally on the governed reasoning
context. They are not registered in `ClaimRegistryManager` and are not
persistent. An otherwise insufficient context becomes inference-ready only for
that transient explicit-claim view.

## Propagation limit

RF-H/1 remains unchanged: base inference plus one propagation pass only.
RF-H/3 does not authorize A -> B -> C, fixed-point inference, recursive chaining,
persistent derived facts, or authority gain.

## Validation

The historical H-R1 exact wording is required to demonstrate:

1. historical Neral -> `SPEC_STORED`;
2. historical Velar -> `SPEC_STORED`;
3. exact H-R1 -> two rules admitted in one observation;
4. no projected `reconstruct ... unavailable` claim;
5. Neral derives prerequisite unavailability;
6. Velar consumes that exact `RULE_RESULT`;
7. final dependent capability remains `REVIEW_REQUIRED`;
8. no transient claim enters the claim registry.

Repository closure still requires `ruff check .` and full `pytest -q`.
