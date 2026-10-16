# ROBY XI.2 — INTEL-G8 Corrective Structural Reasoning Authority Reuse — CONTRACT RED

## Certified entry baseline

- Source of truth: INTEL-G8 SURGICAL GREEN certified.
- Local certification: 14,103 PASS, Ruff clean, 0 FAIL.

## Architectural finding

INTEL-G8 correctly reaches a source-neutral `GovernedMemoryMaterializationProposal`,
but its `build_structural_eligibility()` currently fabricates interpretation,
grounding, and compilation fingerprints locally instead of invoking the existing
`governed_reasoning` producers already owned by the canonical M366.6 path.

This corrective contract does not create a new gate to Memory. It repairs the
single-authority invariant inside G8 before any write-adapter admission work.

## Frozen corrective boundary

```text
G6 source-neutral evaluation
        +
G7 exact-linked explicit approval
        ↓
G8 source-neutral content
        ↓
EXISTING GovernedContextualRuleInterpretationProducer
        ↓
EXISTING GovernedBoundedSemanticRoleRelationGrounder
        ↓
EXISTING GovernedContextualRuleGroundingCompiler
        ↓
StructuralEligibilityEvidence
        ↓
existing G8 M366.6 proposal path
        ↓
STOP
```

## CONTRACT RED obligations

1. Structural eligibility fingerprints must come from the existing governed
   interpretation, grounding, and compilation producers.
2. Each existing producer is invoked exactly once on a successful structural
   path, with the G6/G7 source-neutral content, exact evaluation fingerprint,
   and approved scope.
3. Content that is not a governed structural candidate fails closed and does
   not receive fabricated `StructuralEligibilityEvidence`.
4. A non-candidate interpretation stops before grounding and compilation.
5. The G8 source must not retain a parallel local scheme for interpretation,
   grounding, or compilation fingerprints.
6. Existing M366.6 materialization semantics remain unchanged.
7. No write adapter, `GovernedMemoryWriteRequest`, `OfficialMemoryGateway`,
   runtime wiring, persistence, background process, or new authority is added.

## STOP

`STRUCTURAL ELIGIBILITY != MATERIALIZATION PROPOSAL`

`MATERIALIZATION PROPOSAL != WRITE REQUEST != PERSISTED MEMORY`
