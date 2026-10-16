# M111 — Mobile Conversation Runtime

M111 adds the first logical runtime for Mobile Companion conversations.

## Responsibility
Transform an eligible M110 mobile foundation plus explicit runtime signals into an auditable state transition.

## States
- `idle`
- `running`
- `waiting_user`
- `background`
- `suspended`
- `terminated`

## Actions
- `start`
- `resume`
- `wait`
- `enter_background`
- `suspend`
- `stop`
- `none`

## Non-goals
No audio, notifications, GPS, camera, sensors, transport, scheduling, sleeping, session mutation, message delivery, or active-device mutation.

## Validation
40 focused tests plus the complete regression suite.
