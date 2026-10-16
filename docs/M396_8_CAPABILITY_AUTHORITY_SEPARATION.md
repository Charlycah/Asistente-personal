# M396.8 — Capability / Authority Separation Guardrails

## Invariant

**M396-I08 — Capability != Authority**

A capability declared by a residence or presence endpoint is an objective statement
about what that locality can expose. It is not permission, authorization, ownership,
or authority to decide or execute that capability.

## Rules

1. `capabilities` remains declarative locality context.
2. A capability name never grants permission to invoke or execute anything.
3. Primary-home status grants no extra operational authority.
4. Extended-residence admission grants membership, not capability authority.
5. Active `InteractionLocality` grants no authority to its residence or endpoint.
6. Presence endpoints can advertise context but cannot become decision authorities.
7. Residence Domain defines no permission, grant, policy, execution or invocation API.
8. Residence Domain imports no device/capability authority or execution gateway.
9. Existing canonical authorities remain the sole owners of operational decisions.
10. M396.8 introduces no transport, RPC, remote execution, authentication or pairing.
11. I03-I07 remain binding.

## Example

A cellular residence may declare `camera`, `gps`, `microphone`, and `sensors`. That
means those capabilities exist at that locality. It does not mean the cellular
residence may activate them. Any future operation must still pass through ROBY's
existing governed authority for that capability.

**More senses do not create another authority.**
