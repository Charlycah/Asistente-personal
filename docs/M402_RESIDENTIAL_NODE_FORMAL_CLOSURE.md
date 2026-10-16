# ROBY XI.2 — M402 Residential Node Formal Closure

**Official closure baseline:** M402.3 — Residential Node Minimal Physical/Productive Bootstrap  
**Validation:** M361 synchronized · Ruff clean · 11,072 tests passed · 0 regressions.

## Formal decision

**M402 — Residential Node is CLOSED architecturally and operationally.**

M402.4 is not authorized by continuity alone.

The remaining execution on a concrete mini-PC is classified as a separate
**Residential Node Physical Deployment Certification**. It is deployment evidence,
not an architectural blocker and not a reason to extend M402.

## Closed chain

M396 Residence Domain
→ M397 Governed Connectivity
→ M398 Governed Physical Transport
→ M402.1 Residential Node Foundation
→ M402.2 Minimal Lifecycle Integration
→ M402.3 Minimal Physical/Productive Bootstrap.

## Final ownership

- M396 owns ResidenceId, admission and declared capabilities.
- M397 owns authentication, session and communication readiness.
- M398 owns physical transport and governed connection binding.
- OfficialROBYRuntime / ResidentComponentRegistry retain central resident lifecycle authority.
- ResidentRuntimeService is a lightweight supervisor, not cognitive authority.
- M402 owns residential binding, derived status, lifecycle observation and minimal process bootstrap only.

## Permanent invariants

- one ROBY / one logical brain;
- one RuntimeCompositionRoot;
- one authority per capability;
- ResidenceId is not a network address;
- communication readiness is not authorization;
- transport availability is not identity;
- ResidentialNodeStatus.READY is not permission to act;
- heartbeat/lease are operational metadata, not memory;
- no implicit replication;
- no background cognitive brain on the residential node;
- no automatic authority transfer to the node.

## Completion levels

- Architectural: CLOSED.
- Operational: CLOSED for the configurable minimal productive route.
- Physical deployment: PENDING CERTIFICATION on concrete hardware.
- End-to-end experience: PENDING physical deployment.

## Explicitly outside M402

Governed Synchronization, memory/knowledge/config replication, conflict resolution,
Residential Perception, cameras/sensors and remote cognitive execution remain separate
future work.

## Next master step

**Governed Synchronization Go/No-Go against Estado Maestro Post-M402.**
