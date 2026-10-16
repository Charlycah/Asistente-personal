# ROBY XI.2 — M402.1 Residential Node Foundation

## Scope

Minimal binding and snapshot foundation only. No productive wiring is introduced.

## Contracts

- `ResidentialNodeBinding`: stable declarative link between one M396 `ResidenceId`, an
  existing resident component id, and hosted capability ids.
- `ResidentialNodeSnapshot`: derived read-only operational projection.
- `ResidentialNodeEvaluator`: pure adapter over already-governed M396/M397/M398 and
  resident lifecycle facts.

## States

`REGISTERED`, `READY`, `DEGRADED`, `UNAVAILABLE`.

`READY` requires a non-revoked M396 residence, running/healthy resident lifecycle, coherent
M397 communication readiness, and an available M398 governed physical binding.

`READY` never grants action authority.

## Invariants

- identity comes only from M396 `ResidenceId`;
- hosted capabilities must be declared by the M396 residence;
- M397 remains owner of authentication/admission/session/readiness;
- M398 remains owner of physical transport;
- resident lifecycle remains owned by the existing runtime;
- no new authority, runtime, registry, or capability catalogue;
- no memory/knowledge/config replication;
- no credentials;
- no perception/cameras/sensors;
- no productive `RuntimeCompositionRoot` wiring in this increment.

## Master-plan impact

Directly advances the recovered Residential Node pending item without entering Governed
Synchronization or Residential Perception.
