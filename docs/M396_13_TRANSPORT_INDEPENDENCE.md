# M396.13 — Transport Independence Guardrails

## Invariant

**M396-I13 — Transport Independence**

Residence identity, admission, revocation, presence, capabilities, and interaction
locality are transport-neutral contracts. They must not depend on HTTP, WebSocket,
TCP, UDP, Bluetooth, USB, LAN, URLs, hostnames, ports, sockets, or any other concrete
carrier used later to communicate with an extended residence or presence endpoint.

## Rules

1. `ResidenceId` is independent of network address and transport.
2. Admission and revocation records contain no host, URL, port, protocol, or socket.
3. `PresenceEndpoint` identifies a point of presence, not a network connection string.
4. `InteractionLocality` identifies locality, not a transport session.
5. Residence capabilities remain semantic names, not transport bindings.
6. Residence Domain imports no networking, HTTP, WebSocket, Bluetooth, or USB library.
7. Residence Domain exposes no connect, send, receive, listen, bind, dial, or
   request API.
8. Runtime wiring still contains no Residence Domain transport integration at this
   stage.
9. A future transport adapter must be replaceable without changing Residence Domain.
10. Choosing one transport later must not promote it to identity or authority.
11. I03-I12 remain binding.

## Architectural meaning

ROBY may one day reach a mini-PC over LAN, a cellular residence through another
channel, or a Web presence through HTTP/WebSocket. Those are implementation choices
beneath the governed residence contract. The same residence identity must survive a
change in carrier.

**The window is part of the house; the road used to reach it is not.**
