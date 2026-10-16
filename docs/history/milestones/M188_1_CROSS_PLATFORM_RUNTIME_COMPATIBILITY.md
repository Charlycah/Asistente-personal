# M188.1 — Cross-Platform Runtime Compatibility

## Purpose

Make the operational runtime and its tests behave correctly on Carlos' Windows
laptop while retaining exact owner-only file modes on POSIX systems.

## Changes

- Added `core.platform_runtime_compatibility` as the single boundary for
  filesystem privacy and process-liveness behavior.
- Runtime files continue to use exact mode `0600` on POSIX.
- On Windows, ROBY applies the portable read/write policy available through
  Python and relies on the per-user private runtime directory for NTFS access
  control. Tests no longer interpret Windows `st_mode` as a POSIX ACL.
- Windows process detection now uses `OpenProcess` and treats access denied as
  evidence that the process exists.
- Journals, traces, memory databases, heartbeat state, leases, profiles, and
  sessions all use the shared private-file function.

## Non-goals

- No dependency on `psutil`.
- No automatic modification of inherited NTFS ACLs.
- No cognitive, provider, memory-policy, or tool behavior changes.
