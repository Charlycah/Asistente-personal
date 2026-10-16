# M396 — Distributed Residence Foundation — Formal Closure

## Status

**FORMALLY CLOSED — constitutional and domain foundation complete.**

Certified incoming baseline:

- M396.15 — Governed Evolution Guardrails
- 10,510 tests passed
- Ruff clean
- M361 quality baseline synchronized
- zero known regressions

This closure adds no productive capability, transport, synchronization, remote
execution or distributed runtime. It consolidates and audits the foundation created
from M396.1 through M396.15.

## Governing principle

> **One house. One ROBY. Many windows.**

ROBY XI.2 remains one governed cognitive entity. Distributed Residence extends where
that same ROBY may be represented and eventually present; it does not multiply ROBY.

## Constitutional coverage

The original M396 constitution defines M396-I00 through M396-I20. Closure confirms
that all of them are represented by the foundation. I03-I15 received dedicated
hardening increments; I00-I02 and I16-I20 are foundational invariants materialized
by M396.1/M396.2 and preserved by the later guardrails.

| Invariant | Closure evidence |
| --- | --- |
| I00 Continuity Ontological | M396.1 constitution + M396.2 domain model |
| I01 Unique ROBY Identity | M396.1/M396.2; no ROBY identity per residence |
| I02 Unique Cognitive Authority | M396.1/M396.2 + I03 authority preservation |
| I03 Authority Preservation | M396.3 |
| I04 Explicit Admission | M396.4 |
| I05 Stable Residence Identity | M396.5 |
| I06 Primary Residence Preservation | M396.6 |
| I07 Local Equivalence | M396.7 |
| I08 Capability Is Not Authority | M396.8 |
| I09 No Implicit Replication | M396.9 |
| I10 Credential Isolation | M396.10 |
| I11 Failure Isolation | M396.11 |
| I12 Revocability | M396.12 |
| I13 Transport Independence | M396.13 |
| I14 No Autonomous Promotion | M396.14 |
| I15 Governed Evolution | M396.15 |
| I16 Residence Awareness | M396.1/M396.2 `ResidenceContextSnapshot` |
| I17 Interaction Locality | M396.1/M396.2 `InteractionLocality` |
| I18 Experiential Continuity | M396.1 + I03 cognitive-authority boundary |
| I19 Home Continuity | M396.1/M396.2 + I06/I11/I14 |
| I20 Presence Mobility | M396.1/M396.2 locality model + I07/I13 |

## Productive domain delivered

`core.residence_domain` now provides declarative, immutable contracts for:

- stable residence identity;
- primary-home and extended-residence roles;
- administrative and presence state;
- explicit admission provenance;
- explicit revocation provenance;
- presence endpoints;
- interaction locality;
- residence context snapshots;
- declared capabilities and limitations.

These contracts describe context. They do not execute distributed behavior.

## Authorities preserved

M396 closes without creating a new cognitive super-authority. Existing governed
authorities retain their competencies, including device, resource, presence, context
and cognitive authorities documented in M396.1 and M396.3.

Residence Domain remains a declarative domain model and is not wired into the
productive runtime root at M396 closure.

## Deliberately NOT implemented

Formal closure explicitly confirms that M396 does **not** implement:

- network discovery;
- pairing;
- residence authentication protocol;
- HTTP, WebSocket, TCP, Bluetooth, USB or other transport adapters;
- distributed runtime orchestration;
- remote execution;
- implicit or explicit state replication engine;
- memory synchronization;
- conversation synchronization;
- file/database synchronization;
- credential distribution;
- automatic failover;
- leader election;
- autonomous primary-home promotion;
- home migration;
- per-device cognition, memory or personality.

These are not missing pieces of M396. They are intentionally deferred capabilities
that must pass M396-I15 before future implementation.

## Baseline compatibility

With zero active extended residences, ROBY's existing local behavior remains the
required reference behavior. The laptop remains the canonical primary home. M396 does
not require another machine, phone, Web session or network connection for ROBY to
continue operating locally.

## Gate for the next epoch

Any operational distributed capability after M396 must begin from this sequence:

1. identify the concrete capability;
2. identify the canonical authority that owns the decision;
3. define an explicit contract;
4. prove compatibility with M396-I00 through M396-I20;
5. preserve local fallback and primary-home continuity;
6. implement the smallest operational slice;
7. synchronize root documentation;
8. pass Ruff, M361 and the complete Pytest suite with zero regressions.

No future milestone may reinterpret M396 closure as permission to bypass these gates.

## Closure declaration

M396 — Distributed Residence Foundation is complete when this closure audit and its
architecture tests pass on top of the certified M396.15 baseline.

The foundation is intentionally non-operational in networking terms. Its achievement is
that ROBY now has a governed vocabulary and constitutional boundary for becoming
present through other authorized places without becoming multiple ROBYs.

> **M396 closes the rules of distributed residence before opening the first real
> distributed connection.**
