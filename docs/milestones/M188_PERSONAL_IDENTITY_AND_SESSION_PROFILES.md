# M188 — Personal Identity and Session Profiles

M188 introduces explicit, persistent identity profiles for the official local runtime.

## Profiles

The initial local registry contains three configurable profiles:

- `carlos`: private profile for Carlos.
- `spouse`: private profile for Carlos's wife. The local display name is configurable.
- `family-shared`: explicit shared family context.

The shared profile is not an automatic merge of either private profile. It must be selected explicitly with `ROBY_PROFILE_ID=family-shared`.

## Sessions

Every runtime session is permanently bound to one profile. A session cannot be reopened under another identity, and archived sessions cannot be resumed. Session metadata is persisted separately from conversation content and memory.

## Privacy

Profile and session registries are written atomically with `0600` permissions. Default runtime lifecycle state is stored under a profile- and session-scoped path:

`.roby/identity/profiles/<profile-id>/sessions/<session-id>/runtime_state.json`

## Environment

- `ROBY_PROFILE_ID`
- `ROBY_PROFILE_DATA_PATH`
- `ROBY_PROFILE_CARLOS_NAME`
- `ROBY_PROFILE_SPOUSE_NAME`
- `ROBY_PROFILE_SHARED_NAME`
- `ROBY_RUNTIME_SESSION_ID`
- `ROBY_RUNTIME_STATE_PATH` (optional override)

`ROBY_RUNTIME_OWNER` remains accepted for compatibility, but it must match the selected profile owner.
