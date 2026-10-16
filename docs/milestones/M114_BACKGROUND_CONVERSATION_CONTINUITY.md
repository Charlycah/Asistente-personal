# M114 — Background Conversation Continuity

M114 preserves a minimal, governed, resumable logical checkpoint when mobile conversation or presence moves outside the foreground.

## Scope
- background checkpoint eligibility;
- waiting-user continuity;
- explicit resume, suspend, and terminate decisions;
- network and user-presence constraints;
- checkpoint age and signal freshness;
- immutable repository-backed decisions.

## Non-goals
M114 does not execute background services, schedule work, send notifications, persist raw messages, open network connections, or mutate M111–M113 artifacts.
