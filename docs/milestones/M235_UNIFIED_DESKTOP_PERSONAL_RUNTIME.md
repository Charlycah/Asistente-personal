# M235 — Unified Desktop Personal Runtime

M235 makes the existing Tkinter interface the official graphical entrypoint for the same certified personal runtime used by the development console.

## Operational contract

Run:

```powershell
python main.py --desktop
```

The desktop application builds `EndToEndLocalConversation`, starts the long-lived lifecycle and heartbeat supervisor, and starts the resident battery and reminder awareness services. Normal messages and conversational reminder commands therefore cross the same governed pipeline as terminal conversations.

Resident notices are placed in a thread-safe queue and rendered by Tkinter through `root.after()`. Closing the window stops reminder awareness, battery awareness, the supervisor, and the lifecycle in reverse order.

## Scope boundary

M235 does not redesign the interface, add dynamic household profile selection, or add ambient listening. Those remain subsequent milestones.
