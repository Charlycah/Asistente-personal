# ADR-166 — Natural Greeting Response

## Decision

Introduce M164 as a deterministic natural-greeting realization layer downstream
from M163. It may produce a short greeting only when M163 classified the entry as
a greeting.

## Rationale

`Hola ROBY` must not be acknowledged as a command or echoed back. A dedicated
realization boundary allows ROBY to answer naturally while keeping greeting
selection deterministic, testable, local, and free from provider or network
side effects.

## Consequences

- M164 consumes the exact M163 conversation-entry result.
- Non-greeting entries are withheld.
- Greeting variants may consider the current day period.
- Recently used responses are avoided when alternatives exist.
- Visible greeting text uses ROBY's current no-accent convention.
- Provider calls, network access, and platform mutation remain forbidden.
- Broader voice and style governance remains assigned to M165.
