# M397.1 — Governed Connectivity Constitution

## Status

Constitutional opening of **M397 — Governed Residence Connectivity**.

M397.1 introduces no operational network, transport adapter, socket, server, client,
authentication implementation, pairing, remote execution or distributed runtime.

It defines what governed connectivity means before ROBY opens the first real
distributed connection.

## Certified inherited baseline

M397.1 starts exclusively from the formally closed M396 baseline:

- M396 — Distributed Residence Foundation — Formal Closure;
- 10,520 tests passed;
- Ruff clean;
- M361 quality baseline synchronized;
- zero known regressions.

M396-I00 through M396-I20 remain active constraints. M397 may operationalize
connectivity only without weakening residence identity, authority preservation,
credential isolation, primary-home continuity, failure isolation or governed evolution.

## Governing principle

> **Connectivity grants communication; it never grants authority.**

A residence may become reachable without gaining cognitive authority, capability
authority, permission to execute actions, access to ROBY's private credentials or
power to alter the primary home.

## Constitutional purpose

M397 defines how the single ROBY may establish a real, authenticated, observable,
revocable and auditable communication relationship with an already governed
residence.

M396 answers **who/where**.
M397 answers **whether and how communication is currently possible**.
Transport answers only **how bytes move**.

These concerns must remain separate.

## Architectural layers

### ROBY cognitive core

The existing governed cognitive core remains unique. M397 creates no remote brain,
peer brain, replica cognition, secondary personality, local memory authority or
distributed cognitive leader.

### Residence Domain — M396

`core.residence_domain` remains the canonical declarative model for residence identity,
role, admission provenance, revocation provenance, presence endpoints and interaction
locality.

M397 does not redefine `ResidenceId`, `PRIMARY_HOME`, `EXTENDED` or admission semantics.

### Connectivity Domain — future M397 increments

A future connectivity domain may represent communication facts such as:

- peer identity claim;
- authentication result;
- connection/session identity;
- connectivity state;
- readiness/health;
- governed message envelope;
- revocation/termination evidence;
- auditable connectivity events.

M397.1 defines this vocabulary conceptually only. It creates no productive connectivity
package yet.

### Transport adapters — future M397 increments

TCP, HTTP, WebSocket, Bluetooth, USB, LAN or any future mechanism are implementation
details behind a transport boundary.

No transport primitive forms part of logical residence identity.

## Constitutional distinctions

The following states are intentionally distinct:

`ADMITTED` != `AUTHENTICATED` != `CONNECTED` != `READY`.

A residence can remain admitted while temporarily unreachable.

Authentication proves an identity claim according to a future governed mechanism; it
does not itself admit a residence.

Connection proves a communication channel exists; it does not prove readiness,
capability permission or operational authority.

Readiness is an observable communication/health fact, never a grant of authority.

## Initial invariants

### M397-I00 — Single Logical ROBY

Connectivity never creates a second sovereign ROBY, cognitive core, memory authority,
personality or planning authority.

### M397-I01 — Connectivity Is Not Authority

Being connected does not grant decision authority, capability authority, execution
permission, admission authority or cognitive authority.

### M397-I02 — Identity Is Not Address

`ResidenceId` and future peer identity are independent of IP address, hostname, URL,
port, socket, interface name or transport session.

### M397-I03 — Explicit Authentication

A peer identity claim is never accepted merely because a remote process says who it is.
Future operational connectivity must require explicit governed authentication evidence.

### M397-I04 — Authentication Is Not Admission

Successful authentication does not automatically create or restore residence admission.
Admission remains governed by M396.

### M397-I05 — Explicit Session

Every future active communication relationship must be attributable to an explicit,
finite and observable session/connection context.

### M397-I06 — Transport Independence

Connectivity contracts remain independent of TCP, HTTP, WebSocket, Bluetooth, USB,
LAN, Internet or any other concrete transport.

### M397-I07 — Least Connectivity Privilege

A communication session may exchange only the categories of information explicitly
allowed by its governed contract. Connectivity is not a generic remote shell.

### M397-I08 — Credential Non-Propagation

Opening or authenticating a connection never copies, exposes or distributes ROBY's
private service credentials or `.roby/credentials.json`.

### M397-I09 — Observable Health

ROBY may represent connectivity health such as `CONNECTED`, `READY`, `DEGRADED` or
`UNAVAILABLE` without interpreting those states as authority, admission or identity.

### M397-I10 — Failure Isolation

Loss, timeout, malformed traffic or failure of an extended-residence connection must
not compromise the primary home's local continuity.

### M397-I11 — Revocable Connectivity

Future connectivity must support explicit termination/revocation without rewriting
ROBY identity, residence history or primary-home continuity.

### M397-I12 — Auditable Communication

Architecturally relevant connectivity events must be traceable without logging private
secrets, raw credentials or unrestricted message contents.

## Message rule

> **Message received != authorized command.**

A future message may carry a request, observation, acknowledgement or evidence. Receipt
alone never authorizes execution, tool use, device activation, memory mutation,
configuration change or code modification.

Operational actions must continue through their canonical governed authorities.

## Trust boundary

M397 treats every external connectivity peer as outside the primary-home trust boundary
until the required future authentication and admission checks are satisfied.

Network reachability, local-subnet membership, hostname familiarity or possession of an
IP address are not sufficient trust evidence.

## Failure model

M397 must assume that future peers can:

- disappear without warning;
- reconnect from another network address;
- send malformed or stale data;
- fail authentication;
- be admitted but unavailable;
- be authenticated but not admitted;
- be connected but not ready;
- be revoked while a session exists.

The safe result is always preservation of local ROBY continuity and denial of
unauthorized action.

## Deliberately out of scope for M397.1

M397.1 does not implement:

- sockets, servers or clients;
- HTTP/WebSocket/TCP/Bluetooth/USB adapters;
- network discovery;
- pairing protocol;
- cryptographic authentication;
- key exchange;
- remote commands;
- remote Python execution;
- arbitrary file transfer;
- memory or database synchronization;
- `.roby` replication;
- credential distribution;
- Ollama/model remote invocation;
- camera, microphone, sensor or device control;
- home migration or failover;
- distributed cognitive execution.

## Evolution gate

Every operational M397 increment must:

1. identify the exact connectivity capability;
2. identify the canonical authority that owns any resulting decision;
3. define a transport-neutral contract first;
4. prove compatibility with M396-I00 through M396-I20 and M397 invariants;
5. preserve local-only ROBY behavior;
6. add the smallest operational surface;
7. add architecture and behavior tests;
8. synchronize root documentation and M361;
9. pass Ruff and the complete Pytest suite with zero regressions.

## Exit criterion for M397.1

M397.1 is closed when this constitution is present, root documentation is synchronized,
architecture tests prove that no operational connectivity was introduced, and the
certified M396 behavior remains unchanged.

> **M396 defined the windows. M397.1 defines the rules for opening one safely.**
