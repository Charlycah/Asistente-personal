# M398.1 — Physical Transport Constitution

## Status

Constitutional opening of **M398 — Governed Physical Transport**.

M398.1 introduces no socket, listener, dialer, server, client, serializer, framing
implementation, network discovery, reconnect loop or physical carrier. It defines the
rules that every future concrete transport must obey before ROBY opens the first real
physical channel between residences.

## Certified inherited baseline

M398.1 starts exclusively from the formally closed M397 baseline:

- M397 — Governed Residence Connectivity — Formal Closure;
- 10,687 tests passed;
- Ruff clean;
- M361 quality baseline synchronized;
- zero known regressions.

M396-I00 through M396-I20 and M397-I00 through M397-I12 remain permanent constraints.
M398 may move bytes only without weakening residence identity, authentication,
admission, session lifecycle, health/readiness, revocation, auditability, credential
isolation, primary-home continuity or canonical operational authorities.

## Governing principle

> **Transport carries bytes; it never creates trust, identity, admission or authority.**

A physical channel can establish reachability and carry an already-governed message.
It cannot decide who a peer is, whether a residence belongs to ROBY, whether a session
is admitted, whether a message is an authorized command, or whether an action may run.

M397 governs the logical communication relationship. Existing canonical capability
authorities continue to govern actions. M398 is subordinate to both.

## Architectural purpose

M396 answers **who/where may be a residence**.
M397 answers **whether a governed communication relationship is valid and ready**.
M398 answers only **how an already-governed message crosses a physical carrier**.

These responsibilities must remain separate even when future adapters use TCP, HTTP,
WebSocket, Bluetooth, USB, local IPC or another mechanism.

## Required architectural placement

### Connectivity Domain — M397

`core.connectivity_domain` remains the canonical owner of peer identity claims,
authentication results, admission verification, logical sessions, readiness,
revocation consequences, auditable message envelopes and transport-neutral adapter
contracts.

M398 must not fork, copy, reinterpret or shadow these contracts.

### Physical Transport — future M398 increments

Concrete transport code may eventually own only carrier concerns such as:

- opening and closing physical connections;
- reading and writing framed bytes;
- transport-local peer references;
- bounded buffering;
- carrier timeouts and I/O failures;
- decoding only enough structure to reconstruct a transport-neutral envelope;
- reporting transport outcomes back through M397 boundaries.

It must not own ROBY identity, residence admission, authentication policy, session
authority, command authorization, cognitive decisions or capability execution.

### Runtime composition

A future composition root may wire one concrete adapter behind M397.10 Protocols. The
composition root may connect components but may not become a second connectivity or
transport authority.

M398.1 performs no such wiring yet.

## Constitutional invariants

### M398-I00 — Single ROBY Preservation

A physical channel never creates a second ROBY, remote sovereign brain, replica
identity, alternate cognitive authority or secondary operational authority.

### M398-I01 — Transport Is Subordinate

Every concrete carrier is an adapter behind the transport-neutral contracts established
by M397.10. Carrier implementation details never become domain truth.

### M398-I02 — Physical Reachability Is Not Trust

A successful socket connection, accepted inbound stream, reachable host or open port is
only a transport fact. It does not authenticate or admit a residence.

### M398-I03 — Address Is Not Identity

IP address, hostname, URL, port, interface, MAC address, socket object, file descriptor
or transport-local peer reference never replaces `ResidenceId` or governed peer
identity.

### M398-I04 — No Authentication Inside Carrier

A carrier may transport authentication evidence but may not decide authentication by
itself. Authentication remains behind the M397 authentication boundary.

### M398-I05 — No Admission Inside Carrier

A listener, dialer or adapter may never create, restore or infer residence admission.
Admission remains governed by M396 and verified through M397.

### M398-I06 — Explicit Session Binding

Every transported message must remain attributable to the explicit M397 logical
session and residence binding. A physical reconnect does not resurrect a closed or
terminated logical session.

### M398-I07 — Envelope Before Payload Meaning

The transport layer carries `AuditableMessageEnvelope` data or its bounded serialized
representation. It does not interpret payload meaning, execute commands or route
payloads directly to capability implementations.

### M398-I08 — Receive Is Not Execute

> **Bytes received != message authorized != action authorized.**

Receiving or decoding a frame never authorizes tool use, device action, memory mutation,
configuration change, file modification, code execution or cognitive operation.

### M398-I09 — Bounded and Fail-Closed Input

Future framing and decoding must reject malformed, oversized, incomplete, unsupported
or internally inconsistent input without creating partially trusted domain state.

### M398-I10 — Failure Isolation

Timeout, disconnect, malformed traffic, peer disappearance or carrier failure must not
damage the primary home's local continuity or silently promote another residence.

### M398-I11 — Reconnect Is A New Physical Fact

A physical reconnect may create a new carrier connection but never silently restores
a terminated M397 session, revoked admission, authentication result or readiness.

### M398-I12 — Credential Isolation

Transport implementation must not read, copy, serialize, synchronize or expose
`.roby/credentials.json` or private service credentials merely to establish a carrier.
Any future cryptographic credential mechanism requires its own governed security
contract and least-privilege boundary.

### M398-I13 — Transport Replaceability

TCP, WebSocket, HTTP, Bluetooth, USB or any future carrier must be replaceable without
changing M396 residence identity semantics or M397 connectivity semantics.

### M398-I14 — Observable Transport Without Secret Leakage

Architecturally relevant transport events may be audited using bounded metadata such as
session identifiers, dispositions and failure categories. Raw private credentials,
unrestricted payload contents and secret material must not be logged by default.

## Initial carrier strategy

M398 intends to prove the architecture with one minimal local physical carrier before
adding alternatives. The preferred reference candidate is local TCP because it exposes
connection, framing, timeout and failure concerns without requiring higher-level HTTP
semantics.

This is an architectural direction, not an implementation in M398.1. The concrete
carrier is introduced only after a transport runtime and framing boundary exist.

## Deliberately out of scope for M398.1

M398.1 does not implement:

- `socket` usage;
- TCP listener or client;
- HTTP or WebSocket server/client;
- Bluetooth, USB or IPC adapter;
- binary or JSON serializer;
- message framing;
- reconnect loop;
- network discovery;
- pairing;
- key exchange or cryptographic authentication;
- remote commands or remote Python execution;
- arbitrary file transfer;
- memory/database synchronization;
- cognitive replication;
- model/Ollama remote invocation;
- device or sensor control;
- Internet exposure;
- cloud relay;
- runtime wiring.

## Planned M398 evolution

The intended sequence is deliberately incremental:

1. **M398.1 — Physical Transport Constitution** — constitutional rules only.
2. **M398.2 — Transport Runtime Foundation** — transport-neutral runtime facts, still
   without sockets.
3. **M398.3 — Governed Connection Binding** — physical connection to M397 session and
   residence binding.
4. **M398.4 — Framing & Serialization Boundary** — bounded conversion between envelope
   and transmitted representation.
5. **M398.5 — Local TCP Adapter** — first concrete physical carrier.
6. **M398.6 — Governed Listener & Dialer** — controlled inbound/outbound connection
   establishment.
7. **M398.7 — Transport Failure & Recovery** — timeout, disconnect and reconnect facts
   without implicit readmission.
8. **M398.8 — End-to-End Residence Channel** — first governed physical message path.
9. **M398.9 — Security & Abuse Guardrails** — malformed input, oversized frames,
   mismatch and replay-oriented protections.
10. **M398.10 — Governed Physical Transport Integration & Closure** — integration,
    audit and formal closure if the evidence supports it.

The numbering is a roadmap, not permission to add unnecessary micro-increments. Adjacent
steps may be synthesized when one coherent, independently verifiable change is safer.

## Evolution gate

Every operational M398 increment must:

1. preserve M396 and M397 invariants;
2. identify exactly one transport concern;
3. keep the carrier subordinate to M397.10 boundaries;
4. avoid duplicate authentication, admission, session or action authorities;
5. preserve local-only ROBY behavior when no transport is configured;
6. fail closed on malformed or inconsistent external input;
7. add architecture and behavior tests before expanding runtime wiring;
8. keep private credentials outside transport state;
9. synchronize root documentation and the M361 quality baseline;
10. pass `ruff check .` and the complete `pytest -q` suite with zero regressions.

## Exit criterion for M398.1

M398.1 is closed when this constitution is present, M397 connectivity code is hash
preserved, root documentation is synchronized, no concrete network library or runtime
transport wiring has been introduced, and the complete validation gates remain clean.
