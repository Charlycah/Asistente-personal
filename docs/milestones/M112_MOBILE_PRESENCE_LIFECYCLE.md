# M112 — Mobile Presence Lifecycle

## Objective

Govern the logical lifecycle of ROBY's presence on a mobile device without performing device I/O or operating-system actions.

## Scope

M112 adds:

- explicit mobile presence states;
- declarative lifecycle actions;
- policy-governed background and dormant presence;
- conservative propagation of M111 decisions;
- device availability, connectivity, user presence, and signal freshness checks;
- immutable, deterministic, repository-backed decisions.

## States

- `inactive`
- `activating`
- `active`
- `background`
- `dormant`
- `suspending`
- `terminated`

## Actions

- `activate`
- `maintain`
- `enter_background`
- `become_dormant`
- `suspend`
- `terminate`
- `none`

## Boundary

M112 does not start conversations, send notifications, run timers, activate audio, inspect location, open network connections, change the active device, transfer context, or mutate the M111 runtime. It only declares the next presence transition.
