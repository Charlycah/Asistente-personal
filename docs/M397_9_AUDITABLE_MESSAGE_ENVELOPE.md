# M397.9 — Auditable Message Envelope

## Purpose

M397.9 defines the minimal transport-neutral envelope required to identify, route,
correlate and audit a logical message between governed ROBY residences.

It does not send any message.

## Core rule

> **Message received != authorized command.**

A valid message envelope proves only that structured communication metadata exists.
It never grants command, capability, tool, device, memory or code-execution authority.

## Contracts

### `MessageId`

Opaque stable identity for one logical message.

### `MessageCorrelationId`

Opaque identifier that links related request/response or event flows without depending
on a network protocol.

### `MessageKind`

Initial non-authorizing categories include:

- `PRESENCE_PROBE`
- `PRESENCE_ACK`
- `OBSERVATION`
- `REQUEST`
- `RESPONSE`
- `EVENT`

A `REQUEST` is still only a message category; it is not permission to act.

### `MessagePayloadReference`

Carries only an opaque payload reference and content type.

The envelope does not parse, execute or trust payload contents.

### `AuditableMessageEnvelope`

An immutable envelope contains:

- `message_id`;
- `session_id`;
- sender `ResidenceId`;
- receiver `ResidenceId`;
- message kind;
- timezone-aware creation timestamp;
- optional correlation id;
- optional payload reference.

Sender and receiver must be different residences.

## Auditability

The envelope provides enough metadata to trace who addressed whom, in which logical
session, under which message id, at what time, and how related messages correlate.

Auditability does not require logging raw secrets or unrestricted payload contents.

## Authorization boundary

`authorizes_action` is always false.

Any future execution request must pass through the canonical authority of the requested
capability after message reception.

No message kind can bypass that gate.

## Transport independence

The envelope contains no IP address, hostname, URL, port, socket id, HTTP method,
WebSocket opcode or Bluetooth address.

Serialization and transport remain future adapter concerns.

## Credential isolation

The envelope defines no password, API key, access token, refresh token, private key or
credential-store field.

Payload references must not be used as a backdoor to embed private credentials.

## Session boundary

Every message belongs to an explicit `ConnectivitySessionId`.

A future receiver must reject or quarantine messages that do not belong to the current
governed session.

M397.9 defines the envelope only; it does not implement the receiver.

## Runtime boundary

M397.9 introduces no send, receive, queue, broker, socket, server, client, serializer,
network listener or runtime wiring.

## Exit criterion

M397.9 is complete when message identity, addressing, correlation and audit metadata
are immutable, transport-neutral, secret-free and regression-tested.

> **ROBY can now define what a message is before allowing any message to travel.**
