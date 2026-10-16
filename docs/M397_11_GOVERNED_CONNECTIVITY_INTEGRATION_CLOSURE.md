# M397.11 — Governed Connectivity Integration & Closure

## Status

**M397 — Governed Residence Connectivity: FORMALLY CLOSED** once Ruff and the complete
Pytest suite pass on this increment.

No physical transport is introduced by M397.11.

## Purpose

M397.11 integrates the logical facts defined by M397.1 through M397.10 and proves that
they form one governed connectivity capability without creating a new authority,
coordinator, network runtime or transport implementation.

The closure rule is:

> **A coherent connection may communicate; communication still cannot authorize.**

## Integration contract

`GovernedConnectivitySnapshot` is an immutable, read-only projection over facts already
owned by their canonical boundaries:

- `PeerAuthenticationResult` — identity evidence evaluation;
- `AdmissionVerificationResult` — read-only verification of canonical M396 membership;
- `SessionLifecycleSnapshot` — finite logical session lifecycle;
- `ConnectivityHealthSnapshot` — health and derived readiness.

The snapshot performs no authentication, admission, session transition, health probe,
transport operation or action authorization.

It exists only to fail closed when those facts do not describe the same session and
residence, or when health duplicates disagree with the canonical facts supplied to the
projection.

`communication_ready` is true only when authentication is verified, admission is
verified, the same session is active and the coherent health snapshot is ready.

`authorizes_action` is always false.

## Constitutional closure matrix

### M397-I00 — Single Logical ROBY

No new cognitive core, memory authority, personality, planner or sovereign peer is
created. Connectivity remains a capability of the single ROBY.

### M397-I01 — Connectivity Is Not Authority

Every connectivity-level readiness or acceptance property is non-authorizing.
`GovernedConnectivitySnapshot.authorizes_action` remains false.

### M397-I02 — Identity Is Not Address

Logical peer identity remains `ResidenceId`; transport-local references remain opaque
and separate through `TransportPeerReference`.

### M397-I03 — Explicit Authentication

Peer claims and presentations do not self-authenticate. The authentication boundary
produces an explicit `PeerAuthenticationResult`.

### M397-I04 — Authentication Is Not Admission

Authentication and admission remain different result types. Admission is verified
against the canonical M396 residence snapshot and is never created by M397.

### M397-I05 — Explicit Session

Every integrated connectivity fact must refer to the same finite
`ConnectivitySessionId`. Cross-session facts fail closed.

### M397-I06 — Transport Independence

`core.connectivity_domain` imports no concrete TCP, HTTP, WebSocket, Bluetooth, socket
or equivalent transport library. M397.10 exposes protocols only.

### M397-I07 — Least Connectivity Privilege

The auditable message envelope carries an explicit `MessageKind` and opaque payload
reference. Connectivity supplies no generic remote shell, arbitrary execution API or
implicit capability grant.

### M397-I08 — Credential Non-Propagation

Connectivity contracts contain no access to `.roby/credentials.json` and no private
credential distribution contract. Authentication evidence remains opaque metadata.

### M397-I09 — Observable Health

Health, readiness, authentication, admission and lifecycle remain explicit and
separate. The integration snapshot rejects drift between duplicated health facts and
their supplied governed results.

### M397-I10 — Failure Isolation

Failure and unavailability affect the current connectivity session. They do not mutate
primary-home identity or promote another residence.

### M397-I11 — Revocable Connectivity

Canonical residence revocation causes connectivity termination/readiness loss while
preserving residence history and primary-home continuity.

### M397-I12 — Auditable Communication

Every logical message has message identity, session, sender, receiver, kind and
timezone-aware creation time without requiring raw payload contents or secrets in the
envelope.

## Integrated M397 chain

The complete governed chain is now:

`peer identity presentation`
→ `authentication result`
→ `M396 admission verification`
→ `explicit session lifecycle`
→ `health/readiness`
→ `failure/revocation consequences`
→ `auditable message envelope`
→ `transport adapter boundary`.

`GovernedConnectivitySnapshot` verifies coherence across the central authentication,
admission, session and health facts before communication readiness is consumed.

No step grants operational authority.

## Authority preservation

M397 owns connectivity contracts only.

It does not own:

- cognitive decisions;
- residence admission creation or revocation authority;
- primary-home selection or migration;
- device/capability authorization;
- message semantic authorization;
- command execution;
- credential distribution;
- replication or synchronization;
- concrete network transport.

Those concerns remain behind their canonical governed authorities or future explicit
stages.

## Runtime boundary

M397.11 adds no socket, listener, server, client, URL, port, address, discovery loop,
background network task, serializer, pairing implementation, cryptographic mechanism
or runtime adapter wiring.

The current local-only ROBY runtime remains unchanged.

## Physical transport boundary

M397 is intentionally closed before the first physical carrier is selected.

A TCP, HTTP, WebSocket, LAN or any other concrete adapter must be introduced only after
this closure and behind the M397.10 adapter protocols. Therefore, **physical transport
belongs to a new stage**, not to an extension that silently reopens M397 governance.

## Exit criteria

M397.11 is complete when:

1. the corrected ordered `core/connectivity_domain/__init__.py` is integrated;
2. the integration snapshot is immutable and read-only;
3. inconsistent session/residence/governance facts fail closed;
4. communication readiness remains distinct from action authorization;
5. all M397-I00 through M397-I12 are covered by executable architecture checks and this
   closure record;
6. no concrete transport or runtime wiring exists;
7. root documentation and quality baseline are synchronized;
8. `ruff check .` passes;
9. the complete `pytest -q` suite passes with zero regressions.

> **M397 built the governed doorway. The next stage may choose a road without moving
> the house, copying ROBY, or giving the road authority.**
