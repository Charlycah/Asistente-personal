# M147 — Living Conversation Presence Consumer

M147 is the first real consumer of the governed Presence Context pipeline. It adapts M146 gateway accesses into immutable Living Conversation presence cues.

## Responsibility
- select the newest compatible M146 gateway result;
- validate owner, consumer, freshness, and confidence;
- preserve exact gateway and access lineage;
- expose situation kind, situation signal, declared conversation context, completeness, and confidence;
- represent complete, partial, empty, review, blocked, and not-applicable outcomes.

## Explicit exclusions
M147 does not activate conversation, select timing, generate prompts, realize responses, execute consumer logic, infer identity/activity/intent, adapt behavior, call providers, automate actions, or mutate the platform.
